# Homework 4 — Campus Customs Shop + Chatbot

A Yale Bulldog Blue / Campus Customs storefront with an AI shopping assistant.

- **Frontend:** React + Vite + TypeScript (`frontend/`)
- **Backend:** FastAPI with a PydanticAI agent (`backend/`), using `gpt-5.6-luna` through Portkey
- **Data:** the provided SQLite database and product images (the local data pack, not committed)

## What's here

```
hw4/
├── README.md              this file
├── AI_prompts.md          every prompt given to the coding assistant, by problem
├── requirements.txt       backend Python dependencies
├── .env.example           environment template (placeholders only)
├── backend/
│   ├── main.py            FastAPI app: products, images, auth, chat, chat history
│   ├── agent.py           PydanticAI agent (Portkey + gpt-5.6-luna), agent loop, audit hook
│   ├── tools.py           database tools: search, description, price, stock by size, store info
│   ├── models.py          Pydantic models for the API, tools, agent output, audit entries
│   ├── audit.py           append-only audit trail writer
│   └── prompts/prompt.md  system prompt, including the safety rules
├── frontend/              React + Vite + TypeScript site
├── data/                  put the data pack here (see below); README.md only in Git
└── output/
    ├── harness.md         harness documentation (final reference + per-problem build log)
    ├── design.md          Problem 10 design write-up
    ├── usability.md       Problem 9 usability write-up
    ├── app_check.html     Problem 11 live app check (+ app_check_images/)
    └── audit_trail.json   append-only agent audit trail
```

## 1. Place the local data pack

The database and product images are **not** in this repository. Copy them from the Homework 4 data pack into `hw4/data/`:

```
hw4/data/campus_customs.db
hw4/data/products/*.jpg        (102 images)
```

## 2. Set the API key

From the `hw4/` folder, copy the template and add your Portkey key:

```bash
cp .env.example .env
```

Then edit `.env` and set `PORTKEY_API_KEY=…`. You can also export `PORTKEY_API_KEY` in your shell instead. The shop, products, and login work without a key; only the chatbot needs it.

## 3. Run the backend (terminal 1)

Requires Python 3.12+ (tested with 3.14). From the `hw4/` folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

The API is then at http://localhost:8000. For example, http://localhost:8000/api/health returns `{"status":"ok"}`.

## 4. Run the frontend (terminal 2)

Requires Node.js 20+ (tested with Node 24). From the `hw4/` folder:

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints, normally http://localhost:5173. Vite forwards `/api` and `/media` requests to the backend on port 8000.

If port 8000 is already in use, start uvicorn with another `--port` and run the frontend as `BACKEND_URL=http://localhost:<port> npm run dev`.

## Try it

- **Log in** with the data pack's test account (`test@campuscustoms.yale.edu`), or create an account. New accounts are stored in the `users` table with PBKDF2-SHA256 password hashes.
- **Products:** search, filter by category or price, and sort. Click any card for its product page with live stock by size.
- **Chat** (bottom-right): try the quick-start suggestions, e.g. "What hoodies do you have?". You can also ask about a size or price, or ask "Do you have this in medium?" on a product page. Logged-in conversations are saved and reloaded.
- **Audit trail:** each chat message appends its agent steps (tool calls, results, stop reason) to `output/audit_trail.json`.

## Checks

```bash
cd frontend
npm run build
npm run lint
```

`output/harness.md` documents the models, tools, safety rules, loop limits, the model setup, and the audit trail, along with the tests run for each problem. `output/app_check.html` shows screenshots of the live checks.

## Not committed

- `.env` (real API key)
- `data/campus_customs.db` and `data/products/` (data pack)
- `.venv/`, `node_modules/`, `dist/`, caches, and audit-trail lock and temp files

See `.gitignore`.
