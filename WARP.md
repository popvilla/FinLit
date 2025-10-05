# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project modules

- FinLit Backend (FastAPI, Python 3.11): backend/
- FinLit Frontend (Next.js, TypeScript): frontend/
- Obsidian MCP Server (Express + TypeScript): src/
- Supabase schema/migrations: supabase/
- A second copy of the MCP server exists under Artemis Agentic Memory Layer(MCP)/. Treat src/ at repo root as canonical unless maintainers say otherwise.

Quickstart commands (Windows pwsh 7+)
Note: Use the exact commands below; they are taken from repo configs and READMEs. Replace any placeholder env values before running.

Supabase (local dev)

- Initialize (if first run): supabase init
- Start local services: supabase start
- Apply schema to local instance: supabase db push

Backend (FastAPI)

- From backend/:
  - Install deps (Poetry): poetry install
  - Create env: cp .env.example .env (PowerShell alias for Copy-Item works)
  - Run dev server: poetry run uvicorn main:app --reload --port 8000
  - Smoke test: curl <http://localhost:8000/>
  - Note: No test suite or linter configured here in this snapshot.

Frontend (Next.js)

- From frontend/:
  - Create env: cp .env.local.example .env.local
  - Expected commands per README: npm install && npm run dev
  - Current snapshot caveat: package.json and the lib/* imports used by components (e.g., @/lib/auth, @/lib/api, @/lib/models) are missing, so the frontend won’t build until those are added.

Obsidian MCP Server (Express + TypeScript)

- From repo root (where package.json lives):
  - Install deps: npm install
  - Create env: cp .env.example .env (set MCP_API_KEY, OBSIDIAN_BASE_URL, OBSIDIAN_API_KEY)
  - Dev mode (ts-node + nodemon): npm run dev
  - Build: npm run build
  - Start (compiled dist): npm start
  - Lint: npm run lint

MCP via Docker

- Build & run with compose (root docker-compose.yml): docker-compose up --build
  - Ensure env values are set/updated before running.

MCP API smoke tests (from MCP README)

- Replace placeholders and ensure Authorization header matches MCP_API_KEY.
- Read a note:
  curl -X POST <http://localhost:3000/api/getContext> -H "Content-Type: application/json" -H "Authorization: Bearer {{MCP_API_KEY}}" -d '{"path":"My Daily Notes/2023-10-27.md"}'
- Append to a note:
  curl -X POST <http://localhost:3000/api/appendContext> -H "Content-Type: application/json" -H "Authorization: Bearer {{MCP_API_KEY}}" -d '{"path":"My Daily Notes/2023-10-27.md","content":"\n- New item"}'

High-level architecture

- Backend (backend/)
  - FastAPI app in backend/main.py with CORS for <http://localhost:3000>.
  - Auth: backend/auth.py provides JWT creation/verification, role-guard dependencies (student, instructor, admin). SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES required.
  - Data access: backend/database.py creates a Supabase client using SUPABASE_URL and SUPABASE_SERVICE_KEY (service role for admin-like access). RLS-aware anon client commented for potential use.
  - Pydantic models: backend/models.py defines User, Portfolio, Trade, MarketEvent, ChatbotInteraction, Webinar schemas.
  - Routes (selected):
    - /signup, /token, /users/me (Auth)
    - /portfolios/{user_id} (Student/Admin read)
    - /trades (Execute trade), /portfolios/{portfolio_id}/trades (List)
    - /market-events (List)
    - /chatbot/ask, /chatbot/history (OpenAI-backed interactions)
    - /webinars (List/Create)
  - Chatbot/OpenAI: backend/chatbot.py uses OPENAI_API_KEY and gpt-3.5-turbo by default.

- Supabase (supabase/migrations/0001_initial_schema.sql)
  - Tables: users, portfolios, trades, market_events, webinars, chatbot_interactions.
  - RLS highlights: users limited to self; portfolios owned by user_id; trades constrained via portfolio ownership; market_events/webinars readable by authenticated users; instructors manage their webinars.

- Frontend (frontend/)
  - Next.js app router under src/app/. Components for AuthForm, PortfolioDashboard, TradeForm, ChatbotWidget.
  - Uses Tailwind (globals.css) and path alias @/ to src/. Missing lib/ modules prevent builds in this snapshot.

- MCP Server (src/)
  - Express + TypeScript server (src/index.ts) mounts /api router (src/mcp-server/index.ts).
  - Auth middleware requires Authorization: Bearer {MCP_API_KEY} (src/mcp-server/middleware/auth.ts).
  - Tool routes proxy to Obsidian Local REST API via axios wrappers (src/services/obsidianRestAPI/*).
  - Config validation fails fast if required envs are absent (src/config/index.ts).
  - Dockerfile builds TS -> JS and runs node non-root; docker-compose exposes 3000.

Repository gotchas and conventions

- Duplicate MCP code: There is a second MCP server copy under Artemis Agentic Memory Layer(MCP)/ with its own Dockerfile/README and nearly identical src/. Prefer the root src/ for development unless instructed otherwise.
- Merge-conflicted/duplicate backend files exist at repo root (pyproject.toml, main.py, and various backend modules). Treat backend/ as the source of truth for the FastAPI app.
- Frontend scaffolding is incomplete (no package.json and missing lib/). Use README instructions but expect to add the missing pieces before it runs.
- No test suites detected across modules; npm test is a placeholder and there is no pytest configuration.

Environment variables (names only)

- Backend (.env): SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_ANON_KEY, OPENAI_API_KEY, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
- Frontend (.env.local): NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, NEXT_PUBLIC_FASTAPI_URL
- MCP (.env): PORT, MCP_API_KEY, OBSIDIAN_BASE_URL, OBSIDIAN_API_KEY, MCP_LOG_LEVEL

Key references

- Project README: FinLit setup and run instructions (Supabase start, backend dev, frontend dev expectations)
  - D:\Repo\Online\Financial-Literacy-with-Semantic-Loop\README.md
- MCP README (tools, docker, cURL examples)
  - D:\Repo\Online\Financial-Literacy-with-Semantic-Loop\Artemis Agentic Memory Layer(MCP)\README.md

Open questions to confirm with maintainers

- Which MCP directory is canonical for future work: repo-root src/ or Artemis Agentic Memory Layer(MCP)/src/?
- What is the plan/timeline to add frontend/package.json and the missing lib/* modules referenced by components?
- Should the backend use the anon Supabase client for RLS-sensitive endpoints instead of the service key everywhere?
