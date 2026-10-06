# Campus Customs: Design (Problem 10)

**Concept: "Old Campus storefront."** Yale blue and white on warm ivory paper, collegiate serif headlines, a heraldic shield mark, and Handsome Dan XIX as the shop's seal and the face of its assistant. The goal is to look like a real, premium Yale shop that has been across from campus since 1975, not a template. Functionality from Problems 3–9 is unchanged. Only the frontend changed: no database, backend, agent, or search changes.

## What changed and why it should help customers stay and buy

### 1. Brand system: color, type, and mark

- **Palette:** Yale blue `#00356b` with a deeper navy for the header, footer, and hero; a light "sky" blue accent; a warm ivory page (`#f8f6f1`) instead of stark white; white cards.
- **Type:** headlines, prices, and the brand name use a classic book serif (Iowan Old Style / Palatino stack, from fonts already on the device, so nothing extra downloads). Small uppercase labels with wide letter-spacing are used for eyebrows, filters, and category tags.
- **Shield mark:** an SVG shield with a serif "Y" replaces the plain boxed "Y" in the header and footer.
- **Why:** a consistent, recognizably Yale look signals an established, official store, and trust is what turns browsing into buying. The ivory and serif pairing feels premium and calm, which keeps attention on the products.

### 2. Navigation and footer

- **Announcement bar** above the nav: "Official Yale merchandise · 57 Broadway, New Haven · Open 7 days a week". These are verified store facts.
- **Nav links** get a hover underline that stays under the current page. Logged-in shoppers see an italic "Hi, {name}" and a pill-shaped Log out button.
- **Footer** now has three columns: brand story, a Visit column (address, hours, phone, email), and Shop links into the category filters. It also carries the Handsome Dan photo credit site-wide.
- **Why:** shoppers always know where they are, and the store's real address and hours are visible on every page, which builds trust and supports in-store visits. Footer category links give a second route into products from anywhere.
- **On phones,** the header scrolls away instead of sticking, so products get the screen.

### 3. Home hero with Handsome Dan as the shop's seal

- **Same content as before:** eyebrow, headline, copy, both buttons, and the photo with its credit. The headline now sets *Yale* in italic light blue.
- **Background:** a layered navy background with a faint diagonal pinstripe, a soft blue glow behind the mascot, and a very large faint serif "Y" watermark.
- **Mascot seal:** Handsome Dan's existing photo sits in a white-bordered circle inside a ring of set type reading "HANDSOME DAN XIX · YALE'S BULLDOG MASCOT · SINCE 1889", like a collegiate seal. The ring turns slightly on hover.
- **Fact strip:** "1975 · Founded in New Haven", "102 · Styles in the shop" (live count from the API), "7 days · Open at 57 Broadway".
- **Motion:** a gentle fade-up when the page loads.
- **Why:** the photo now reads as the store's emblem rather than an added picture. Pride in the mascot is a strong emotional reason to buy Yale gear. The fact strip gives quick, true credibility points at the moment a visitor decides whether to stay.

### 4. Shop by category (Home)

- Five tiles: Hoodies (27), Crewnecks (28), T-shirts (25), Quarter-zips (11), Jackets & fleece (8). The counts come live from `/api/products`, and each tile opens the Products page already filtered (Problem 9 filters).
- The "01 / 02 / 03" highlight cards keep their text, with numbered serif indices.
- **Why:** most shoppers arrive knowing the *kind* of thing they want. One click from the home page to the right filtered list removes a step between interest and a product page.

### 5. Product cards (Products page, Home, and chat)

- **Image:** sits on a soft off-white panel and zooms slightly on hover.
- **Text:** a small uppercase garment-type label from the database (e.g. "PULLOVER HOODIE"), a serif product name, a bold price with aligned digits, and a two-line description.
- **"View details →"** slides in on hover or keyboard focus.
- **"Low stock" badge:** shown only when the real inventory total is 15 or fewer. Currently that's 3 products: Football Left Chest T Shirt, T Felt Y Heavyweight, Tri Blend Sports Hockey T Shirt.
- **The same component** is used everywhere, so chat cards look and behave exactly like catalogue cards.
- **Why:** clearer hierarchy (type, then name, then price) makes scanning 102 items faster. Hover feedback makes cards feel clickable. An honest scarcity cue from real inventory encourages purchase without inventing urgency.

### 6. Products page filters

- The filter bar is a white card with small uppercase labels and soft ivory inputs that turn white on focus. The Clear button is a pill.
- **Why:** the tools read as part of the store, not a form, so shoppers are more likely to use them and find a match.

### 7. Single product page

- **Image:** large, in a framed white panel that stays in view (sticky) while the shopper reads the details on desktop.
- **Details:** the price is set large in serif. The size/stock table has a tinted header, bold sizes, and sold-out rows struck through.
- **New actions:** **"Ask about this item"** opens the branded chat with the product-aware quick-start ready (it sends nothing until clicked), and **"Keep browsing"** returns to Products.
- **Trust list:** "Official Yale merchandise · Shop in person at 57 Broadway, New Haven · Stock shown live from our inventory". All three are factual.
- **Why:** this is where the buy decision happens. Price and stock are unmissable, help is one click away for size or fit questions, and the trust points answer "is this legit?" on the spot.

### 8. Chat widget integrated with the brand

- **Launcher:** a navy pill with a white border, Handsome Dan's face in a sky-blue ring, and "Chat".
- **Header:** a pinstriped navy header with the Dan avatar, "Campus Customs Assistant" in serif, and the subtitle "Styles, sizes & stock · Yale Bulldog Blue". The avatar is the existing photo, cropped with CSS to his face.
- **Body:** an ivory message area. Shopper bubbles are Yale blue; assistant bubbles are white with a soft shadow. Inputs and suggestion chips are rounded, and the typing dots are blue.
- **Motion:** the panel slides up gently when opened.
- **Why:** a chat that looks like part of the store (and wears the mascot) feels trustworthy and on-brand, so more shoppers will ask a question instead of leaving. That's where size, stock, and "what do you have for…" questions become sales.

### 9. Forms, About, and details

- **Log in / Create account:** centered white cards with a Yale-blue top rule, an eyebrow ("Welcome back, Bulldog" / "Join Yale Bulldog Blue"), and one line on the real benefit (the assistant remembers your conversation).
- **About:** set on a white "page" card with a ruled heading and a tinted info box for the visit details.
- **Buttons:** consistent pill shape, with a slight lift on hover.
- **Accessibility:** a visible sky-blue focus ring for keyboard users. Motion is disabled for shoppers who set "reduce motion".
- **Why:** account creation is framed by what the shopper gets, which raises sign-ups for returning customers. Polished small details make the whole store feel cared for, and accessible focus states and reduced motion keep it usable for everyone.

## Responsive behavior

At phone widths:
- The hero stacks with a smaller seal, and the fact strip becomes three compact columns.
- Product grids show two columns; descriptions are hidden so names and prices stay readable.
- The footer stacks, and the chat panel fits the screen.

No page scrolls sideways at 375 px (tested on 6 pages).

## Kept intact

- All 102 products and their original images.
- The Handsome Dan XIX photo and its CC BY-SA 4.0 credit, in the hero, now also in the footer.
- Authentication, customer memory, page context, search/filters, quick-start and suggestion chips, product pages, and the agent and its tools.
