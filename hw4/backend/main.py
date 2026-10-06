"""Campus Customs backend: product catalogue, inventory, product images, user accounts, and chat.

Run from the backend/ folder:
    uvicorn main:app --reload --port 8000
"""

import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import sqlite3
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from agent import AgentNotConfigured, run_chat
from models import (
    MAX_HISTORY_MESSAGES,
    ChatHistoryResponse,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    HistoryMessage,
    UserContext,
)
from tools import AgentDeps, load_current_product, load_product_cards, primary_category

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
# CAMPUS_CUSTOMS_DB lets tests point at a copy of the database; the default is the provided file.
DB_PATH = Path(os.environ.get("CAMPUS_CUSTOMS_DB", DATA_DIR / "campus_customs.db"))
PRODUCTS_DIR = DATA_DIR / "products"

# Same scheme as the provided users table: pbkdf2_sha256$<salt>$<hex digest>,
# PBKDF2-HMAC-SHA256 over the UTF-8 password and UTF-8 salt string, 120,000 iterations.
PBKDF2_ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 120_000

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_NAME_LENGTH = 50
MAX_EMAIL_LENGTH = 254
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

logger = logging.getLogger("campus_customs")

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]

app = FastAPI(title="Campus Customs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Signed, HTTP-only session cookie holding the logged-in user's id. Set SESSION_SECRET to keep
# sessions valid across restarts; otherwise a random key is used and users log in again after a restart.
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET") or secrets.token_hex(32),
    session_cookie="campus_customs_session",
    max_age=7 * 24 * 60 * 60,
    same_site="lax",
)

# image_file_path values look like "products/<product_id>.jpg", so they map to /media/<image_file_path>.
app.mount("/media/products", StaticFiles(directory=PRODUCTS_DIR), name="product-images")


def get_connection(read_only: bool = True) -> sqlite3.Connection:
    # Product routes open the database read-only; only account creation writes to it.
    mode = "ro" if read_only else "rw"
    conn = sqlite3.connect(f"{DB_PATH.as_uri()}?mode={mode}", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def size_rank(size: str) -> int:
    return SIZE_ORDER.index(size) if size in SIZE_ORDER else len(SIZE_ORDER)


def product_from_row(row: sqlite3.Row, inventory: list[dict]) -> dict:
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "category": primary_category(row["garment_type"]),
        "description": row["description"],
        "colors": json.loads(row["colors"]),
        "search_tags": json.loads(row["search_tags"]),
        "image_file_path": row["image_file_path"],
        "image_url": f"/media/{row['image_file_path']}",
        "price": row["price"],
        "inventory": inventory,
        "total_stock": sum(item["quantity"] for item in inventory),
    }


def load_inventory(conn: sqlite3.Connection) -> dict[str, list[dict]]:
    by_product: dict[str, list[dict]] = {}
    for row in conn.execute("SELECT product_id, size, quantity FROM inventory"):
        by_product.setdefault(row["product_id"], []).append(
            {"size": row["size"], "quantity": row["quantity"]}
        )
    for items in by_product.values():
        items.sort(key=lambda item: size_rank(item["size"]))
    return by_product


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/products")
def list_products() -> list[dict]:
    with closing(get_connection()) as conn:
        inventory = load_inventory(conn)
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
    return [product_from_row(row, inventory.get(row["product_id"], [])) for row in rows]


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict:
    with closing(get_connection()) as conn:
        row = conn.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        inventory = load_inventory(conn).get(product_id, [])
    return product_from_row(row, inventory)


# ---------- Authentication ----------


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str


class LoginRequest(BaseModel):
    email: str
    password: str


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS
    ).hex()
    return f"{PBKDF2_ALGORITHM}${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, salt, _ = stored_hash.split("$")
    except ValueError:
        return False
    if algorithm != PBKDF2_ALGORITHM:
        return False
    return hmac.compare_digest(hash_password(password, salt), stored_hash)


def public_user(row: sqlite3.Row) -> dict:
    # Never include password_hash in responses.
    return {
        "id": row["id"],
        "name": row["name"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "email": row["email"],
        "created_at": row["created_at"],
    }


def normalize_email(email: str) -> str:
    return email.strip().lower()


def find_user_by_email(conn: sqlite3.Connection, email: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM users WHERE lower(email) = ?", (email,)).fetchone()


def validate_registration(body: RegisterRequest) -> tuple[str, str, str]:
    first_name = body.first_name.strip()
    last_name = body.last_name.strip()
    email = normalize_email(body.email)
    if not first_name or not last_name:
        raise HTTPException(status_code=400, detail="Please enter your first and last name.")
    if len(first_name) > MAX_NAME_LENGTH or len(last_name) > MAX_NAME_LENGTH:
        raise HTTPException(
            status_code=400, detail=f"Names must be {MAX_NAME_LENGTH} characters or fewer."
        )
    if len(email) > MAX_EMAIL_LENGTH or not EMAIL_PATTERN.match(email):
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")
    if not MIN_PASSWORD_LENGTH <= len(body.password) <= MAX_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Password must be {MIN_PASSWORD_LENGTH}–{MAX_PASSWORD_LENGTH} characters.",
        )
    if body.password != body.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")
    return first_name, last_name, email


@app.post("/api/auth/register", status_code=201)
def register(body: RegisterRequest, request: Request) -> dict:
    first_name, last_name, email = validate_registration(body)
    with closing(get_connection(read_only=False)) as conn:
        if find_user_by_email(conn, email) is not None:
            raise HTTPException(
                status_code=409, detail="An account with this email already exists."
            )
        try:
            with conn:
                cursor = conn.execute(
                    "INSERT INTO users (name, email, password_hash, first_name, last_name) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (f"{first_name} {last_name}", email, hash_password(body.password), first_name, last_name),
                )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=409, detail="An account with this email already exists."
            )
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    request.session["user_id"] = row["id"]
    return {"user": public_user(row)}


@app.post("/api/auth/login")
def login(body: LoginRequest, request: Request) -> dict:
    email = normalize_email(body.email)
    if not email or not body.password:
        raise HTTPException(status_code=400, detail="Please enter your email and password.")
    with closing(get_connection()) as conn:
        row = find_user_by_email(conn, email)
    # Same message for unknown email and wrong password, so the form doesn't reveal which accounts exist.
    if row is None or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    request.session["user_id"] = row["id"]
    return {"user": public_user(row)}


@app.post("/api/auth/logout")
def logout(request: Request) -> dict:
    request.session.clear()
    return {"ok": True}


@app.get("/api/auth/me")
def me(request: Request) -> dict:
    user_id = request.session.get("user_id")
    if user_id is None:
        return {"user": None}
    with closing(get_connection()) as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        request.session.clear()
        return {"user": None}
    return {"user": public_user(row)}


# ---------- Chat ----------


def current_user_context(request: Request) -> UserContext | None:
    user_id = request.session.get("user_id")
    if user_id is None:
        return None
    with closing(get_connection()) as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        return None
    return UserContext(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        name=row["name"],
        email=row["email"],
    )


# ---------- Chat history (chat_messages) ----------
#
# Follows the provided rows: one "user" row per message (products_json NULL) and one "assistant"
# row per reply (products_json = JSON list of the product objects shown, "[]" when none).

MAX_HISTORY_ROWS = 200


def stored_product_ids(products_json: str | None) -> list[str]:
    try:
        items = json.loads(products_json) if products_json else []
    except json.JSONDecodeError:
        return []
    return [item["product_id"] for item in items if isinstance(item, dict) and "product_id" in item]


def load_user_history(user_id: int, limit: int) -> list[sqlite3.Row]:
    """The most recent saved rows for this user only, oldest first."""
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT id, role, content, products_json, created_at FROM chat_messages "
            "WHERE user_id = ? AND role IN ('user', 'assistant') ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return list(reversed(rows))


def save_chat_turn(user_id: int, message: str, response: ChatResponse) -> None:
    products_json = json.dumps([card.model_dump() for card in response.products])
    with closing(get_connection(read_only=False)) as conn, conn:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'user', ?, NULL)",
            (user_id, message),
        )
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)",
            (user_id, response.reply, products_json),
        )


@app.get("/api/chat/history")
def chat_history(request: Request) -> ChatHistoryResponse:
    """Saved conversation for the logged-in shopper; guests get an empty list."""
    user_id = request.session.get("user_id")
    if user_id is None:
        return ChatHistoryResponse()
    messages = []
    for row in load_user_history(user_id, MAX_HISTORY_ROWS):
        # Cards are rebuilt from the catalogue so names, prices, and images are current.
        products = load_product_cards(DB_PATH, stored_product_ids(row["products_json"]))
        messages.append(
            HistoryMessage(
                id=row["id"], role=row["role"], content=row["content"], products=products,
                created_at=row["created_at"],
            )
        )
    return ChatHistoryResponse(messages=messages)


@app.post("/api/chat")
async def chat(body: ChatRequest, request: Request) -> ChatResponse:
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Please type a message.")
    user = current_user_context(request)
    page = body.page
    deps = AgentDeps(
        db_path=DB_PATH,
        user=user,
        current_product=load_current_product(DB_PATH, page.product_id if page else None),
    )
    if user is not None:
        # Logged-in shoppers: the saved conversation is the source of truth, not the browser.
        history = [
            ChatMessage(role=row["role"], content=row["content"], product_ids=stored_product_ids(row["products_json"]))
            for row in load_user_history(user.id, MAX_HISTORY_MESSAGES)
        ]
    else:
        history = body.history
    try:
        response = await run_chat(message, history, deps)
    except AgentNotConfigured:
        logger.error("Chat unavailable: PORTKEY_API_KEY is not set.")
        raise HTTPException(status_code=503, detail="The assistant isn't configured right now.")
    except Exception:
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=502, detail="The assistant couldn't answer just now. Please try again."
        )
    if user is not None:
        # Saved only after the agent answered successfully.
        save_chat_turn(user.id, message, response)
    return response
