# Copilot Instructions for OpenAI-Chats

Use this file as the authoritative repository-wide instruction set for OpenAI-Chats.

Read this file first for every task in this repository. Use `.github/agents/` only when the task clearly matches a specialized workflow or agent handoff. Do not default to Speckit or any other workflow-specific instructions for ordinary implementation work.

## Working Order

Follow this order unless the user gives a better one:

1. Read this file.
2. Check the current branch and any matching `specs/NNN-*` directory.
3. Locate the correct layer for the change before you edit code.
4. Use the smallest validation and rebuild steps that prove the change.
5. Test browser-facing changes in the built-in VS Code browser before you finish.

## Task Flow

Use this task flow:

- Start with this file.
- Check the current branch name.
- Look for a matching `specs/NNN-*` directory.
- Use matching sprint or spec artifacts for requirements, scope, and terminology.
- Do not force a workflow from those artifacts unless the user explicitly asks for it.
- Read a file under `.github/agents/` only when the task clearly belongs to that specialized workflow.

## Core Rules

Follow these rules unless the user explicitly asks otherwise:

- Extend `chatgpt_archive/` before adding duplicate logic elsewhere.
- Keep `api/` thin. Put shared business logic in the core library.
- Preserve the boundary between internal SQLite IDs and public OpenAI IDs.
- Update the entire `segments` pipeline when you change conversation rendering.
- Use the shared frontend API client and React Query hooks instead of ad hoc `fetch` calls.
- Follow existing tooling and formatting conventions.
- Add type hints to public Python functions.
- Use functional React components. Default to server components. Add `'use client'` only when interactivity requires it.
- Record meaningful progress, decisions, and discoveries with `/chronicle` during multi-step work.

## Validation And Completion

Do the following at the end of every task:

- Run the smallest validation step that proves the change.
- Rebuild the smallest part of the app needed to validate the change.
- Bring up the rebuilt target locally when the change affects running behavior.
- Test the changed behavior in the built-in VS Code browser before you finish when the change affects the UI or a browser-accessible flow.
- For changes under `web/`, run `cd web && npx tsc --noEmit` before any rebuild.
- For frontend-only changes, prefer `cd web && npm run build` unless the task specifically requires container validation.
- Run `docker compose build <service> && docker compose up -d <service>` only when the change affects containerized behavior, cross-service integration, deployment configuration, or the user explicitly asks for Docker validation.

## Architecture

Follow these architecture rules:

- Treat `chatgpt_archive/` as the source of truth for archive import, SQLite schema and migrations, FTS5 search, embeddings, and export formats.
- Restrict `api/` code to HTTP-specific orchestration, validation, progress tracking, and response shaping.
- Treat SQLite as the primary datastore. Use `chatgpt_archive/db.py` for schema creation, FTS triggers, favorites and tags tables, and migrations. Assume default data lives under `~/.chatgpt-archive/`.
- Treat media as filesystem-backed. Do not store media in SQLite. Resolve attachments through `CHATGPT_ARCHIVE_DIR` or persisted archive media and expose them through media endpoints.
- Treat transcript rendering as a cross-layer pipeline. Update all of these together when you change rendering behavior:
  - Backend formatter: `api/services/formatting_service.py`
  - API response models: `api/models/responses.py`
  - Frontend rendering: `web/src/components/conversations/MessageBubble.tsx`
- Keep frontend contract types aligned with `web/src/types/index.ts` and the shared API client in `web/src/services/api.ts`.
- Treat Docker Compose as the production-style local stack. Assume it runs FastAPI, Next.js, and nginx. Assume `NEXT_PUBLIC_API_URL` is baked into the frontend build.

## Project Structure

Use these directories for orientation:

```text
chatgpt_archive/         # Core library and source of truth for archive logic
api/                     # FastAPI adapter over the core library
web/                     # Next.js frontend
tests/                   # Core library tests
api/tests/               # API integration tests
web/__tests__/           # Frontend unit and E2E tests
specs/                   # Feature and sprint design artifacts
docker/                  # Container build and runtime files
```

Use this test layout:

- `tests/` and `tests/unit/` for the core Python package
- `api/tests/` for FastAPI behavior with temporary SQLite databases and shared fixtures in `api/tests/conftest.py`
- `web/__tests__/` for Vitest tests, MSW mocks, and Playwright specs under `web/__tests__/e2e`

## Tech Stack

Use the following stack assumptions when you reason about the codebase:

- Backend: Python 3.10+, FastAPI, Pydantic, SQLite, pytest
- Frontend: Next.js 16 App Router, React 19, TypeScript, Tailwind CSS, shadcn/ui, Vitest, Playwright
- Infrastructure: Docker Compose, nginx reverse proxy
- Data and search: SQLite in `chatgpt_archive.db`, FTS5 search, filesystem-backed media storage

## Build, Test, and Lint Commands

Use these commands when setup, validation, or local execution is required:

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
# For a single frontend test file, pass the path directly after `--`
cd web && npm run test -- __tests__/services/api.test.ts
cd web && npm run test:coverage
cd web && npm run build

# E2E
cd web && npx playwright test __tests__/e2e/conversation.spec.ts

# Full stack via Docker
docker compose up -d
```

## Current Feature Context

Use the following context when it applies:

- Treat `003-inline-media` and `004-frontend-formatting` as recent feature areas.
- When you work on inline media, account for filesystem-backed archive media exposed by the API and rendered through the frontend transcript pipeline.
- When you work on frontend formatting, account for the backend `segments` pipeline and the possible use of `react-markdown` and `remark-breaks` for safe markdown rendering.

## Skill Guidance

Use skills only for tasks that benefit from a specialized workflow. Prefer ordinary implementation flow for normal feature work, bug fixes, refactors, tests, and backend or API changes.

Use these skills when the task clearly matches:

- Use `frontend-design` for new pages, major UI redesigns, or distinctive frontend components.
- Use `adapt` for responsive behavior, mobile layout fixes, and cross-screen adjustments.
- Use `animate` for purposeful motion, interaction polish, and transitions.
- Use `clarify` for UX copy, labels, empty states, errors, and onboarding text.
- Use `harden` for edge cases, error handling, overflow, and resilience work in the UI.
- Use `optimize` for frontend performance, rendering cost, loading behavior, and bundle concerns.
- Use `audit` for broad interface reviews across accessibility, responsiveness, theming, or quality.
- Use `polish`, `normalize`, `extract`, `colorize`, `bolder`, `quieter`, `distill`, `delight`, and `onboard` only when the task explicitly asks for that kind of design refinement.
- Use `summarize-github-issue-pr-notification`, `suggest-fix-issue`, `address-pr-comments`, and `create-pull-request` for GitHub issue and pull request workflows.
- Use `find-skills` when the user asks whether a skill exists for a task.

Do not reach for a skill when ordinary repository guidance is enough.

## Agent Guidance

Apply these rules when you use specialized agent instructions:

- Pick the matching instruction file from `.github/agents/` only when a task calls for a specialized agent workflow.
- Treat generated or workflow-specific instruction files as supplemental context unless the task explicitly belongs to that workflow.
- Update this file when shared repository guidance changes. Do not duplicate repository-wide guidance across multiple instruction files.

## Quick Reference

Use these common commands when you need broad validation:

```bash
# All tests at once
source .venv/bin/activate && pytest api/tests/ -v && cd web && npm test

# Coverage
source .venv/bin/activate && pytest api/tests/ --cov=api --cov-report=term-missing
cd web && npm test -- --coverage
```
