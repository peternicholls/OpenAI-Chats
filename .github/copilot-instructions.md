# Copilot Instructions for OpenAI-Chats

This file complements `.github/agents/copilot-instructions.md`. Use the agent-specific guidance in `.github/agents/` when it is relevant to the task, but do not assume a specialized agent or the Specify workflow is required for every change.

## Build, test, and lint commands

```bash
# Python setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,excel]"
(cd api && pip install -e ".[dev]")

# Core library tests
source .venv/bin/activate && pytest tests/ -v --tb=short --ignore=tests/unit -q
source .venv/bin/activate && pytest tests/unit/ -v --tb=short
source .venv/bin/activate && pytest tests/unit/test_search.py::test_sanitize_query_empty_raises -q

# API tests
source .venv/bin/activate && pytest api/tests/ -v --tb=short
source .venv/bin/activate && pytest api/tests/test_formatting_service.py::test_build_render_segments_returns_markdown_for_plain_text -q

# Python lint / format checks
source .venv/bin/activate && ruff check chatgpt_archive/ api/
source .venv/bin/activate && black --check chatgpt_archive/ api/

# Frontend
cd web && npm ci
cd web && npm run lint
cd web && npx tsc --noEmit
cd web && npm run test
cd web && npm run test -- __tests__/services/api.test.ts
cd web && npm run test:coverage
cd web && npm run build

# E2E
cd web && npx playwright test __tests__/e2e/conversation.spec.ts

# Full stack via Docker
docker compose up -d
```

## High-level architecture

- `chatgpt_archive/` is the source of truth for archive import, SQLite schema/migrations, FTS5 search, embeddings, and export formats. Prefer extending this package instead of reimplementing logic elsewhere.
- `api/` is a FastAPI adapter over the core library. `api/services/archive_service.py` intentionally wraps `chatgpt_archive` so routers stay thin and HTTP-specific while business logic remains shared.
- SQLite is the primary datastore. `chatgpt_archive/db.py` owns schema creation, FTS triggers, tags/favorites tables, and migrations. Default data lives under `~/.chatgpt-archive/`.
- Media is filesystem-backed, not stored in SQLite. The API resolves attachments from `CHATGPT_ARCHIVE_DIR` / persisted archive media and exposes them through media endpoints.
- Transcript rendering is split across backend and frontend:
  - backend: `api/services/formatting_service.py` converts raw message content plus attachments into ordered `segments`
  - API models: `api/models/responses.py` defines the discriminated union for `markdown`, `attachment`, and `fallback` segments
  - frontend: `web/src/components/conversations/MessageBubble.tsx` prefers `message.segments` over raw `content`
- `web/` is a Next.js App Router app. It uses a centralized fetch wrapper in `web/src/services/api.ts`, React Query hooks for data access, and mirrors API contracts in `web/src/types/index.ts`.
- Docker Compose runs the production-style stack: FastAPI API, Next.js frontend, and nginx as the reverse proxy. `NEXT_PUBLIC_API_URL` is baked into the frontend build.

## Key conventions

- Keep the API layer thin. When adding behavior, first look for the right place in `chatgpt_archive/`; only add API-specific orchestration, validation, progress tracking, or response shaping in `api/`.
- Preserve the boundary between internal DB IDs and public OpenAI IDs. API and frontend contracts use OpenAI conversation/message IDs; SQLite integer IDs stay internal.
- When changing conversation rendering, update the whole `segments` pipeline together: backend formatter, Pydantic response models, frontend TypeScript types, API client normalization, and transcript tests.
- In the frontend, use the shared API client and React Query hooks/query keys instead of ad hoc `fetch` calls.
- Tests are layered:
  - `tests/` and `tests/unit/` cover the core Python package
  - `api/tests/` exercises FastAPI behavior with temporary SQLite databases and shared fixtures in `api/tests/conftest.py`
  - `web/__tests__/` contains Vitest tests, MSW mocks, and Playwright specs under `web/__tests__/e2e`
- The repo often works in sprint branches that line up with a matching `specs/NNN-*` directory. Use the current branch and matching spec folder as context when they exist, but do not assume every task must follow or update the Specify/Speckit workflow.
- `.github/agents/copilot-instructions.md` and other files under `.github/agents/` contain additional agent-oriented context. Reuse their relevant guidance, but keep standard implementation sessions lightweight when no specialized workflow is needed.
