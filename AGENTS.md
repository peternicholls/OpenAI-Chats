# Repository Guidelines

## Project Structure & Module Organization

`chatgpt_archive/` contains the core CLI and exporters. `api/` holds the FastAPI backend, split into `routers/`, `services/`, `models/`, and `middleware/`. `web/` is the Next.js frontend with source under `web/src/` and tests under `web/__tests__/`. Python tests live in `tests/` and `api/tests/`. Shared docs and specs are in `docs/` and `specs/`. AI-specific shared guidance lives in `.ai/`, with Codex skills in `.codex/skills/` and GitHub-side agent files in `.github/agents/`.

## Build, Test, and Development Commands

- `pip install -e .` installs the CLI package locally.
- `pip install -e ".[dev]"` installs Python test dependencies.
- `pytest tests/ api/tests/ -q` runs the Python and API test suites.
- `cd api && uvicorn main:app --reload` starts the API locally.
- `cd web && npm install` installs frontend dependencies.
- `cd web && npm run dev` starts the Next.js app.
- `cd web && npm run build` builds the frontend for production.
- `cd web && npm test` runs Vitest unit tests.
- `cd web && npm run test:e2e` runs Playwright end-to-end tests.
- `docker-compose up -d` runs the local stack with Docker.

## Coding Style & Naming Conventions

Python targets 3.10+ for the CLI and 3.11+ for the API. Format API Python with Black and lint with Ruff using a 100-character line length: `cd api && black . && ruff check .`. Use `snake_case` for Python modules/functions and `PascalCase` for Pydantic models/classes. Frontend code is TypeScript with ESLint (`cd web && npm run lint`); use React component names in `PascalCase`, hooks in `useThing` form, and keep files aligned with existing Next.js routing conventions.

## Testing Guidelines

Use `pytest` for Python and API coverage, `vitest` with Testing Library for frontend units, and Playwright for browser flows. Name Python tests `test_*.py`; colocate frontend tests under `web/__tests__/`. Add or update tests with every behavior change, especially around import, search, export, and API contracts.

## Commit & Pull Request Guidelines

Recent history follows conventional prefixes such as `fix:`, `fix(ci):`, `fix(review):`, and `style:`. Keep commits focused and imperative, for example `fix(api): handle missing export metadata`. PRs should summarize user-facing impact, list test coverage, link related issues/specs, and include screenshots for visible UI changes.

## Shared Standards

Canonical engineering standards and skills live in `.ai/` and are surfaced to Copilot via `.github/instructions/`. Read the relevant file before generating or modifying code in that domain:

- **AI collaboration policy** — `.ai/standards/ai-collaboration.md`
- **CSS conventions** — `.ai/standards/css-guidelines.md`
- **Frontend UI patterns** — `.ai/patterns/frontend-ui.md`
- **Modern CSS skill** — `.ai/skills/modern-css/SKILL.md`

## Agent-Specific Notes

Keep reusable AI guidance in `.ai/` and reference it from `.codex/skills/` or `.github/agents/` instead of duplicating instructions across tool-specific files.
