"""Append-only audit trail of agent-loop activity (output/audit_trail.json).

run_chat (agent.py) captures every message of a run with PydanticAI's capture_run_messages and
calls record_run when the run ends, whether it succeeded or failed. Each tool call, retry, and the
final structured answer becomes one AuditEntry. Entries are appended: existing entries are always
read back and kept, and the file is replaced atomically so a crash can't leave it half-written.
"""

import fcntl
import json
import logging
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, RetryPromptPart, ToolCallPart, ToolReturnPart

from models import AuditEntry

DEFAULT_AUDIT_PATH = Path(__file__).resolve().parents[1] / "output" / "audit_trail.json"
MAX_TEXT = 120
MAX_LIST_ITEMS = 10

logger = logging.getLogger("uvicorn.error")
_write_lock = threading.Lock()

SENSITIVE_WORDS = re.compile(r"pass(word|wd)?|pbkdf2|hash|secret|token|api[_-]?key|credit|card number|ssn", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
LONG_NUMBER = re.compile(r"\d[\d -]{7,}\d")


def audit_path() -> Path:
    # AUDIT_TRAIL_PATH lets tests write somewhere else; the default is output/audit_trail.json.
    return Path(os.environ.get("AUDIT_TRAIL_PATH", DEFAULT_AUDIT_PATH))


# ---------- Making arguments and results safe to store ----------


def safe_text(text: str) -> str:
    if SENSITIVE_WORDS.search(text):
        return "[redacted]"
    text = EMAIL.sub("[email]", text)
    text = LONG_NUMBER.sub("[number]", text)
    return text if len(text) <= MAX_TEXT else text[: MAX_TEXT - 1] + "…"


def safe_value(value: Any) -> Any:
    if isinstance(value, str):
        return safe_text(value)
    if isinstance(value, dict):
        return {
            key: "[redacted]" if SENSITIVE_WORDS.search(str(key)) else safe_value(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        items = [safe_value(item) for item in value[:MAX_LIST_ITEMS]]
        return items + ([f"… +{len(value) - MAX_LIST_ITEMS} more"] if len(value) > MAX_LIST_ITEMS else [])
    return value


def summarize_result(tool: str, content: Any) -> str:
    """A one-line summary of a tool result, keeping the facts that matter for an audit."""
    data = content.model_dump() if hasattr(content, "model_dump") else content
    if not isinstance(data, dict):
        return safe_text(str(data))
    if tool == "search_catalogue":
        ids = [m["product_id"] for m in data.get("matches", [])]
        return safe_text(
            f"total_matches={data.get('total_matches')} returned={len(ids)} truncated={data.get('truncated')} "
            f"keyword_match={data.get('keyword_match')} ids={','.join(ids)}"
        )
    if tool == "get_store_info":
        return "store facts returned (address, hours, phone, email, online store)"
    product = (data.get("product") or {}).get("product_id")
    parts = [f"status={data.get('status')}", f"product={product}"]
    if tool == "get_product_price":
        parts.append(f"price={data.get('price')}")
    elif tool == "get_stock_by_size":
        parts += [
            f"requested_size={data.get('requested_size')}",
            f"requested_qty={data.get('requested_size_quantity')}",
            f"available={','.join(data.get('available_sizes') or [])}",
            f"total_stock={data.get('total_stock')}",
        ]
    elif tool == "get_product_description":
        parts.append(f"description_chars={len(data.get('description') or '')}")
    if data.get("candidates"):
        parts.append(f"candidates={len(data['candidates'])}")
    return safe_text(" ".join(parts))


def summarize_final(args: dict) -> str:
    # The reply text is not stored: it can contain the shopper's own name or email.
    product_ids = args.get("product_ids") or []
    return safe_text(
        f"reply_chars={len(args.get('reply') or '')} cards={len(product_ids)} "
        f"suggestions={len(args.get('suggestions') or [])} ids={','.join(product_ids)}"
    )


# ---------- Turning a run's messages into entries ----------


def build_entries(
    messages: list[ModelMessage],
    *,
    run_id: str,
    stop_reason: str,
    tool_names: set[str],
    model: str,
    logged_in: bool,
    page_product_id: str | None,
) -> list[AuditEntry]:
    responses = [m for m in messages if isinstance(m, ModelResponse)]
    returns: dict[str, ToolReturnPart] = {}
    retries: list[RetryPromptPart] = []
    for message in messages:
        if isinstance(message, ModelRequest):
            for part in message.parts:
                if isinstance(part, ToolReturnPart):
                    returns[part.tool_call_id] = part
                elif isinstance(part, RetryPromptPart):
                    retries.append(part)

    common = dict(
        run_id=run_id,
        stop_reason=stop_reason,
        model_finish_reason=responses[-1].finish_reason if responses else None,
        model_requests=len(responses),
        model=model,
        logged_in=logged_in,
        page_product_id=page_product_id,
    )
    rows: list[dict] = []
    for response in responses:
        for part in response.parts:
            if not isinstance(part, ToolCallPart):
                continue
            args = part.args_as_dict()
            if part.tool_name in tool_names:
                returned = returns.get(part.tool_call_id)
                rows.append(dict(
                    time=response.timestamp, event="tool_call", tool=part.tool_name, arguments=safe_value(args),
                    result=summarize_result(part.tool_name, returned.content) if returned else "no result (run stopped)",
                ))
            else:
                rows.append(dict(time=response.timestamp, event="final_output", tool=part.tool_name,
                                 arguments=None, result=summarize_final(args)))
    for retry in retries:
        rows.append(dict(time=retry.timestamp, event="tool_retry", tool=retry.tool_name, arguments=None,
                         result=safe_text(str(retry.content))))
    if not rows or stop_reason != "final_output":
        rows.append(dict(time=datetime.now(timezone.utc), event="run_error", tool=None, arguments=None,
                         result=f"run stopped: {stop_reason}"))

    rows.sort(key=lambda row: row["time"])
    return [
        AuditEntry(step=index, time=row.pop("time").astimezone(timezone.utc).isoformat(timespec="seconds"), **row, **common)
        for index, row in enumerate(rows, start=1)
    ]


# ---------- Appending to the file ----------


def append_entries(entries: list[AuditEntry]) -> None:
    """Append entries to the audit file, keeping every existing entry."""
    if not entries:
        return
    path = audit_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(path.name + ".lock")
    with _write_lock, open(lock_path, "w") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)  # also guards against other processes
        existing: list = []
        if path.exists() and path.stat().st_size > 0:
            try:
                existing = json.loads(path.read_text())
                if not isinstance(existing, list):
                    raise ValueError("audit trail is not a JSON list")
            except ValueError:
                # Never discard unreadable history: keep it beside the new file.
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                path.rename(path.with_name(f"{path.stem}.unreadable-{stamp}{path.suffix}"))
                existing = []
        updated = existing + [entry.model_dump(mode="json") for entry in entries]
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n")
        os.replace(tmp, path)  # atomic: readers see the old or the new file, never a partial one


def record_run(messages: list[ModelMessage], **kwargs: Any) -> None:
    """Build and append the entries for one run. Audit problems never break the chat."""
    try:
        append_entries(build_entries(messages, **kwargs))
    except Exception:
        logger.exception("Could not write the audit trail")
