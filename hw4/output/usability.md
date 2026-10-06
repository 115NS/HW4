# Campus Customs: Usability Improvements (Problem 9)

Four improvements were added on top of the Problem 1–8 site: two on the frontend and two in the agent/backend. Everything below was implemented and tested in the running app. Test details are in `output/harness.md` (Problem 9 section).

---

## 1. Products page search and filtering (frontend)

### What was added

A filter bar at the top of the Products page (`frontend/src/pages/ProductsPage.tsx`) with:

- **Search box**: matches every typed word against each product's name, garment type, description, search tags, and colors. For example, "davenport" finds the Davenport College Crewneck, and "bulldog hoodie" finds the 2 hoodies with bulldog designs.
- **Category dropdown**: with live counts: Hoodies (27), Crewnecks (28), T-shirts (25), Quarter-zips (11), Jackets & fleece (8), Long-sleeve shirts (2), Other sweatshirts (1). Categories come from a new `category` field on `/api/products`, computed by the backend with the same rules the chatbot's search uses. This matters because the database's `garment_type` column has 22 inconsistent spellings.
- **Price dropdown**: Under $50, $50–$75, or $75 and up.
- **Sort dropdown**: Name (A–Z), Price: low to high, Price: high to low.
- **Result count** ("Showing 27 of 102 products"), a **Clear** button, and a friendly message when nothing matches.

All filtering uses the existing `/api/products` data; there is no separate product list. Filters are kept in the URL (`?q=…&category=…&price=…&sort=…`). Opening a product and pressing Back returns to the same filtered list, and a filtered view can be shared as a link.

Product cards and single-product pages are unchanged: the same `ProductCard` component, the same links.

### Why it helps

Shoppers no longer have to scroll through 102 cards to find, say, a hoodie under $50 or something for their residential college. They can answer "what do you have for Davenport?" or "what's cheapest?" themselves in a couple of clicks. For the store, faster discovery means fewer abandoned visits, and it takes simple browsing questions off the chatbot (and off model costs).

---

## 2. Chat quick-start suggestions (frontend)

### What was added

- When the chat opens on a fresh conversation, it shows clickable suggestion chips: **"What hoodies do you have?"**, **"What do you have in stock?"**, and **"Help me find Yale gear."**
- On a single-product page, an extra first chip appears: **"What sizes of this are in stock?"**. Because the chat already sends page context (Problem 8), "this" refers to the product being viewed.
- Clicking a chip sends that question through the existing chat flow (`send()` in `ChatWidget.tsx`), exactly as if it were typed. It carries the same history and page context, and its answer can include product cards.
- After a reply, the chat shows the **agent's own follow-up suggestions** for that reply, if it gave any (see improvement 4). For example, after a hoodie search it showed "Show more hoodies", "Show navy hoodies", "Show gray hoodies", and "Hoodies under $50". The quick-starts disappear once the conversation starts.

### Why it helps

An empty chat box makes shoppers guess what the assistant can do. The chips show it at a glance (product search, stock, finding Yale gear) and get a first answer with one click, which helps on phones in particular. Follow-up chips turn "here are 27 hoodies" into an obvious next step instead of a dead end. For the business, more shoppers actually use the assistant and reach products.

---

## 3. Store information tool (agent/backend)

### What was added

- A new agent tool, `get_store_info()` in `backend/tools.py`. It returns a structured `StoreInfo` (`backend/models.py`): store name, online store (Yale Bulldog Blue, yalebulldogblue.com), address (57 Broadway, New Haven, CT 06511), hours ("Open 7 days a week"), a note that exact daily times aren't listed so shoppers should call to confirm, phone ((203) 789-2157), email (team@campuscustoms.com), founding year (1975), and a one-line description.
- These are the same facts researched in Problem 3 and already shown in the site's footer and About page. A test checks that they match. No opening times were invented, because none were verified.
- The store facts were moved out of the system prompt and into the tool. `backend/prompts/prompt.md` now has a "Store information tool" section: use `get_store_info` for location, hours, contact, or history questions; answer only from its fields; don't call product tools for these; and don't invent exact times.

**Verified with one real model call:** "What are your store hours and phone number?" made the agent call **only** `get_store_info`, and it replied: *"Campus Customs is open 7 days a week, though exact daily opening and closing times aren't listed—please call to confirm today's hours. The phone number is (203) 789-2157."*

### Why it helps

Store questions (where, when, how to contact) are some of the most common things shoppers ask. A dedicated tool keeps those answers consistent and grounded in one verified source, and it's honest about what isn't known: no made-up hours. It also avoids wasted product-search calls for non-product questions. If the store's details ever change, there is one place to update them.

---

## 4. More efficient, more useful catalogue search (agent/backend)

### What was added

`search_catalogue` (`backend/tools.py`) still searches the real catalogue for any category or theme (the Problem 7 behavior). It now returns a **ranked page** of results plus **ways to narrow** them:

- **Pages instead of everything at once.** Results come back 8 at a time (`limit`, max 20), with `total_matches`, `truncated`, and `next_offset`. Nothing is removed: paging through returns every match (tested: all 27 hoodies, exactly the database set). "Show more" calls the tool again with `offset`.
- **Ranking by the shopper's query.** Keyword matches in the product **name** rank above matches in tags, which rank above matches in description or colors. With no keywords, products with the **most sizes in stock** come first, so shoppers see items they can actually buy. Optional `sort`: `price_low`, `price_high`, or `name`.
- **New filters:** `size` (only products with that size in stock, e.g. "hoodies in medium" → 21), `min_price` and `max_price`, alongside the existing `category`, `keywords`, and `color`.
- **Narrowing options computed over all matches, not just the page shown:** category counts, main-color counts grouped into families (e.g. hoodies: navy 17, gray 10, where "gray" covers heather/charcoal/dark heather), price bands with counts (Under $50: 2, $50–$75: 23, $75+: 2), and the full price range. The agent may only offer filter values that appear here.
- **Closest matches instead of nothing.** If no product matches every keyword, products matching some of them are returned and flagged `keyword_match: "some"`, and the agent says so. For example, "Harvard sweatpants" now returns the 2025 Yale vs Harvard T-shirt as the closest match, clearly labeled.
- **Structured follow-ups.** The agent's output (`AgentReply`) gained `suggestions` (up to 4 short follow-up questions), which `/api/chat` returns and the chat renders as clickable chips (improvement 2).
- **Safety net.** At most 12 product cards are shown per reply, even if the model lists more IDs. Cards are still rebuilt from the database by `load_product_cards`.
- **Prompt updates.** Report `total_matches` and the price range of the full matching set (described as such, not as the range of the cards shown), offer concrete narrowing options with their real counts, page with `offset` for "show more", and keep the default page size.

**Verified with one real model call** (clicking the "What hoodies do you have?" chip):
- The agent made one `search_catalogue(category="hoodie", limit=8)` call.
- It showed **8 cards, exactly the database's top-ranked first page**, and replied: *"We have 27 hoodies, with these top picks ranging from $45.00 to $88.00 … 17 are navy and 10 are gray. These are the top picks shown—ask to see more, or narrow by color or price."*
- It offered the chips "Show more hoodies", "Show navy hoodies", "Show gray hoodies", and "Hoodies under $50", all backed by real counts.
- One imprecision: the $45–$88 range it quoted is for all 27 hoodies, not just the 8 shown.

**Follow-up correction:** the prompt now says the search's price range covers the full matching set, never just the cards on the page, and it gives the agent an example to copy: *"Our 27 hoodies range from $45.00 to $88.00 overall; here are the top 8 matches."* The distinction matters most for broad searches: for "What do you have in stock?", all 102 products range from $32 to $98, but the first page of 8 only spans $32–$72. Only the wording guidance changed; the search logic is the same. To save Portkey budget, this was checked with free tests (the rule reaches the model's instructions, and the reported range really covers every match), not with another real model call.

### Why it helps

Before, "What hoodies do you have?" dropped 27 cards into a small chat window, and "What do you have in stock?" could have produced up to 40. Now the shopper sees a manageable set of the most relevant, most available items first, plus the true total and one-click ways to narrow by color, price, size, or to see more. Every product, price, and count still comes from the database. For the business, shoppers reach a product they want faster, and each chat reply stays smaller, which also keeps model usage down.
