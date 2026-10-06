"""Campus Customs PydanticAI agent, called through Portkey."""

import logging
import os
from functools import lru_cache
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext, capture_run_messages
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, ToolCallPart, UserPromptPart
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.usage import UsageLimits

from audit import record_run
from models import AgentReply, ChatMessage, ChatResponse, MAX_HISTORY_MESSAGES
from tools import PRODUCT_TOOLS, AgentDeps, load_product_cards

BACKEND_DIR = Path(__file__).resolve().parent
PROMPT_PATH = BACKEND_DIR / "prompts" / "prompt.md"

MODEL_NAME = "gpt-5.6-luna"
PORTKEY_BASE_URL = "https://api.portkey.ai/v1"

# PORTKEY_API_KEY comes from the environment: an exported variable, Homework-4/.env, or the
# AI Foundations root .env (course layout). Existing variables are never overridden.
load_dotenv(BACKEND_DIR.parent / ".env")
load_dotenv(BACKEND_DIR.parents[2] / ".env")
os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

logger = logging.getLogger("uvicorn.error")

# A guard so one chat message can't trigger a runaway loop of model calls.
USAGE_LIMITS = UsageLimits(request_limit=5)
# Safety net: search pages are 8 by default; even if the model lists more IDs, show at most this many cards.
MAX_CARDS_PER_REPLY = 12


class AgentNotConfigured(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_agent() -> Agent[AgentDeps, AgentReply]:
    """Build the agent on first use, so the rest of the API works even without a key."""
    api_key = os.environ.get("PORTKEY_API_KEY")
    if not api_key:
        raise AgentNotConfigured("PORTKEY_API_KEY is not set.")

    model = OpenAIResponsesModel(
        MODEL_NAME,
        provider=OpenAIProvider(api_key=api_key, base_url=PORTKEY_BASE_URL),
        settings={"openai_reasoning_effort": "low"},
    )
    agent = Agent(
        model,
        deps_type=AgentDeps,
        output_type=AgentReply,
        instructions=PROMPT_PATH.read_text(),
        tools=PRODUCT_TOOLS,
    )

    @agent.instructions
    def shopper_context(ctx: RunContext[AgentDeps]) -> str:
        # Only the fields the assistant needs to know who it's talking to: no id, password hash, or timestamps.
        user = ctx.deps.user
        if user is None:
            return "Customer: a guest who is not logged in. Their chat is not saved."
        return (
            "Customer: logged in.\n"
            f"- Name: {user.name}\n"
            f"- First name: {user.first_name or user.name}\n"
            f"- Email: {user.email}"
        )

    @agent.instructions
    def page_context(ctx: RunContext[AgentDeps]) -> str:
        product = ctx.deps.current_product
        if product is None:
            return "Current page: the shopper is not on a single-product page."
        return (
            "Current page: the shopper is viewing this product's page.\n"
            f"- Name: {product.name}\n"
            f"- product_id: {product.product_id}\n"
            f"- Garment type: {product.garment_type}"
        )

    return agent


def to_message_history(history: list[ChatMessage]) -> list[ModelMessage]:
    """Convert recent turns into PydanticAI messages.

    Assistant turns note which product cards were shown, so "the second one" can be resolved later.
    """
    messages: list[ModelMessage] = []
    for message in history[-MAX_HISTORY_MESSAGES:]:
        if message.role == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=message.content)]))
        else:
            content = message.content
            if message.product_ids:
                content += "\n[Product cards shown: " + ", ".join(message.product_ids) + "]"
            messages.append(ModelResponse(parts=[TextPart(content=content)]))
    return messages


TOOL_NAMES = {tool.__name__ for tool in PRODUCT_TOOLS}


async def run_chat(message: str, history: list[ChatMessage], deps: AgentDeps) -> ChatResponse:
    """Run the agent loop for one chat message and append its steps to the audit trail."""
    model_history = to_message_history(history)
    audit = dict(
        run_id=uuid4().hex[:12],
        tool_names=TOOL_NAMES,
        model=MODEL_NAME,
        logged_in=deps.user is not None,
        page_product_id=deps.current_product.product_id if deps.current_product else None,
    )
    try:
        agent = get_agent()
    except AgentNotConfigured:
        record_run([], stop_reason="not_configured", **audit)
        raise

    with capture_run_messages() as messages:
        try:
            result = await agent.run(
                message,
                deps=deps,
                message_history=model_history,
                usage_limits=USAGE_LIMITS,
            )
        except UsageLimitExceeded:
            record_run(messages[len(model_history):], stop_reason="request_limit_reached", **audit)
            raise
        except Exception as error:
            record_run(messages[len(model_history):], stop_reason=f"error:{type(error).__name__}", **audit)
            raise
    new_messages = result.new_messages()
    record_run(new_messages, stop_reason="final_output", **audit)

    tool_calls = [
        f"{part.tool_name}({part.args_as_json_str()})"
        for msg in new_messages
        if isinstance(msg, ModelResponse)
        for part in msg.parts
        if isinstance(part, ToolCallPart) and part.tool_name in TOOL_NAMES
    ]
    logger.info("Chat tool calls: %s", ", ".join(tool_calls) or "none")
    output = result.output
    return ChatResponse(
        reply=output.reply,
        products=load_product_cards(deps.db_path, output.product_ids[:MAX_CARDS_PER_REPLY]),
        suggestions=[s.strip() for s in output.suggestions if s.strip()][:4],
    )
