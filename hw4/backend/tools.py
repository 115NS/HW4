"""Dependencies, database helpers, and tools for the Campus Customs agent."""

import difflib
import json
import re
import sqlite3
from contextlib import closing
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from pydantic_ai import RunContext

from models import (
    CatalogueSearchResult,
    CurrentProduct,
    FacetCount,
    NarrowingOptions,
    PriceBand,
    SearchSort,
    StoreInfo,
    LookupStatus,
    ProductCard,
    ProductCategory,
    ProductDescriptionResult,
    ProductMatch,
    ProductPriceResult,
    ProductRef,
    SizeStock,
    StockResult,
    UserContext,
)

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]
MAX_CANDIDATES = 8


@dataclass
class AgentDeps:
    """Per-request context passed to the agent and its tools."""

    db_path: Path
    user: UserContext | None = None
    current_product: CurrentProduct | None = None


def connect_read_only(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"{db_path.as_uri()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def load_current_product(db_path: Path, product_id: str | None) -> CurrentProduct | None:
    """Look up the product on the shopper's current page; unknown IDs give None."""
    if not product_id:
        return None
    with closing(connect_read_only(db_path)) as conn:
        row = conn.execute(
            "SELECT product_id, name, garment_type FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
    return CurrentProduct(**dict(row)) if row else None


# ---------- Resolving a shopper's product text to one catalogue row ----------

# Catalogue names are built from slugs ("Football Left Chest T Shirt", "Morse 1 4 Zip"),
# so shopper wording is rewritten into the same form before matching.
PHRASE_SYNONYMS = [
    (r"\bt-?shirts?\b|\btees?\b|\btshirts?\b", "t shirt"),
    (r"\b1/4[ -]?zip\b|\bquarter[ -]?zips?\b", "1 4 zip"),
    (r"\bcrew[ -]?necks?\b", "crewneck"),
    (r"\bhoodies\b|\bhoody\b", "hoodie"),
    (r"\bvs\.?\b|\bversus\b", "vs"),
    (r"\bgrey\b", "gray"),
]
STOPWORDS = {"the", "a", "an", "your", "you", "of", "in", "for", "my", "that", "this", "one"}


def normalize_text(text: str) -> str:
    text = text.lower().replace("&", " and ")
    for pattern, replacement in PHRASE_SYNONYMS:
        text = re.sub(pattern, replacement, text)
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


def query_tokens(text: str) -> list[str]:
    return [token for token in normalize_text(text).split() if token not in STOPWORDS]


def token_in_name(token: str, name_tokens: set[str]) -> bool:
    # Accept simple plurals ("crewnecks" -> "crewneck").
    return token in name_tokens or (token.endswith("s") and token[:-1] in name_tokens)


def resolve_product(conn: sqlite3.Connection, query: str) -> tuple[LookupStatus, sqlite3.Row | None, list[ProductRef]]:
    """Return ("found", row, []), ("ambiguous", None, matches), or ("not_found", None, close names)."""
    rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
    normalized = normalize_text(query)
    slug = normalized.replace(" ", "-")

    for row in rows:
        if query.strip() == row["product_id"] or slug == row["product_id"] or normalized == normalize_text(row["name"]):
            return "found", row, []

    tokens = query_tokens(query)
    if tokens:
        matches = [
            row for row in rows
            if all(token_in_name(token, set(normalize_text(row["name"]).split())) for token in tokens)
        ]
        if len(matches) == 1:
            return "found", matches[0], []
        if matches:
            return "ambiguous", None, [ProductRef(product_id=r["product_id"], name=r["name"]) for r in matches[:MAX_CANDIDATES]]

    names = {normalize_text(row["name"]): row for row in rows}
    close = difflib.get_close_matches(normalized, list(names), n=5, cutoff=0.6)
    return "not_found", None, [ProductRef(product_id=names[n]["product_id"], name=names[n]["name"]) for n in close]


SIZE_ALIASES = {
    "xs": "XS", "extra small": "XS", "x small": "XS", "xsmall": "XS",
    "s": "S", "small": "S", "sm": "S",
    "m": "M", "medium": "M", "med": "M",
    "l": "L", "large": "L", "lg": "L",
    "xl": "XL", "extra large": "XL", "x large": "XL", "xlarge": "XL",
    "xxl": "XXL", "2xl": "XXL", "xx large": "XXL", "double extra large": "XXL", "2x": "XXL",
}


def normalize_size(size: str) -> str | None:
    return SIZE_ALIASES.get(" ".join(re.sub(r"[^a-z0-9]+", " ", size.lower()).split()))


# ---------- Agent tools ----------


def get_product_description(ctx: RunContext[AgentDeps], product: str) -> ProductDescriptionResult:
    """Look up a product's description, garment type, and colors in the catalogue.

    Use for questions about what a product looks like, its design, material details, or colors.

    Args:
        product: The product name as the shopper wrote it (e.g. "Davenport College crewneck"), or an exact product_id.
    """
    with closing(connect_read_only(ctx.deps.db_path)) as conn:
        status, row, candidates = resolve_product(conn, product)
    if row is None:
        return ProductDescriptionResult(status=status, query=product, candidates=candidates)
    return ProductDescriptionResult(
        status="found",
        query=product,
        product=ProductRef(product_id=row["product_id"], name=row["name"]),
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
    )


def get_product_price(ctx: RunContext[AgentDeps], product: str) -> ProductPriceResult:
    """Look up a product's price in US dollars from the catalogue.

    Use whenever the shopper asks what something costs. Never state a price without this tool.

    Args:
        product: The product name as the shopper wrote it (e.g. "Basic Hoodie Big Yale"), or an exact product_id.
    """
    with closing(connect_read_only(ctx.deps.db_path)) as conn:
        status, row, candidates = resolve_product(conn, product)
    if row is None:
        return ProductPriceResult(status=status, query=product, candidates=candidates)
    return ProductPriceResult(
        status="found",
        query=product,
        product=ProductRef(product_id=row["product_id"], name=row["name"]),
        price=row["price"],
    )


def get_stock_by_size(ctx: RunContext[AgentDeps], product: str, size: str | None = None) -> StockResult:
    """Look up how many units of a product are in stock in each size (XS, S, M, L, XL, XXL).

    Use for any question about availability, sizes, or whether something is in stock or sold out.
    Never state stock or availability without this tool.

    Args:
        product: The product name as the shopper wrote it, or an exact product_id.
        size: Optional size the shopper asked about, e.g. "M", "medium", "XL". Leave empty to get every size.
    """
    with closing(connect_read_only(ctx.deps.db_path)) as conn:
        status, row, candidates = resolve_product(conn, product)
        if row is None:
            return StockResult(status=status, query=product, candidates=candidates)
        inventory = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (row["product_id"],)
        ).fetchall()

    sizes = sorted(
        (SizeStock(size=r["size"], quantity=r["quantity"], in_stock=r["quantity"] > 0) for r in inventory),
        key=lambda item: SIZE_ORDER.index(item.size) if item.size in SIZE_ORDER else len(SIZE_ORDER),
    )
    result = StockResult(
        status="found",
        query=product,
        product=ProductRef(product_id=row["product_id"], name=row["name"]),
        sizes=sizes,
        available_sizes=[item.size for item in sizes if item.in_stock],
        total_stock=sum(item.quantity for item in sizes),
    )
    if size:
        normalized = normalize_size(size)
        by_size = {item.size: item for item in sizes}
        result.requested_size = normalized or size
        result.requested_size_valid = normalized in by_size
        result.requested_size_quantity = by_size[normalized].quantity if normalized in by_size else None
        result.requested_size_in_stock = bool(normalized in by_size and by_size[normalized].in_stock)
    return result


# Shopper-facing categories mapped onto the 22 free-text garment_type values in the catalogue.
CATEGORY_RULES: dict[str, Callable[[str], bool]] = {
    "hoodie": lambda gt: "hood" in gt,
    "crewneck": lambda gt: "crewneck" in gt and "t-shirt" not in gt,
    "t-shirt": lambda gt: "t-shirt" in gt,
    "quarter-zip": lambda gt: "quarter-zip" in gt,
    "jacket": lambda gt: "jacket" in gt,
    "long-sleeve": lambda gt: "long-sleeve" in gt and "shirt" in gt,
    "sweatshirt": lambda gt: "sweatshirt" in gt or "hood" in gt or gt == "crewneck",
}


def first_sentence(text: str, max_length: int = 140) -> str:
    sentence = re.split(r"(?<=\.)\s", text.strip(), maxsplit=1)[0]
    return sentence if len(sentence) <= max_length else sentence[: max_length - 1].rstrip() + "…"


def primary_category(garment_type: str) -> str:
    """The single most specific category for a garment_type (used by the Products page filter)."""
    gt = garment_type.lower()
    for category in ["hoodie", "crewneck", "t-shirt", "quarter-zip", "jacket", "long-sleeve"]:
        if CATEGORY_RULES[category](gt):
            return category
    return "sweatshirt"


# Main garment colors in the catalogue vary in wording ("navy" / "navy blue", "heather gray" /
# "charcoal gray" / "dark heather charcoal"), so they are grouped into families for filtering and counts.
COLOR_FAMILIES = [
    ("navy", ("navy",)),
    ("gray", ("gray", "charcoal")),
    ("cream", ("cream", "ivory")),
    ("white", ("white",)),
    ("coral", ("coral",)),
]


def color_family(color: str) -> str:
    text = normalize_text(color)
    for family, words in COLOR_FAMILIES:
        if any(word in text for word in words):
            return family
    return text


DEFAULT_PAGE_SIZE = 8
MAX_PAGE_SIZE = 20
PRICE_BANDS = [("Under $50", None, 50.0), ("$50–$75", 50.0, 75.0), ("$75 and up", 75.0, None)]


def keyword_score(tokens: list[str], row: sqlite3.Row, tags: list[str], colors: list[str]) -> tuple[int, int]:
    """(number of keywords matched, weighted score): name matches count most, then tags, then the rest."""
    name_words = set(normalize_text(row["name"]).split())
    tag_words = set(normalize_text(" ".join(tags)).split())
    other_words = set(normalize_text(" ".join([row["garment_type"], row["description"], *colors])).split())
    matched, score = 0, 0
    for token in tokens:
        if token_in_name(token, name_words):
            matched, score = matched + 1, score + 3
        elif token_in_name(token, tag_words):
            matched, score = matched + 1, score + 2
        elif token_in_name(token, other_words):
            matched, score = matched + 1, score + 1
    return matched, score


def build_narrowing(matches: list[ProductMatch]) -> NarrowingOptions:
    categories = Counter(primary_category(m.garment_type) for m in matches)
    colors = Counter(color_family(m.colors[0]) for m in matches if m.colors)
    bands = []
    for label, low, high in PRICE_BANDS:
        count = sum(1 for m in matches if (low is None or m.price >= low) and (high is None or m.price < high))
        if count:
            bands.append(PriceBand(label=label, min_price=low, max_price=high, count=count))
    prices = [m.price for m in matches]
    return NarrowingOptions(
        categories=[FacetCount(value=v, count=c) for v, c in categories.most_common()],
        main_colors=[FacetCount(value=v, count=c) for v, c in colors.most_common(6)],
        price_bands=bands,
        price_min=min(prices) if prices else None,
        price_max=max(prices) if prices else None,
    )


def search_catalogue(
    ctx: RunContext[AgentDeps],
    category: ProductCategory | None = None,
    keywords: str | None = None,
    color: str | None = None,
    size: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: SearchSort = "relevance",
    limit: int = DEFAULT_PAGE_SIZE,
    offset: int = 0,
) -> CatalogueSearchResult:
    """Search the catalogue and return one page of the best matches plus ways to narrow the rest.

    Use when the shopper asks what products of a type or theme you carry, e.g. "What hoodies do you have?",
    "Do you have anything for Davenport?", "Show me navy crewnecks", "hoodies under $60 in medium",
    "What do you have in stock?" (no filters). Every filter given must match. Results come from the database.

    Args:
        category: Garment category, if the shopper named one. "sweatshirt" covers hoodies, crewnecks,
            quarter-zip sweatshirts, and the mockneck.
        keywords: Other words to match in the product name, description, or tags, such as a residential
            college, school, sport, team, family member, brand, or design (e.g. "Davenport", "baseball", "mom",
            "Champion", "bulldog"). Leave out words already covered by category or color.
        color: The garment's main color, e.g. "navy", "gray", "white" (logo/print colors don't count).
        size: Only products with this size in stock, e.g. "M", "medium", "XL".
        min_price: Lowest price in US dollars.
        max_price: Highest price in US dollars.
        sort: "relevance" (default: best keyword matches first, then most sizes in stock), "price_low",
            "price_high", or "name".
        limit: Matches per page (default 8, max 20). Keep the default so the shopper isn't overwhelmed.
        offset: Start of the page; use next_offset from the previous result to show more.
    """
    tokens = query_tokens(keywords) if keywords else []
    wanted_color = normalize_text(color) if color else ""
    wanted_size = normalize_size(size) if size else None
    with closing(connect_read_only(ctx.deps.db_path)) as conn:
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        inventory = conn.execute("SELECT product_id, size, quantity FROM inventory").fetchall()

    stock: dict[str, dict[str, int]] = {}
    for item in inventory:
        stock.setdefault(item["product_id"], {})[item["size"]] = item["quantity"]

    # (keywords matched, keyword score, product)
    candidates: list[tuple[int, int, ProductMatch]] = []
    for row in rows:
        colors = json.loads(row["colors"])
        sizes = stock.get(row["product_id"], {})
        if category and not CATEGORY_RULES[category](row["garment_type"].lower()):
            continue
        # colors[0] is the garment's main color; the rest are print/logo colors.
        if wanted_color and not (
            colors and (wanted_color in normalize_text(colors[0]) or color_family(colors[0]) == color_family(wanted_color))
        ):
            continue
        if size and sizes.get(wanted_size or "", 0) <= 0:
            continue
        if min_price is not None and row["price"] < min_price:
            continue
        if max_price is not None and row["price"] > max_price:
            continue
        matched, score = keyword_score(tokens, row, json.loads(row["search_tags"]), colors) if tokens else (0, 0)
        if tokens and matched == 0:
            continue
        candidates.append((matched, score, ProductMatch(
            product_id=row["product_id"],
            name=row["name"],
            garment_type=row["garment_type"],
            price=row["price"],
            colors=colors,
            short_description=first_sentence(row["description"]),
            total_stock=sum(sizes.values()),
            available_sizes=[s for s in SIZE_ORDER if sizes.get(s, 0) > 0],
        )))

    keyword_match = "none"
    if tokens:
        full = [c for c in candidates if c[0] == len(tokens)]
        # Prefer products matching every keyword; fall back to partial matches only if there are none.
        keyword_match = "all" if full else ("some" if candidates else "all")
        candidates = full or candidates

    if sort == "price_low":
        candidates.sort(key=lambda c: (c[2].price, c[2].name))
    elif sort == "price_high":
        candidates.sort(key=lambda c: (-c[2].price, c[2].name))
    elif sort == "name":
        candidates.sort(key=lambda c: c[2].name)
    else:
        candidates.sort(key=lambda c: (-c[0], -c[1], -len(c[2].available_sizes), -c[2].total_stock, c[2].name))

    matches = [c[2] for c in candidates]
    limit = max(1, min(limit, MAX_PAGE_SIZE))
    offset = max(0, offset)
    page = matches[offset: offset + limit]
    has_more = offset + limit < len(matches)
    return CatalogueSearchResult(
        category=category,
        keywords=keywords,
        color=color,
        size=wanted_size or size,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        keyword_match=keyword_match,
        total_matches=len(matches),
        offset=offset,
        matches=page,
        truncated=has_more,
        next_offset=offset + limit if has_more else None,
        narrowing=build_narrowing(matches) if matches else None,
    )


# ---------- Store information ----------

# Facts verified from yalebulldogblue.com and public listings in Problem 3 (see output/harness.md).
STORE_INFO = StoreInfo(
    store_name="Campus Customs",
    online_store="Yale Bulldog Blue (yalebulldogblue.com)",
    address="57 Broadway, New Haven, CT 06511 (across from Yale's campus)",
    hours="Open 7 days a week",
    hours_note="Exact daily opening and closing times aren't listed here; call the store to confirm today's hours.",
    phone="(203) 789-2157",
    email="team@campuscustoms.com",
    founded=1975,
    about="The oldest official Yale merchandise retailer in New Haven, selling licensed Yale apparel and gifts.",
)


def get_store_info(ctx: RunContext[AgentDeps]) -> StoreInfo:
    """Get Campus Customs store information: address, hours, phone, email, online store, and history.

    Use for any question about where the store is, when it's open, how to contact it, or its background.
    Don't use product tools for these questions.
    """
    return STORE_INFO


PRODUCT_TOOLS = [search_catalogue, get_product_description, get_product_price, get_stock_by_size, get_store_info]


# ---------- Product cards shown under replies ----------


def load_product_cards(db_path: Path, product_ids: list[str]) -> list[ProductCard]:
    """Turn product IDs chosen by the agent into cards using database values.

    Unknown IDs are dropped, so a made-up ID can never show a fake product or price.
    """
    unique_ids = list(dict.fromkeys(product_ids))
    if not unique_ids:
        return []
    placeholders = ", ".join("?" for _ in unique_ids)
    with closing(connect_read_only(db_path)) as conn:
        rows = conn.execute(
            f"""
            SELECT c.product_id, c.name, c.garment_type, c.description, c.price, c.image_file_path,
                   COALESCE(SUM(i.quantity), 0) AS total_stock
            FROM catalogue c LEFT JOIN inventory i ON i.product_id = c.product_id
            WHERE c.product_id IN ({placeholders})
            GROUP BY c.product_id
            """,
            unique_ids,
        ).fetchall()
    by_id = {
        row["product_id"]: ProductCard(
            product_id=row["product_id"],
            name=row["name"],
            garment_type=row["garment_type"],
            description=row["description"],
            price=row["price"],
            image_url=f"/media/{row['image_file_path']}",
            total_stock=row["total_stock"],
        )
        for row in rows
    }
    return [by_id[product_id] for product_id in unique_ids if product_id in by_id]
