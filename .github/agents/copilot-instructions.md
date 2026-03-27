# OpenAI-Chats Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-25

## Active Technologies
- Python 3.11+ (backend), TypeScript / Next.js 15 (frontend) + FastAPI (API), SQLite via `chatgpt_archive.db` (data layer), React + Tailwind CSS (web UI) (003-inline-media)
- SQLite (no schema changes); local filesystem (permanent archive media store) (003-inline-media)
- Python 3.11+ (backend), TypeScript / Next.js 16 / React 19 (frontend) + FastAPI, existing API response models, Next.js App Router, Tailwind CSS, planned `react-markdown` + `remark-breaks` for safe markdown rendering (004-frontend-formatting)
- SQLite plus existing archive media filesystem; no schema changes (004-frontend-formatting)
- Python 3.10+ (backend), TypeScript 5 / React 19 / Next.js 16 (frontend) + FastAPI, Pydantic, SQLite-backed archive service, React, Tailwind CSS, existing attachment components; planned addition of `react-markdown` and `remark-breaks` (004-frontend-formatting)
- SQLite for indexed archive data; filesystem-backed archive media store already introduced by feature 003; no schema changes planned (004-frontend-formatting)

### Backend (Python)
- Python 3.8+ with virtual environment (.venv/)
- FastAPI for API backend (api/)
- SQLite with FTS5 for database
- pytest for testing (pytest-asyncio, pytest-mock, httpx)

### Frontend (TypeScript/React)
- Next.js 16 with App Router (web/)
- React 19 with TypeScript
- Tailwind CSS + shadcn/ui components
- vitest + testing-library for unit tests
- Playwright for E2E tests

### Infrastructure
- Docker Compose for deployment
- nginx for static file serving

## Project Structure

```text
chatgpt_archive/         # Core Python library (CLI tool)
api/                     # FastAPI backend
  routers/               # API endpoints
  services/              # Business logic
  models/                # Pydantic models
  tests/                 # API integration tests (62 tests)
web/                     # Next.js frontend
  src/
    app/                 # App Router pages
    components/          # React components
    hooks/               # Custom hooks
    services/            # API client
  __tests__/             # Test files
    components/          # Component tests
    hooks/               # Hook tests
    services/            # API client tests
    e2e/                 # Playwright E2E tests
    mocks/               # MSW handlers
tests/                   # Core library tests
specs/                   # Design documents
docker/                  # Dockerfiles
```

## Commands

```bash
# Activate Python virtual environment
source .venv/bin/activate

# Run core library tests
pytest tests/

# Run API tests (62 tests)
pytest api/tests/ -v

# Run frontend tests (55 tests)
cd web && npm test

# Run E2E tests (Playwright)
cd web && npm run test:e2e

# Start dev servers
cd web && npm run dev         # Frontend on :3000
cd api && uvicorn main:app    # API on :8000

# Docker deployment
docker-compose up -d
```

## Code Style

### Python
- Black for formatting
- Ruff for linting
- Type hints required for public functions
- Google-style docstrings

### TypeScript/React
- ESLint + Prettier
- Functional components with hooks
- Server components by default, 'use client' for interactivity

## Recent Changes
- 004-frontend-formatting: Added Python 3.10+ (backend), TypeScript 5 / React 19 / Next.js 16 (frontend) + FastAPI, Pydantic, SQLite-backed archive service, React, Tailwind CSS, existing attachment components; planned addition of `react-markdown` and `remark-breaks`
- 004-frontend-formatting: Added Python 3.11+ (backend), TypeScript / Next.js 16 / React 19 (frontend) + FastAPI, existing API response models, Next.js App Router, Tailwind CSS, planned `react-markdown` + `remark-breaks` for safe markdown rendering
- 003-inline-media: Added Python 3.11+ (backend), TypeScript / Next.js 15 (frontend) + FastAPI (API), SQLite via `chatgpt_archive.db` (data layer), React + Tailwind CSS (web UI)

  - Test suite: 62 API tests, 55 frontend tests, 27 E2E tests
  - Coverage: API 82%, Frontend core paths covered

<!-- MANUAL ADDITIONS START -->
## Test Commands Quick Reference

```bash
# All tests at once
source .venv/bin/activate && pytest api/tests/ -v && cd web && npm test

# With coverage
pytest api/tests/ --cov=api --cov-report=term-missing
cd web && npm test -- --coverage
```

### Agent Skills 
Pick the relevant agent skill file from the `.github/agents/` directory for the task at hand. Each file contains specific instructions, tools, and handoffs for different agent roles (e.g., MCP Builder, Paid Media Auditor, Studio Operations). Use the appropriate agent to ensure optimal performance and task execution.

<!-- MANUAL ADDITIONS END -->
