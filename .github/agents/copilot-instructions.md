# OpenAI-Chats Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-05-01

## Active Technologies

### Backend (Python)
- Python 3.8+ with virtual environment (.venv/)
- FastAPI for API backend (api/)
- SQLite with FTS5 for database
- pytest for testing (pytest-asyncio, pytest-mock, httpx)

### Frontend (TypeScript/React)
- Next.js 16 with App Router (web/)
- React 19 with TypeScript
- Tailwind CSS + shadcn/ui components
- date-fns + react-day-picker for date filters and calendar interactions
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

- **005-browse-by-date**: Planned separate date-browsing mode with local-timezone calendar bucketing
  - Adds calendar summary/day-detail API contracts plus unknown-date grouping
  - Extends non-date search/list flows with initiated-date and updated-date ordering
- **002-web-ui**: Web UI with FastAPI backend, Next.js frontend, Docker deployment
  - Test suite: 62 API tests, 55 frontend tests, 27 E2E tests
  - Coverage: API 82%, Frontend core paths covered
- **001-archive-search-export**: Core CLI tool with import, search, export functionality

<!-- MANUAL ADDITIONS START -->
## Test Commands Quick Reference

```bash
# All tests at once
source .venv/bin/activate && pytest api/tests/ -v && cd web && npm test

# With coverage
pytest api/tests/ --cov=api --cov-report=term-missing
cd web && npm test -- --coverage
```
<!-- MANUAL ADDITIONS END -->
