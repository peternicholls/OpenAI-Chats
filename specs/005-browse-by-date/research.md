# Research: Browse Chats by Date

## Decision 1: Reuse the existing FastAPI + Next.js + shared-library architecture

- **Decision**: Implement date browsing through shared Python query helpers in `chatgpt_archive`, expose them through FastAPI routers, and consume them from the existing Next.js app.
- **Rationale**: The current codebase already separates shared archive logic, API transport, and web rendering. Reusing that structure preserves CLI-first parity, avoids duplicate date semantics, and keeps the date-browsing feature aligned with the existing search and conversation-list stack.
- **Alternatives considered**:
  - Build the feature entirely in the web client by fetching all conversations and grouping in-browser: rejected because it breaks consistency, scales poorly for large local archives, and bypasses CLI/API reuse.
  - Implement the feature only in the API layer: rejected because the shared library is the correct place for timestamp rules that must be reused outside the web UI.

## Decision 2: Use `react-day-picker` and `date-fns` for the calendar UI

- **Decision**: Build the separate date-browsing mode with the already-installed `react-day-picker` and `date-fns` packages.
- **Rationale**: Both dependencies are already present in `web/package.json`, so the feature can ship without introducing a new calendar dependency or a second date utility stack. This keeps the frontend implementation consistent with existing React 19 / Next.js 16 patterns and reduces styling/integration risk.
- **Alternatives considered**:
  - Create a custom calendar grid from scratch: rejected because it adds avoidable UI complexity and accessibility risk.
  - Add a different calendar library: rejected because the repo already has a suitable dependency.

## Decision 3: Compute day buckets server-side using the viewer's IANA timezone

- **Decision**: Send the viewer's local timezone from the client and compute initiated-date and updated-date boundaries on the backend with Python's standard `zoneinfo` support.
- **Rationale**: The spec requires local-timezone day boundaries. Server-side bucketing ensures that calendar cells, unknown-date handling, date-range filtering, and paginated day-detail results all use one consistent interpretation of time.
- **Alternatives considered**:
  - Compute buckets in the browser: rejected because pagination and unknown-date grouping would diverge from API results.
  - Use UTC for all bucketing: rejected because the user explicitly chose viewer-local semantics.

## Decision 4: Add dedicated calendar endpoints and extend existing search/list sorting

- **Decision**: Introduce dedicated read endpoints for calendar summaries and day-detail retrieval, while extending `GET /api/conversations` and `POST /api/search` to support initiated-date and last-updated-date ordering.
- **Rationale**: The feature needs both a separate date-browsing mode and cross-mode date ordering. Dedicated calendar endpoints keep the calendar payload compact and purpose-built, while additive sort parameters preserve existing search and list integrations.
- **Alternatives considered**:
  - Force all date browsing through the existing `POST /api/search` endpoint: rejected because keyword search semantics and calendar summary semantics are different.
  - Create an entirely separate search subsystem: rejected because the existing list/search routes already own adjacent behavior.

## Decision 5: Keep initiated date canonical for calendar placement; use updated date only for sorting elsewhere

- **Decision**: Calendar placement always uses conversation initiated date, while non-date modes may order by either initiated date or last updated date.
- **Rationale**: This matches the clarified spec and gives the calendar a stable, predictable placement rule. Updated date remains available where recency ordering is useful without causing calendar cells to shift.
- **Alternatives considered**:
  - Allow updated date to move conversations between calendar days: rejected because it makes the calendar unstable and harder to browse.
  - Support only one date field everywhere: rejected because the user explicitly wants both initiated and updated ordering in other modes.

## Decision 6: Represent missing initiated dates as an explicit unknown-date group

- **Decision**: Conversations without usable initiated timestamps appear in a dedicated unknown-date group and never receive inferred calendar placement.
- **Rationale**: The constitution emphasizes data integrity, and the spec explicitly rejects misleading placement. An explicit unknown-date group preserves access without inventing dates.
- **Alternatives considered**:
  - Infer initiated date from last updated date: rejected because it changes the meaning of the data.
  - Exclude such conversations entirely: rejected because it hides valid archive content from the user.

## Decision 7: Preserve CLI-first parity through shared query primitives and CLI-facing sort/date options

- **Decision**: The same shared query logic that powers the web calendar should also back CLI/library access to initiated-date filtering, updated-date ordering, and grouped date summaries.
- **Rationale**: The constitution requires CLI-first capability. Even though the calendar visualization is web-specific, the underlying browse-by-date operations must remain accessible from the non-GUI surfaces.
- **Alternatives considered**:
  - Treat date browsing as a UI-only exception: rejected because it would violate the project constitution.
  - Build a second, CLI-only implementation path: rejected because it duplicates the date semantics and increases maintenance cost.
