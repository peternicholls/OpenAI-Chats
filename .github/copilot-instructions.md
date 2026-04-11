# Copilot Instructions for OpenAI-Chats

This is the authoritative repository-wide Copilot instruction file for OpenAI-Chats.

Start here first for any task in this repository. Use `.github/agents/` only when the task clearly maps to a specialized workflow or agent handoff; do not default to Speckit or other workflow-specific instructions for ordinary implementation work.

## Tech Stack

- Backend: Python 3.10+ with FastAPI, Pydantic, SQLite, and pytest
- Frontend: Next.js 16 App Router, React 19, TypeScript, Tailwind CSS, shadcn/ui, Vitest, and Playwright
- Infrastructure: Docker Compose with nginx reverse proxy
- Data and search: SQLite via `chatgpt_archive.db`, FTS5 search, and filesystem-backed media storage

## Project Structure

```text
chatgpt_archive/         # Core Python library and source of truth for archive logic
api/                     # FastAPI adapter over the core library
web/                     # Next.js frontend
tests/                   # Core library tests
api/tests/               # API integration tests
web/__tests__/           # Frontend unit and E2E tests
specs/                   # Feature and sprint design artifacts
docker/                  # Container build and runtime files
```

## Build, Test, and Lint Commands

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
# Single frontend test file (Vitest): pass the path directly after `--`
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
- Chronicle meaningful progress, decisions, and discoveries with `/chronicle` during multi-step work so future sessions can recover context more reliably.
- Follow existing style tools rather than inventing local formatting rules: Black and Ruff for Python, ESLint and Prettier-compatible formatting for TypeScript and React.
- Type hints are expected on public Python functions. React code should use functional components, with server components by default and `'use client'` only where interactivity requires it.
- Tests are layered:
  - `tests/` and `tests/unit/` cover the core Python package
  - `api/tests/` exercises FastAPI behavior with temporary SQLite databases and shared fixtures in `api/tests/conftest.py`
  - `web/__tests__/` contains Vitest tests, MSW mocks, and Playwright specs under `web/__tests__/e2e`
- The repo often works in sprint branches that line up with a matching `specs/NNN-*` directory. Use the current branch and matching spec folder as context when they exist, but do not assume every task must follow or update the Specify/Speckit workflow.
- `.github/agents/` contains specialized agent instructions. Use the relevant file there when a task explicitly maps to a specialized workflow, but do not default to those files for ordinary implementation work.

## Task kickoff

- At the start of sprint or feature work, check the current branch name and look for a matching `specs/NNN-*` directory.
- Treat matching sprint/spec artifacts as important context for requirements, scope, and terminology, but not as a mandatory workflow unless the user explicitly asks for that process.
- Start from this file first, then pull in a relevant `.github/agents/` instruction file only if the task clearly belongs to that specialized workflow.

## Current Feature Context

- Recent feature work includes `003-inline-media` and `004-frontend-formatting`.
- Inline media depends on filesystem-backed archive media exposed by the API and rendered through the frontend transcript pipeline.
- Frontend formatting work depends on the backend `segments` pipeline and may involve `react-markdown` and `remark-breaks` for safe markdown rendering.

## Agent Guidance

- If a task calls for a specialized agent workflow, pick the matching instruction file from `.github/agents/`.
- Treat generated or workflow-specific instruction files as supplemental context unless the task explicitly belongs to that workflow.
- Avoid duplicating repository-wide guidance across multiple instruction files. Update this file when shared repo guidance changes.

## Quick Reference

```bash
# All tests at once
source .venv/bin/activate && pytest api/tests/ -v && cd web && npm test

# Coverage
source .venv/bin/activate && pytest api/tests/ --cov=api --cov-report=term-missing
cd web && npm test -- --coverage
```
