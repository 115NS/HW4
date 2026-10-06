# Homework 4: Campus Customs Shop + Chatbot — AI Prompts

## Setup: Project inspection and preparation

### Prompt

> I’m starting Homework 4, Campus Customs Shop + Chatbot. Let’s set up the project first before working on Problem 1.
> Please inspect the current Homework 4 project folder and the available data. The project will be a React + Vite TypeScript frontend with a Python FastAPI backend using a PydanticAI agent. The provided data includes data/campus_customs.db and data/products/, and the database contains the catalogue, inventory, and users tables.
> Please do the following setup work only:
>
> * Inspect the existing project structure and the provided database/data so you understand what is already available.
> * Check the database schema and existing data rather than assuming field names or structures.
> * Set up the project so we can work through the homework one problem at a time.
> * Use Portkey for the AI calls and keep the API key in the local environment only. Never put secrets into project files or Git.
> * Keep the React/Vite frontend and FastAPI/PydanticAI backend clearly separated.
> * Research the Campus Customs/Yale Bulldog Blue style information required by the assignment when we reach the agent-prompt work, rather than inventing details.
> * Create and maintain AI_prompts.md from the beginning. It should contain one section per homework problem with the actual prompt I give you. Only record follow-up prompts when I actually send one; do not invent follow-ups.
> * Do not solve any homework problem yet.
> * Do not commit data/campus_customs.db or data/products/ to Git.
> * Make sure we can eventually run the required frontend/backend commands from the terminal exactly as the assignment specifies. Pay particular attention to the exact CLI flags and commands the assignment gives us; don’t substitute your own interface.
> * Keep the project easy to test from a clean environment later.
>
> For now, just inspect the project/data and prepare the setup. Tell me what you found and what, if anything, needs to be created before we start Problem 1.
> Do not move on to Problem 1 until I give you the Problem 1 prompt.

## Problem 1: Vibe coder prompts

### Prompt

> I want to complete Problem 1 of Homework 4.
> The goal is to set up and maintain AI_prompts.md as the log of what I type to my vibe coder for this homework.
> Please make sure AI_prompts.md is correctly set up for Homework 4 and that my setup prompt is preserved as the Setup section. Then add a Problem 1 section containing the actual prompt I am giving you now.
> For this homework, keep one section per problem and record the actual prompt I send you. If I later send a follow-up for a problem, record that follow-up too, but never invent follow-ups or prompts that I did not actually send.
> Do not paste the assignment page or URL into the prompt log.
> Do not start building the shop, chatbot, database functionality, frontend, or backend yet unless something is strictly required for Problem 1.
> After completing Problem 1, tell me exactly what you changed and confirm that the prompt log is ready for Problem 2.
> Also, since the final assignment requires a public GitHub repository, initialize a local Git repository in Homework-4 if one does not already exist, using the existing .gitignore. Do not commit the database, product images, .env, or any other secrets/data files.

### Follow-up prompt

The first prompt did not spell out the full Problem 1 requirements: the exact section title, and that each follow-up must include one sentence explaining what the first prompt was missing.

> One clarification for Problem 1: I also need to make sure the AI_prompts.md section follows the exact Problem 1 requirements.
> Please update the Problem 1 section so it includes:
>
> * the problem number and title: “Problem 1: Vibe coder prompts”
> * the actual prompt I sent you for Problem 1, in my own words
> * a follow-up prompt only if I actually needed one after the first prompt, with one sentence explaining what was missing from the first prompt
>
> The assignment says the prompt log is the evidence for this problem, so please make sure it reflects the prompts I actually sent rather than adding invented prompts or assignment text.
> This will correctly count as the real follow-up for Problem 1, because the first prompt didn't include the full Problem 1 requirements; kindly add

## Problem 2: Analyze the database

### Prompt

> I want to complete Problem 2: Analyze the database.
> Please inspect data/campus_customs.db and make sure we understand the database structure based on the actual schema and data, not assumptions.
> For the three required tables — catalogue, inventory, and users — document every table and every field in output/harness.md. For each field, add one short explanation of why that field matters for the Campus Customs shop or chatbot.
> Please keep the existing database analysis accurate and use the actual field names and types from the database. You can also note any other table you find if it is relevant, but do not let that replace the required catalogue, inventory, and users documentation.
> Start or update output/harness.md so this becomes the first substantive section of the harness. We will keep adding to this same file in later problems, so don't overwrite or remove useful setup information.
> Also update AI_prompts.md with the actual Problem 2 prompt I am giving you now. Only add a follow-up if I actually send one later.
> Do not build the shop, chatbot, frontend, authentication, or other functionality yet. Do not modify the database.
> After completing this, report what you found and confirm that the table/field documentation matches the actual database schema.
> One thing I want to be especially careful about because of feedback from my previous homework: whenever a later problem specifies exact commands, CLI flags, routes, or file names, implement those exact interfaces rather than substituting your own. For this problem, just focus on the database analysis and harness.

## Problem 3: Build the Campus Customs website

### Prompt

> I want to complete Problem 3: Build the Campus Customs website.
> Please build the React + Vite + TypeScript frontend and the simple FastAPI backend needed for this problem, using the actual database and product images we inspected in Problem 2.
> The site should have a navigation bar at the top linking to these main pages:
>
> * Home
> * Products
> * About Us
> * Log in
> * Create account
>
> For the Home and About Us pages, research yalebulldogblue.com to understand the Campus Customs/Yale Bulldog Blue style and information, but write the content in our own words. Do not copy text from the original site.
> Products page:
>
> * Read the catalogue from data/campus_customs.db.
> * Show the actual product images using the image paths in the database.
> * Show each product's name, price, and a short description.
> * Make each product card clickable and take the shopper to a single-product page.
> * The single-product page should have a large product image on one side and the full product information on the other, including description, price, and sizes/stock where available.
> * Use the actual database inventory when showing stock information rather than inventing stock.
>
> Add a chat interface in the bottom-right of the site. It does not need to connect to the AI agent yet; for this problem a working UI stub that is ready to call the backend later is enough.
> Create the small FastAPI API needed to read the database and serve the products and product images. The assignment specifically suggests backend/main.py for this. Keep the backend simple for now because it will be expanded into the agent backend in Problem 5.
> Please inspect the existing project before making changes and use the actual database schema and image paths. Do not modify the database or product images.
> Also make sure the project can actually be run and tested locally. Use the standard commands appropriate for the React/Vite frontend and FastAPI backend, and document the commands you use. Do not invent custom CLI flags where standard commands are sufficient. If the assignment later specifies an exact command or flag, we will use that exact interface.
> Please test the implementation after building it:
>
> * frontend starts successfully
> * backend starts successfully
> * products load from the database
> * product images load correctly
> * product cards navigate to individual product pages
> * stock/size information comes from inventory
> * navigation links work
> * chat stub appears and is usable
> * there are no console/runtime errors in the main flows
>
> Update output/harness.md with the relevant Problem 3 implementation details and any important setup/run information. Keep the existing Problem 2 database analysis.
> Update AI_prompts.md with this exact Problem 3 prompt. Only add a follow-up if I actually send one later.
> Do not start Problem 4 or build the AI chatbot/agent yet.

## Problem 4: Create account and login

### Prompt

> I want to complete Problem 4: Create account and login.
> Build the normal authentication flow for the Campus Customs site.
> For Create Account, collect:
>
> * first name
> * last name
> * email
> * password
> * confirm password
>
> For Login, collect:
>
> * email
> * password
>
> New accounts should be stored in the existing users table in data/campus_customs.db. Passwords must be stored securely using the same PBKDF2-SHA256 approach already used by the database, never as plaintext.
> Also verify the existing test account works:
> email: [test@campuscustoms.yale.edu](mailto:test@campuscustoms.yale.edu)
> password: password
> Test both logging into the existing test account and creating/logging into a brand-new account. Make sure duplicate emails, incorrect passwords, password mismatches, and other obvious validation cases are handled appropriately.
> Keep the existing Problem 3 site and product functionality working. Do not start Problem 5 yet.
> Update output/harness.md with a concise explanation of how authentication works, what user information is stored, and how passwords are protected.
> Also update AI_prompts.md with this exact Problem 4 prompt. Only add a follow-up there if I actually send one later.

## Problem 5: PydanticAI agent backend

### Prompt

> I want to complete Problem 5: PydanticAI agent backend.
> Turn the existing Campus Customs chat stub into a real PydanticAI agent behind the FastAPI backend.
> Please keep the agent organized into these four files under backend/:
>
> * backend/prompts/prompt.md
> * backend/agent.py
> * backend/tools.py
> * backend/models.py
>
> Keep backend/main.py as the FastAPI app that is run with:
> uvicorn main:app --reload --port 8000
> when running from the backend/ folder.
> For this problem, the agent should be connected to the existing front-end chat widget so that a message typed into the website is sent to FastAPI and the agent returns a real reply.
> Use Portkey for the model API calls and use gpt-5.6-luna for now. Do not hard-code or expose the API key; use the existing environment setup.
> Add a basic Campus Customs system prompt in backend/prompts/prompt.md with the store's voice and basic safety/helpfulness rules. Keep it easy to expand in later problems.
> Set up the Pydantic/PydanticAI structured types in models.py for the chat response and product cards as needed.
> The agent should be wired so it can receive the user's message and, where available, the logged-in user's context. For now, don't build all the product/search tools yet unless they are necessary for the basic agent connection — later problems will expand the agent's capabilities.
> Keep everything from Problems 3 and 4 working: the website, products API, product pages, authentication, login/logout, and chat UI.
> Test the full flow through the real website: type a message into the chat, make sure it reaches FastAPI, gets handled by the PydanticAI agent through Portkey, and that the response appears in the chat.
> Please avoid unnecessary repeated model calls while testing because I want to conserve my Portkey budget.
> Update output/harness.md with how the frontend connects to FastAPI, how the agent is loaded, which model is being used, and how the basic chat flow works.
> Update AI_prompts.md with this exact Problem 5 prompt. Only add a follow-up if I actually send one later.

### Follow-up prompt

The first prompt did not include any Handsome Dan mascot image, so this follow-up asks for a small Yale-themed photo of him on the Home page.

> For the existing Homework 4 site, I want to add a small Yale-themed visual element featuring Handsome Dan, Yale’s bulldog mascot.
> Please first research who Handsome Dan is and find an appropriate, recognizable photo of Handsome Dan from a reliable/public source, preferably an official Yale source. I want an actual photo rather than a generic bulldog image. Make sure the image is appropriate to use in this student project and don’t replace or disrupt any of the existing product images.
> Then add the Handsome Dan image to the Home page in a way that feels natural with the existing Yale Bulldog Blue/Campus Customs design. Keep the current layout and styling essentially the same — this should be a tasteful small enhancement, not a redesign. It could work as a small mascot feature in or near the hero section or another visually appropriate spot.
> Please make sure the image is stored locally in the project rather than relying on an external image URL, and keep the site working normally. Do not use any Portkey/model calls for this; this is just a frontend change.
> After making the change, run the existing frontend checks and make sure the Home page still renders correctly. Update output/harness.md only if necessary to document the new asset. Do not start Problem 6 yet.
> Also update AI_prompts.md with this exact prompt as a follow-up under the appropriate Problem 5 section, since this is a follow-up request after Problem 5.

## Problem 6: Database tools for the chatbot

### Prompt

> I want to complete Problem 6 of Homework 4.
> Add the database tools needed for the Campus Customs chatbot to answer real product questions using data from data/campus_customs.db.
> The agent should have tools that can look up:
>
> * product description
> * product price
> * stock quantities by size
>
> The agent must use the database for these answers and must never invent prices or stock. If a requested size is out of stock, it should say that clearly.
> Please expand backend/prompts/prompt.md so the agent knows when to use these tools, and add or update the appropriate structured return types in backend/models.py.
> Update output/harness.md with each tool, what it does, and the model fields you chose for the lookup results and why.
> Keep the existing frontend, authentication, Handsome Dan addition, and Problem 5 agent structure working. Do not redesign anything or start Problem 7.
> Please test the tools against the real database with a few representative product/price/stock questions, but keep Portkey/model calls to the minimum necessary. Continue using gpt-5.6-luna through Portkey; do not switch to a more expensive model unless the assignment specifically requires it.
> Update AI_prompts.md with this exact prompt under Problem 6. Only add a follow-up there if I actually send you one.

## Problem 7: Catalogue search with product cards in chat

### Prompt

> I want to complete Problem 7 of Homework 4.
> Update the chatbot so that when a shopper asks about a type or category of product, the agent can search the real Campus Customs catalogue and return structured product matches. The frontend should then dynamically display those matching products as product cards in the chat/page area, including the product image, name, price, and short information.
> For example, if someone asks “What hoodies do you have?”, the agent should search the catalogue rather than guessing and return the relevant products. The product cards should use the real database/product data, not information invented by the model.
> The important part is the API contract: the agent should return structured product matches, and the frontend should render those matches. Please use the existing Pydantic/PydanticAI models and tools where appropriate rather than creating a separate parallel system.
> Also make sure the dynamically displayed product cards behave exactly like the existing product cards from Problem 3. Clicking one should open the same single-item product page with the large image and full product information.
> Update backend/prompts/prompt.md so the agent knows when and how to search for product matches. Update output/harness.md to explain how a chat search becomes structured product results and then product cards on the frontend.
> Please test this end to end with at least one real catalogue search through the chatbot and verify that the returned cards are the correct products and that clicking a returned card opens the correct product detail page. Also run the existing regression tests for Problems 3–6.
> Keep the testing efficient and minimize real Portkey/model calls. Continue using gpt-5.6-luna through Portkey; do not switch models unless the assignment specifically requires it.
> Keep the existing authentication, price/description/stock tools, Handsome Dan addition, and other working functionality intact. Do not start Problem 8.
> Update AI_prompts.md with this exact prompt under Problem 7. Only add a follow-up there if I actually send you one.

## Problem 8: Customer memory

### Prompt

> I want to complete Problem 8 of Homework 4: Customer memory.
> Please build this on top of the existing Homework 4 implementation without breaking the work from Problems 1–7.
> When a shopper is logged in, persist their chat history in the existing data/campus_customs.db chat_messages table and reload that history when they return. Guest users should still be able to chat normally, but their chat history does not need to persist.
> For logged-in users, make sure the agent receives enough customer context to know who is chatting, specifically their name and email. Follow the existing PydanticAI agent/context pattern rather than exposing unnecessary account information to the model.
> Also add page context to the agent. When a shopper is on a single-product page and asks something like “do you have this in pink?”, the agent should know which product they are referring to from the current page. Pass the relevant product context through the existing agent context/request flow rather than making the model guess.
> Please inspect the existing chat_messages table and current chat implementation before changing anything, and reuse its existing fields/structure where appropriate.
> Make sure:
>
> * logged-in users see their previous chat history after logging back in or refreshing/reopening the site
> * guest users can still chat without errors
> * only the logged-in user's own chat history is loaded
> * user name and email are available to the agent for logged-in users
> * the agent receives the current product/page context when the user is on a product page
> * chat messages are persisted only after successful logged-in-user conversations
> * passwords, password hashes, and other unnecessary account fields are never sent to the model
> * existing product search, product cards, authentication, and chat behavior continue to work
>
> Update output/harness.md to explain:
>
> 1. how chat history is stored and reloaded,
> 2. what customer fields the agent sees and why,
> 3. how page/product context is passed to the agent.
>
> Test the feature with both a logged-in user and a guest, including returning to a logged-in conversation and asking a question from a product page. Use the real database carefully and do not leave unwanted test users or test data behind.
> Use the existing Portkey/gpt-5.6-luna setup only when a real model call is actually needed for testing. Avoid unnecessary paid model calls.
> Update AI_prompts.md with this exact prompt under Problem 8. Do not add a follow-up unless I actually send you one.

## Problem 9: Usability improvements

### Prompt

> I want to complete Problem 9 of Homework 4: Usability improvements.
> Please build on the existing Homework 4 implementation from Problems 1–8. Do not redesign the site or undo any existing functionality.
> I want these four usability improvements:
>
> 1. Front-end improvement: product search and filtering
>
> Add a useful search/filter experience to the Products page so shoppers can find products more easily among the 102 products in the catalogue.
> At minimum, let shoppers search by product name/keywords and filter by garment category. If it fits naturally with the existing design, also add a simple price filter or sort option.
> Use the existing database/API data rather than creating a separate product dataset. Keep the current product cards and single-product pages working exactly as they do now.
>
> 2. Front-end improvement: chat quick-start suggestions
>
> Improve the chat widget so that when the chat is first opened, it gives the shopper a few clickable suggested questions/prompts. For example:
>
> * What hoodies do you have?
> * What do you have in stock?
> * Help me find Yale gear.
>
> Clicking a suggestion should put/send that question through the existing chat flow. Keep the current chat functionality and product cards intact.
>
> 3. Agent/backend improvement: store information tool
>
> Add a small agent tool for factual Campus Customs store information such as the store address, hours, and phone number.
> The agent should use this tool for store-information questions instead of unnecessarily calling product-search tools. Keep the information grounded in the store facts already established in the project.
> Update backend/prompts/prompt.md so the agent knows when to use this tool.
>
> 4. Agent/backend improvement: make product search more efficient and useful
>
> Improve the existing catalogue search so that large searches are handled more usefully in the chatbot instead of overwhelming the shopper with a huge number of product cards.
> Keep the Problem 7 behavior intact: when the shopper asks for a product category, the agent should still search the real catalogue and return matching product cards. Do not simply remove results or hard-code a small product list.
> Use sensible ranking/narrowing based on the shopper's query, and when there are many matches, give the shopper a useful way to narrow the results. Make sure the product information and cards still come from the database.
> For all four improvements:
>
> * Do not break Problems 1–8.
> * Do not modify the seed database permanently with test data.
> * Keep authentication, customer memory, page context, product pages, product cards, and the existing chatbot working.
> * Use fake/function models for automated tests wherever possible.
> * Do not make unnecessary Portkey/model calls. Only use a real model call if it is genuinely necessary to verify an end-to-end agent behavior.
> * If you do need a real model call, tell me before spending multiple calls.
> * Run the existing build, lint, and regression checks.
> * Make sure all four improvements actually appear in the running application.
>
> Create output/usability.md and, for each of the four improvements, explain:
>
> 1. What was added.
> 2. Why it helps a Campus Customs shopper or the business.
>
> Keep the write-up factual and based on what was actually implemented and tested.
> Update output/harness.md with any important implementation/testing details if needed.
> Update AI_prompts.md with this exact prompt under Problem 9. Do not add a follow-up unless I actually send you one.
> Do not start Problem 10 yet

### Follow-up prompt

The first prompt did not say how the chatbot should describe the price range for a paged search, and the live test showed it attributing the full set's $45–$88 range to only the 8 products on the page.

> Please make one small correction to Problem 9 based on the live test result. In the chatbot response for a paged search such as “What hoodies do you have?”, make sure the price range is clearly described as applying to the full matching set of products, not just the 8 products currently displayed on the page. For example, say that the 27 hoodies range from $45–$88 overall, while the current page shows the top 8 matches.
> Do not change the search logic or other Problem 9 features. Update any relevant tests or documentation if needed, run the free checks, and update AI_prompts.md with this as a real follow-up under Problem 9. Do not start Problem 10.
> And yes, I’m still keeping an eye on your Portkey budget. The agent powering the chatbot is currently gpt-5.6-luna through Portkey; Claude's daily budget is separate. We should continue avoiding unnecessary real calls. Also, remember that “2 model calls” does not necessarily mean $2—actual Portkey spend depends on tokens/model usage.

## Problem 10: Style the website

### Prompt

> I want to complete Problem 10 of Homework 4.
>
> Please style the existing Campus Customs/Yale Bulldog Blue website so it feels more like a polished, real Yale/Campus Customs storefront while keeping everything we have already built working.
>
> I want the design to feel distinctly Yale and premium rather than like a generic ecommerce template. Keep the existing navy/white Yale color direction, but improve the visual hierarchy, typography, spacing, buttons, product cards, chat widget, and overall polish. Use subtle motion/hover effects where they genuinely improve the experience, but do not overdo animations.
>
> Please keep Handsome Dan XIX from Problem 5 as part of the site's visual identity. Make the existing Handsome Dan image feel intentionally integrated into the design rather than like an unrelated image that was added afterward.
>
> A few specific things I want:
>
> Make the Home page hero feel more polished and visually interesting while preserving its current content and functionality.
> Improve the product cards so browsing feels more like a real premium campus store.
> Make the chat widget feel integrated with the site branding rather than like a generic floating chat box.
> Improve typography, spacing, buttons, hover states, and small visual details throughout the site.
> Keep the site responsive on desktop and mobile.
> Do not remove any existing functionality from Problems 3–9.
> Do not change the underlying database or product data.
> Do not make unnecessary changes to the authentication, agent logic, tools, or search behavior.
> Do not use any Portkey/model calls for this problem unless absolutely necessary; this is primarily a frontend/design task.
> Preserve all 102 products and their existing images.
> Keep the existing Handsome Dan image and its required attribution.
> Please use your judgment on the exact design details rather than making the site look like a generic template. The goal is a cohesive, distinctive Yale/Campus Customs storefront.
> Create/update output/design.md as required by the assignment. Keep it concrete and concise: explain what you changed and why each change should help customers stick around and buy.
>
> After implementing the design, run the existing build, lint, and relevant browser/regression checks and make sure all existing functionality still works.
>
> Update AI_prompts.md with this exact prompt under Problem 10. Do not start Problem 11 yet.

## Problem 11: Live app check

### Prompt

> I want to complete Problem 11 of Homework 4.
> Test the live site and create output/app_check.html as required by the assignment. Use the actual running app and real database data for the checks, and take clear screenshots that prove each result.
> Please test these three things:
>
> 1. Chat inventory check:
> Ask the chatbot about the stock of a specific product/size and verify that the answer gives the real inventory and price from the database. Choose a product and size where the result is easy to show clearly.
> 2. Dynamic search-result cards:
> Ask the chatbot a category question such as “What hoodies do you have?” and verify that the matching products appear dynamically as product cards with the correct images, names, prices, and other visible product information.
> 3. Problem 9 usability feature:
> Test one of the usability improvements from Problem 9. Choose one that is easy to demonstrate clearly in a screenshot, such as the Products page search/filtering or the chat quick-start suggestions.
>
> For each of the three checks, take a clear screenshot of the actual running site and save the images in output/app_check_images/. Then create output/app_check.html with:
>
> * a clear heading for each check
> * the corresponding screenshot
> * 1–2 sentences explaining exactly what the screenshot proves
> * relative image paths from app_check.html to the images, such as app_check_images/inventory.png
>
> Make the HTML clean and easy to grade.
> Please use real screenshots of the running app rather than mocked/faked screenshots. Avoid making unnecessary changes to the application itself.
> Also update AI_prompts.md with this exact prompt under Problem 11. Do not add a follow-up unless we actually need one later.
> Run the relevant checks after creating the app check and make sure the screenshots and HTML actually work. Do not start Problem 12 yet

## Problem 12: Audit trail, safety rules, and harness

### Prompt

> I want to complete Problem 12 of Homework 4.
> Please implement the audit trail, safety rules, and final harness documentation described in the assignment.
> First inspect the existing project and the work from Problems 1–11 so you build on the current architecture rather than replacing anything.
> For the audit trail, create or update output/audit_trail.json so it is append-only and records agent-loop activity across runs. Each entry should include the time, tool name, short/safe arguments or result, and the reason the agent stopped. Do not wipe or overwrite previous audit entries when the agent runs again. Make sure the logging is actually connected to the agent/tool loop rather than being a test-only artifact.
> Add sensible safety rules to prompts/prompt.md based on the current Campus Customs agent. In particular, make sure the agent does not invent product, price, stock, or store information; uses the database/tools for factual product information; does not expose private customer information; and does not take actions outside the capabilities of the site. Keep the rules practical and consistent with the existing agent behavior.
> Finish output/harness.md so it clearly documents:
>
> * the Pydantic/PydanticAI model fields in models.py and why they were chosen
> * the available tools and agent abilities
> * the safety rules
> * the agent-loop limits and result caps
> * which model is used and how
> * how to run the backend and frontend
> * how the audit trail works and what it records
>
> Please inspect the existing implementation and choose the cleanest approach that fits the current architecture. Do not unnecessarily change features from Problems 1–11.
> Run the existing build, lint, backend tests, and relevant regression checks after making the changes. Also specifically verify that audit_trail.json keeps its previous entries when another agent run occurs, and that the logged arguments/results do not contain sensitive information such as passwords or password hashes.
> Do not make unnecessary real model calls. Use fake/mock testing where possible and only use a real model call if it is genuinely necessary to verify something that cannot otherwise be tested.
> Update AI_prompts.md with this exact prompt under Problem 12. Only add a follow-up there if I actually give you one later.
> Do not start Problem 13 yet

## Problem 13: Submit to GitHub

### Prompt

> I want to complete Problem 13 of Homework 4.
> Please prepare the current Homework 4 project for submission and push it to a public GitHub repository.
> First inspect the entire current project from Problems 1–12 and make sure the submission reflects the final working version. Do not undo or redesign any of the existing work.
> The GitHub submission needs to follow the assignment requirements:
>
> * The homework must be inside a folder named `hw4`.
> * The repository must be public so the grader can open and clone it.
> * Do not upload a zip.
> * Do not commit the real `.env`.
> * Do not commit `data/campus_customs.db`.
> * Do not commit the product images under `data/products/`.
> * Make sure `.gitignore` correctly excludes the real secrets, database, product images, and other local-only files.
> * Include `.env.example` with placeholder values only.
> * Keep `AI_prompts.md`, `requirements.txt`, `README.md`, `frontend/`, `backend/`, `output/`, and the other required source/documentation files in the submission.
> * The `output/` files required by the assignment should be included, including `harness.md`, `design.md`, `usability.md`, `app_check.html`, `app_check_images/`, and `audit_trail.json`.
> * Make sure `README.md` clearly explains how a grader can obtain/place the local data pack and then run the backend and frontend.
> * Check that the README's run instructions match the actual current project commands.
> * Make sure there are no API keys, passwords, password hashes, private customer information, or other secrets anywhere in the files that will be committed.
>
> Before pushing, inspect the final Git diff/status and the exact list of files that will be committed. In particular, verify that the database, product images, `.env`, and any generated secrets are not included.
> Run the final build, lint, and the relevant existing tests/checks before committing.
> Then create or use the appropriate public GitHub repository, put the project under the required `hw4/` folder, commit the final submission, and push it.
> After pushing, verify that the public repository is accessible and that the expected `hw4/` folder and files are actually visible on GitHub.
> Do not make unnecessary changes to the application itself. Do not make real model calls unless absolutely necessary for a final verification.
> Update AI_prompts.md with this exact prompt under Problem 13. Do not start any additional homework work after this.
> Finally, report:
>
> 1. The GitHub repository URL.
> 2. The exact submission path inside the repository.
> 3. What was excluded for security/data-pack reasons.
> 4. The final tests/checks that passed.
> 5. Any issue or limitation you encountered while pushing.

### Follow-up prompt

The first prompt did not say which GitHub repository to push to or how to authenticate, so this follow-up names the public repository I created and the sign-in method.

> I created the public GitHub repository HW4: https://github.com/115NS/HW4
> Please push the prepared hw4/ submission from Homework/hw4-submission/hw4/ to this repository.
> Keep the required structure exactly as the assignment specifies, with the homework inside the hw4/ folder. Do not manually upload anything through GitHub.
> Before pushing, do one final check that .env, campus_customs.db, product images, and any other files excluded by the final scan are not included.
> Use the GitHub authentication method we selected: Token in Terminal tab. I will enter my credentials/token myself in the Terminal when prompted.
> After the push, verify that the public repository has the expected hw4/ folder and files, and give me the final repository URL.
