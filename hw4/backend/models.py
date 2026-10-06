"""Structured types for the Campus Customs chat API and agent."""

from typing import Literal

from pydantic import BaseModel, Field

MAX_MESSAGE_LENGTH = 2000
MAX_HISTORY_MESSAGES = 20


class ChatMessage(BaseModel):
    """One earlier turn of the conversation, as shown in the chat widget."""

    role: Literal["user", "assistant"]
    content: str = Field(max_length=MAX_MESSAGE_LENGTH * 4)
    product_ids: list[str] = Field(
        default_factory=list, max_length=40, description="Products whose cards were shown with an assistant turn."
    )


class PageContext(BaseModel):
    """Where the shopper is on the site when they send a message."""

    path: str | None = Field(default=None, max_length=300)
    product_id: str | None = Field(default=None, max_length=200, description="Set on a single-product page.")


class ChatRequest(BaseModel):
    """Body of POST /api/chat.

    `history` is only used for guests; a logged-in shopper's history is read from chat_messages instead.
    """

    message: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)
    history: list[ChatMessage] = Field(default_factory=list)
    page: PageContext | None = None


class UserContext(BaseModel):
    """The logged-in shopper, loaded from the users table. Never includes the password hash.

    The agent's instructions use only name, first_name, and email (see agent.shopper_context).
    """

    id: int
    first_name: str | None
    last_name: str | None
    name: str
    email: str


class AgentReply(BaseModel):
    """Structured output the agent must return."""

    reply: str = Field(
        description="The message shown to the shopper in the chat window. Plain text; short paragraphs or '-' lists."
    )
    product_ids: list[str] = Field(
        default_factory=list,
        description=(
            "catalogue product_id values for products to show as cards under the reply. "
            "Only use IDs returned by a tool; leave empty when no specific products are discussed."
        ),
    )
    suggestions: list[str] = Field(
        default_factory=list,
        max_length=4,
        description=(
            "Up to 4 short follow-up questions the shopper could tap next, written as the shopper would type them "
            "(e.g. 'Show navy hoodies', 'Hoodies under $60', 'Show more hoodies'). Leave empty if none are useful."
        ),
    )


# ---------- Database lookup tool results ----------

LookupStatus = Literal["found", "not_found", "ambiguous"]


class ProductRef(BaseModel):
    """Identifies one catalogue product."""

    product_id: str = Field(description="catalogue.product_id; use this exact value in product_ids or follow-up tool calls.")
    name: str


class ProductLookup(BaseModel):
    """Fields every lookup result shares: whether the product query resolved to exactly one product."""

    status: LookupStatus = Field(
        description="found: exactly one product matched. ambiguous: several matched; see candidates. not_found: none matched; see candidates for close names."
    )
    query: str = Field(description="The product text the tool was called with.")
    product: ProductRef | None = Field(default=None, description="The matched product when status is found.")
    candidates: list[ProductRef] = Field(
        default_factory=list,
        description="Possible matches to offer the shopper when status is ambiguous or not_found.",
    )


class ProductDescriptionResult(ProductLookup):
    """Result of get_product_description."""

    garment_type: str | None = None
    description: str | None = None
    colors: list[str] = Field(default_factory=list)


class ProductPriceResult(ProductLookup):
    """Result of get_product_price."""

    price: float | None = Field(default=None, description="Price in US dollars from catalogue.price.")
    currency: Literal["USD"] = "USD"


class SizeStock(BaseModel):
    """Stock of one size from the inventory table."""

    size: str
    quantity: int
    in_stock: bool


class StockResult(ProductLookup):
    """Result of get_stock_by_size."""

    requested_size: str | None = Field(
        default=None, description="The requested size normalized to XS, S, M, L, XL, or XXL; null if none was asked."
    )
    requested_size_valid: bool | None = Field(
        default=None, description="False when the requested size isn't one the shop carries; null if no size was asked."
    )
    requested_size_quantity: int | None = Field(
        default=None, description="Units in stock for the requested size; 0 means sold out in that size."
    )
    requested_size_in_stock: bool | None = Field(
        default=None, description="True if the requested size has at least one unit; false if sold out or invalid."
    )
    sizes: list[SizeStock] = Field(default_factory=list, description="Every size for this product, XS to XXL.")
    available_sizes: list[str] = Field(default_factory=list, description="Sizes with quantity > 0.")
    total_stock: int | None = None


ProductCategory = Literal["hoodie", "crewneck", "t-shirt", "quarter-zip", "jacket", "long-sleeve", "sweatshirt"]


class ProductMatch(BaseModel):
    """One product returned by search_catalogue, with the facts needed to describe it briefly."""

    product_id: str = Field(description="Exact catalogue.product_id; copy it into product_ids to show this product's card.")
    name: str
    garment_type: str
    price: float = Field(description="Price in US dollars from catalogue.price.")
    colors: list[str] = Field(description="Garment color first, then print/logo colors.")
    short_description: str = Field(description="First sentence of catalogue.description.")
    total_stock: int
    available_sizes: list[str] = Field(description="Sizes with quantity > 0, XS to XXL.")


SearchSort = Literal["relevance", "price_low", "price_high", "name"]


class FacetCount(BaseModel):
    """How many of the matching products share one value (used to suggest ways to narrow down)."""

    value: str
    count: int


class PriceBand(BaseModel):
    label: str = Field(description="e.g. 'Under $50'")
    min_price: float | None
    max_price: float | None
    count: int


class NarrowingOptions(BaseModel):
    """Computed over ALL matches (not just this page), so the agent can offer real ways to narrow a big result."""

    categories: list[FacetCount] = Field(description="Categories among the matches, most common first.")
    main_colors: list[FacetCount] = Field(
        description="Most common main-color families among the matches (top 6); each value works as the color filter."
    )
    price_bands: list[PriceBand] = Field(description="Non-empty price bands among the matches.")
    price_min: float | None = Field(description="Lowest price across ALL total_matches (the full matching set), not just this page.")
    price_max: float | None = Field(description="Highest price across ALL total_matches (the full matching set), not just this page.")


class CatalogueSearchResult(BaseModel):
    """Result of search_catalogue: one page of ranked matches plus ways to narrow the rest."""

    category: ProductCategory | None = Field(description="Category filter that was applied, if any.")
    keywords: str | None = Field(description="Keyword filter that was applied, if any.")
    color: str | None = Field(description="Color filter that was applied, if any.")
    size: str | None = Field(default=None, description="Size filter (normalized) that was applied, if any.")
    min_price: float | None = None
    max_price: float | None = None
    sort: SearchSort = "relevance"
    keyword_match: Literal["all", "some", "none"] = Field(
        default="none",
        description="all: every keyword matched. some: no product matched every keyword, so products matching "
        "some of them are returned (tell the shopper). none: no keywords were given.",
    )
    total_matches: int = Field(description="How many catalogue products matched all filters.")
    offset: int = Field(default=0, description="Index of the first match on this page.")
    matches: list[ProductMatch] = Field(description="This page of matches, best first (see sort).")
    truncated: bool = Field(description="True when more matches exist beyond this page.")
    next_offset: int | None = Field(default=None, description="Pass as offset to get the next page; null on the last page.")
    narrowing: NarrowingOptions | None = Field(default=None, description="Ways to narrow the full result set.")


class StoreInfo(BaseModel):
    """Result of get_store_info: the store facts the project has verified."""

    store_name: str
    online_store: str
    address: str
    hours: str
    hours_note: str
    phone: str
    email: str
    founded: int
    about: str


class ProductCard(BaseModel):
    """A product shown under an assistant reply. Built from the database, never from model text.

    Carries the same fields the Products page cards use, so the frontend renders it with the same component.
    """

    product_id: str
    name: str
    garment_type: str
    description: str
    price: float
    image_url: str
    total_stock: int


class CurrentProduct(BaseModel):
    """The product on the page the shopper is viewing, verified against the catalogue."""

    product_id: str
    name: str
    garment_type: str


class ChatResponse(BaseModel):
    """Response of POST /api/chat."""

    reply: str
    products: list[ProductCard] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list, description="Follow-up questions shown as clickable chips.")


class HistoryMessage(BaseModel):
    """One saved chat_messages row, as returned to the chat widget."""

    id: int
    role: Literal["user", "assistant"]
    content: str
    products: list[ProductCard] = Field(default_factory=list)
    created_at: str


class ChatHistoryResponse(BaseModel):
    """Response of GET /api/chat/history."""

    messages: list[HistoryMessage] = Field(default_factory=list)


# ---------- Audit trail ----------

AuditEvent = Literal["tool_call", "tool_retry", "final_output", "run_error"]


class AuditEntry(BaseModel):
    """One step of an agent run, appended to output/audit_trail.json (see audit.py).

    Holds only short, redacted tool arguments and result summaries: never the shopper's name, email,
    message text, the reply text, or anything password-related.
    """

    time: str = Field(description="UTC ISO-8601 time of the step.")
    run_id: str = Field(description="Groups the entries of one agent run (one chat message).")
    step: int = Field(description="Order of the entry within its run, starting at 1.")
    event: AuditEvent
    tool: str | None = Field(default=None, description="Tool name; 'final_result' for the structured answer.")
    arguments: dict | None = Field(default=None, description="Tool arguments, redacted and truncated.")
    result: str | None = Field(default=None, description="Short summary of the tool result or final answer.")
    stop_reason: str = Field(
        description="Why the run stopped: final_output, request_limit_reached, not_configured, or error:<Type>."
    )
    model_finish_reason: str | None = Field(default=None, description="Finish reason of the run's last model response.")
    model_requests: int = Field(description="Model requests made in this run (capped by the request limit).")
    model: str
    logged_in: bool = Field(description="Whether the shopper was logged in (no identity is stored).")
    page_product_id: str | None = Field(default=None, description="Product page the shopper was on, if any.")
