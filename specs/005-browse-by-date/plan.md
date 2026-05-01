# Implementation Plan: Browse Chats by Date

**Branch**: `005-browse-by-date` | **Date**: 2026-05-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-browse-by-date/spec.md`

## Summary

Add a separate date-browsing mode to the existing web archive experience, backed by FastAPI read endpoints and shared archive query logic that group conversations by initiated date in the viewer's local timezone. The implementation also extends existing search and conversation-list flows so non-date modes can order results by initiated date or last updated date, while conversations without usable initiated timestamps remain reachable through an explicit unknown-date group.

## Technical Context

**Language/Version**: Python 3.11 for API backend, Python 3.10+ for shared library, TypeScript 5 with React 19 / Next.js 16 for frontend  
**Primary Dependencies**: FastAPI, Pydantic 2, sqlite3/FTS5, React Query, date-fns, react-day-picker, shadcn/ui  
**Storage**: Existing SQLite archive database in `chatgpt_archive/db.py`; no new persistence store required  
**Testing**: pytest (`tests/`, `api/tests/`), Vitest + Testing Library (`web/__tests__/`), Playwright (`web/__tests__/e2e/`)  
**Target Platform**: Local-first web app on macOS/Linux/Windows browsers with FastAPI backend  
**Project Type**: web application with shared Python library + API + Next.js frontend  
**Performance Goals**: Date-period and day-detail queries under 500ms for typical local archives; adjacent-period navigation updates under 2s; preserve existing search responsiveness  
**Constraints**: Archive remains source of truth, SQLite stays single-file, underlying date access must remain available to CLI/library surfaces, initiated date is canonical for calendar placement, day boundaries use viewer local timezone, unknown dates must not be inferred  
**Scale/Scope**: Single-user local archives with thousands of conversations, month/week calendar periods, paginated day-detail and unknown-date result sets

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| I. Data-First | Archive remains canonical, DB is derived | ✅ PASS | Uses existing `create_time`/`update_time`; no archive mutation or inferred source data |
| II. CLI-First | Core capability accessible outside GUI | ✅ PASS | Date grouping and date-sort primitives will live in shared Python query logic and remain available to CLI/library flows even though the calendar presentation is web-only |
| III. Fast Search & Retrieval | Preserve fast local retrieval | ✅ PASS | Reuses indexed conversation timestamps and paginated queries; no query-time reindexing |
| IV. Format-Agnostic Export | Do not break export surfaces | ✅ PASS | Feature is read-only and does not alter export contracts or stored conversation payloads |
| V. Simplicity & Composability | Prefer existing stack and minimal complexity | ✅ PASS | Reuses current FastAPI, Next.js, React Query, and `react-day-picker`; no new datastore or service |
| Data Integrity | Preserve IDs and avoid misleading data placement | ✅ PASS | Unknown initiated dates are isolated in an explicit unknown-date group rather than guessed |

**Gate Result**: ✅ ALL PASS - Proceed to Phase 0 and Phase 1 design

## Project Structure

### Documentation (this feature)

```text
specs/005-browse-by-date/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── date-browsing.openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
chatgpt_archive/
├── cli.py
├── db.py
├── search.py
└── models.py

api/
├── main.py
├── models/
│   ├── requests.py
│   └── responses.py
├── routers/
│   ├── conversations.py
│   └── search.py
├── services/
│   └── archive_service.py
└── tests/
    ├── test_conversations.py
    └── test_search.py

web/
├── src/
│   ├── app/
│   │   ├── page.tsx
│   │   └── search/page.tsx
│   ├── components/
│   │   ├── conversations/
│   │   └── search/
│   ├── hooks/
│   │   ├── queryKeys.ts
│   │   ├── useConversations.ts
│   │   └── useSearch.ts
│   ├── services/api.ts
│   └── types/index.ts
└── __tests__/
    ├── components/
    ├── hooks/
    ├── services/
    └── e2e/
```

**Structure Decision**: Keep the existing three-layer layout: shared Python archive queries in `chatgpt_archive/`, API orchestration in `api/`, and UI state/rendering in `web/`. This satisfies Constitution Principles I, II, and V by centralizing date semantics once and reusing them across CLI/library, API, and web surfaces.

## Phase 0 Research Highlights

- Reuse `react-day-picker` and `date-fns` already present in the frontend rather than introducing a new calendar library.
- Compute calendar buckets server-side from conversation timestamps using a viewer-supplied IANA timezone, so day grouping, filtering, pagination, and unknown-date handling are consistent across clients.
- Introduce dedicated calendar read endpoints while extending existing list/search sorting contracts for initiated-date and updated-date ordering.
- Keep initiated date as the only calendar-placement basis; reserve updated date for sort order only in non-date browsing modes.
- Treat missing initiated timestamps as explicit unknown-date results instead of inferring from updated timestamps.

## Post-Design Constitution Check

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| I. Data-First | Archive remains canonical, DB is derived | ✅ PASS | Design uses existing conversation timestamps and derived calendar buckets only |
| II. CLI-First | Core capability accessible outside GUI | ✅ PASS | Shared query layer can back CLI list/search enhancements without duplicating web logic |
| III. Fast Search & Retrieval | Preserve fast local retrieval | ✅ PASS | Calendar summaries use timestamp-bounded SQL queries and paginated detail endpoints |
| IV. Format-Agnostic Export | Do not break export surfaces | ✅ PASS | Contracts are additive and read-only |
| V. Simplicity & Composability | Prefer existing stack and minimal complexity | ✅ PASS | No new infra, no new persistence model, no new frontend state framework |
| Data Integrity | Preserve IDs and avoid misleading data placement | ✅ PASS | Unknown-date group and explicit timezone semantics prevent silent data distortion |

**Post-Design Gate Result**: ✅ ALL PASS - Ready for `/speckit.tasks`

## Complexity Tracking

> No constitutional violations require special justification.

| Aspect | Decision | Justification |
|--------|----------|---------------|
| Calendar UI | Reuse `react-day-picker` | Already installed, accessible, and adequate for month/day selection |
| Date grouping | Server-side bucketing with timezone input | Keeps grouping consistent across web and CLI/API consumers |
| Missing dates | Explicit unknown-date group | Avoids misleading inferred placement |
| Sort expansion | Extend existing list/search endpoints | Minimizes API surface churn while meeting the new behavior |
