# Tasks: Browse Chats by Date

**Input**: Design documents from `/specs/005-browse-by-date/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, quickstart.md ✓, contracts/date-browsing.openapi.yaml ✓

**Tests**: Tests are first-class tasks for this feature. For each slice, write the failing test first, implement until it passes, then keep the broader validation tasks in the final phase.

**Organization**: Tasks grouped by user story for independent implementation

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1-US4) - Setup/Foundational/Polish phases have no story label
- Task IDs are stable references; tasks may appear in dependency order instead of strict numeric order within a phase
- Task IDs may include suffix letters when a test-first task is inserted without renumbering later tasks
- Exact file paths included in descriptions

## TDD Guardrails

- Add or update the narrowest failing test before changing production code for a task
- Keep backend query and router behavior covered in pytest before wiring the frontend
- Cover frontend state and rendering in Vitest before relying on end-to-end checks
- Use Playwright to lock the user-visible flow only after the underlying unit/integration tests exist
- Do not mark a task complete until its new or updated tests pass locally

---

## Phase 1: Setup

**Purpose**: Expose the new date mode in the existing web shell and establish the route/file surfaces the feature will use.

- [ ] T001 Add a separate date-browsing navigation entry in web/src/components/layout/Sidebar.tsx
- [ ] T002 Create the separate date-browsing page scaffold in web/src/app/date/page.tsx
- [ ] T003 [P] Define date-browsing frontend models and expanded date sort enums in web/src/types/index.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared API, query, storage, and CLI primitives that all user stories rely on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004a Add failing backend contract tests for calendar params, date-sort validation, and response shapes in api/tests/test_conversations.py, api/tests/test_search.py, tests/integration/test_api_conversations.py, and tests/integration/test_api_search.py
- [ ] T004 Extend date-aware request models for calendar params and search sort fields in api/models/requests.py
- [ ] T005 [P] Extend response models for calendar periods, day buckets, unknown-date groups, and updated search metadata in api/models/responses.py
- [ ] T006 [P] Extend shared sort validation to accept initiated_date and updated_date in api/middleware/validation.py and router allow-lists
- [ ] T007 [P] Add date-browsing query keys in web/src/hooks/queryKeys.ts
- [ ] T008a [P] Add failing frontend service and request-mapping tests for timezone propagation and date-browse query keys in web/__tests__/services/api.test.ts, web/__tests__/mocks/handlers.ts, and new web/__tests__/hooks/useDateBrowse.test.ts
- [ ] T008 [P] Capture the viewer's IANA timezone in the web client and centralize date-browsing request mapping in web/src/lib/timezone.ts and web/src/services/api.ts
- [ ] T009 [P] Add date-browsing API client methods and date-sort request mapping in web/src/services/api.ts
- [ ] T010 Add update-time sort index coverage for date browsing in chatgpt_archive/db.py
- [ ] T011a Add failing shared-library tests for timezone bucketing, updated-date ordering, unknown-date grouping, and deterministic pagination in tests/unit/test_search.py and tests/test_cli.py
- [ ] T011 Implement timezone-aware initiated-date bucketing, updated-date sorting, and unknown-date query helpers in chatgpt_archive/search.py
- [ ] T012 Implement date-browsing service adapters and sort alias handling in api/services/archive_service.py
- [ ] T013 Add CLI subcommands or flags for date browsing and date-based sorting in chatgpt_archive/cli.py
- [ ] T014 Implement deterministic ordering and pagination for day-detail and unknown-date result sets in chatgpt_archive/search.py and api/services/archive_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Browse Chats on a Calendar (Priority: P1) 🎯 MVP

**Goal**: Deliver a separate calendar-style date-browsing mode that shows dated conversation buckets and an explicit unknown-date group.

**Independent Test**: Open the date-browsing mode, select a day with known conversations, verify that dated results and the unknown-date group are both reachable without entering a keyword query, and confirm returning to the broader browsing surface preserves orientation.

### Implementation for User Story 1

- [ ] T015a [US1] Add failing API and integration tests for calendar, by-date, and unknown-date endpoints in api/tests/test_conversations.py and tests/integration/test_api_conversations.py
- [ ] T015 [US1] Add calendar, by-date, and unknown-date endpoints to api/routers/conversations.py
- [ ] T016a [P] [US1] Add failing hook and component tests for date-browse loading, day selection, unknown-date access, and conversation-open affordances in new web/__tests__/hooks/useDateBrowse.test.ts, new web/__tests__/components/DateBrowseCalendar.test.tsx, and new web/__tests__/components/DateBrowseResults.test.tsx
- [ ] T016 [P] [US1] Create the date-browse hook for calendar, day, and unknown-date queries in web/src/hooks/useDateBrowse.ts
- [ ] T017 [P] [US1] Create the calendar month/week view component in web/src/components/search/DateBrowseCalendar.tsx
- [ ] T018 [P] [US1] Create the date result list and unknown-date group component, including conversation-open affordances, in web/src/components/search/DateBrowseResults.tsx
- [ ] T019 [US1] Export date-browse UI components in web/src/components/search/index.ts
- [ ] T020a [US1] Add failing Playwright coverage for entering date mode, opening a day result, reaching the unknown-date group, and returning to the broader browse flow in new web/__tests__/e2e/date-browse.spec.ts
- [ ] T020 [US1] Compose the dedicated /date browsing mode, make the unknown-date group reachable, and preserve the last broader browsing destination in web/src/app/date/page.tsx and web/src/components/layout/Sidebar.tsx

**Checkpoint**: User Story 1 should provide a usable calendar-style browse mode on its own and return to the prior broader browsing surface without losing orientation

---

## Phase 4: User Story 2 - Narrow to a Time Window (Priority: P2)

**Goal**: Let users constrain calendar browsing to a selected date range and handle empty ranges clearly.

**Independent Test**: Apply a start date and end date in date mode and verify that only matching initiated-date conversations remain visible while empty ranges show a clear recovery path.

### Implementation for User Story 2

- [ ] T021a [US2] Add failing API and integration tests for invalid ranges, constrained calendar buckets, constrained day results, and empty-range behavior in api/tests/test_conversations.py and tests/integration/test_api_conversations.py
- [ ] T021 [US2] Reject invalid or reversed date ranges in the calendar endpoints in api/routers/conversations.py
- [ ] T022a [P] [US2] Add failing frontend tests for range input state, reset behavior, and empty-state recovery messaging in new web/__tests__/components/DateBrowseRangeFilter.test.tsx and new web/__tests__/hooks/useDateBrowse.test.ts
- [ ] T022 [US2] Extend initiated-date queries with range-constrained calendar buckets and day results in chatgpt_archive/search.py
- [ ] T023 [US2] Propagate range filters through date-browsing service methods in api/services/archive_service.py
- [ ] T024 [P] [US2] Create range filter controls for date mode in web/src/components/search/DateBrowseRangeFilter.tsx
- [ ] T025 [US2] Export date range controls in web/src/components/search/index.ts
- [ ] T026 [US2] Wire range state, reset behavior, and explicit empty-state recovery messaging into web/src/app/date/page.tsx

**Checkpoint**: User Stories 1 and 2 should support approximate-timeframe discovery without keyword search

---

## Phase 5: User Story 3 - Order Other Search Results by Date (Priority: P3)

**Goal**: Add initiated-date and last-updated ordering to the existing conversation list and search views outside the dedicated date mode.

**Independent Test**: In the conversation list and search pages, switch between initiated-date and last-updated sorting and verify that results reorder correctly without changing the active mode.

### Implementation for User Story 3

- [ ] T027a [US3] Add failing API and integration tests for initiated-date and updated-date ordering in api/tests/test_search.py, api/tests/test_conversations.py, tests/integration/test_api_search.py, and tests/integration/test_api_conversations.py
- [ ] T027 [US3] Accept initiated-date and updated-date ordering in api/routers/search.py
- [ ] T028 [US3] Accept initiated-date and updated-date ordering in api/routers/conversations.py
- [ ] T029 [US3] Extend non-date sort execution for initiated-date and updated-date ordering in api/services/archive_service.py
- [ ] T030a [P] [US3] Add failing hook, service, and page tests for date-sort labels and request propagation in web/__tests__/hooks/useSearch.test.ts, web/__tests__/hooks/useConversations.test.ts, web/__tests__/services/api.test.ts, and new web/__tests__/components/DateSortControls.test.tsx
- [ ] T030 [P] [US3] Update search hook request state for initiated-date and updated-date ordering in web/src/hooks/useSearch.ts
- [ ] T031 [P] [US3] Update conversation list hook sort options for initiated-date and updated-date ordering in web/src/hooks/useConversations.ts
- [ ] T032a [US3] Add failing Playwright coverage for initiated-date and updated-date sorting in web/__tests__/e2e/home.spec.ts and web/__tests__/e2e/search.spec.ts
- [ ] T032 [US3] Add clearly labeled initiated-date and updated-date sort controls to the conversation list page in web/src/app/page.tsx
- [ ] T033 [US3] Add clearly labeled initiated-date and updated-date sort controls to the search page in web/src/app/search/page.tsx

**Checkpoint**: User Story 3 should improve date-based discovery even when users stay in existing non-date modes

---

## Phase 6: User Story 4 - Move Between Nearby Dates (Priority: P4)

**Goal**: Support adjacent period navigation while preserving the user’s selected date-range context in date mode.

**Independent Test**: Navigate to the previous and next month or week from the date-browsing mode and verify that the selected context updates correctly while any active range filter is preserved.

### Implementation for User Story 4

- [ ] T034a [US4] Add failing API and integration tests for adjacent period navigation and preserved range context in api/tests/test_conversations.py and tests/integration/test_api_conversations.py
- [ ] T034 [US4] Add adjacent period calculation and preserved selected-day metadata to calendar queries in chatgpt_archive/search.py
- [ ] T035 [US4] Expose previous and next period navigation through date-browsing service methods in api/services/archive_service.py
- [ ] T036 [US4] Accept adjacent period navigation inputs in api/routers/conversations.py
- [ ] T037a [P] [US4] Add failing component and end-to-end tests for previous and next period navigation with preserved range state in new web/__tests__/components/DateBrowsePeriodNav.test.tsx and new web/__tests__/e2e/date-browse.spec.ts
- [ ] T037 [P] [US4] Create previous and next period navigation controls in web/src/components/search/DateBrowsePeriodNav.tsx
- [ ] T038 [US4] Export period navigation controls in web/src/components/search/index.ts
- [ ] T039 [US4] Wire adjacent navigation and preserved range context into web/src/app/date/page.tsx

**Checkpoint**: All user stories should now be independently usable and cumulatively support full date-based discovery

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Align docs and validate the implemented API and web workflows while confirming the CLI surface remains usable and documented.

- [ ] T040 [P] Update API documentation for calendar and date sort endpoints in docs/API.md
- [ ] T041 [P] Update CLI and product overview documentation for date browsing in README.md
- [ ] T042 [P] Update command and usage references for date browse and date sort options in docs/USAGE.md
- [ ] T043 Run the manual API and web validation flow in specs/005-browse-by-date/quickstart.md, including unknown-date access and return-to-browse behavior
- [ ] T044 Run CLI smoke checks for date-browse and date-sort commands and record the exact working invocations in docs/USAGE.md
- [ ] T045 Run the focused backend, frontend, and end-to-end commands listed in specs/005-browse-by-date/quickstart.md and record pass/fail results alongside any follow-up notes
- [ ] T046 Measure date-period query time, day-detail query time, and adjacent-period navigation responsiveness against the thresholds in specs/005-browse-by-date/plan.md, and record the results in specs/005-browse-by-date/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 because range narrowing extends the date mode
- **User Story 3 (Phase 5)**: Depends on Foundational completion and can proceed independently of User Story 2
- **User Story 4 (Phase 6)**: Depends on User Story 1 and User Story 2 because adjacent navigation must preserve date-mode and range context
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational - establishes the separate date mode
- **US2 (P2)**: Starts after US1 - extends the date mode with range narrowing
- **US3 (P3)**: Starts after Foundational - extends existing non-date search/list views
- **US4 (P4)**: Starts after US1 and US2 - builds adjacent navigation on top of date mode state

### Dependency Graph

```text
Phase 1 Setup
    ↓
Phase 2 Foundational
    ↓
 ┌───────┴────────┐
 ↓                ↓
US1              US3
 ↓
US2
 ↓
US4
    ↓
Phase 7 Polish
```

### Within Each User Story

- Add the narrowest failing tests before the production task they cover
- Shared query/service work before router exposure when a story touches both layers
- Router and API client work before page composition
- Components before page integration
- End-to-end coverage after the underlying pytest and Vitest slices are already passing
- Each story should be validated at its checkpoint before moving to the next dependent story, and the final phase should capture the exact validation evidence and command outcomes

---

## Parallel Examples

### Parallel Example: User Story 1

```text
T016 [US1] Create the date-browse hook in web/src/hooks/useDateBrowse.ts
T017 [US1] Create the calendar month/week view component in web/src/components/search/DateBrowseCalendar.tsx
T018 [US1] Create the date result list and unknown-date group component in web/src/components/search/DateBrowseResults.tsx
```

### Parallel Example: User Story 2

```text
T022 [US2] Extend initiated-date queries in chatgpt_archive/search.py
T024 [US2] Create range filter controls in web/src/components/search/DateBrowseRangeFilter.tsx
```

### Parallel Example: User Story 3

```text
T030 [US3] Update search hook request state in web/src/hooks/useSearch.ts
T031 [US3] Update conversation list hook sort options in web/src/hooks/useConversations.ts
```

### Parallel Example: User Story 4

```text
T035 [US4] Expose previous and next period navigation in api/services/archive_service.py
T037 [US4] Create period navigation controls in web/src/components/search/DateBrowsePeriodNav.tsx
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Confirm the separate date mode can open a conversation from a selected day and surface the unknown-date group
5. Demo the MVP before layering on range filters, non-date sort expansion, and adjacent navigation

### Incremental Delivery

1. Setup + Foundational establish the reusable date semantics across CLI, API, and web
2. Add User Story 1 to deliver the first user-visible date-browsing workflow
3. Add User Story 2 to make approximate timeframe discovery practical
4. Add User Story 3 to improve date-based discovery in existing search/list screens
5. Add User Story 4 to complete adjacent period exploration and context preservation
6. Finish with documentation and quickstart validation

### Parallel Team Strategy

1. One developer can complete backend shared date semantics while another prepares the date-mode UI shell during Setup/Foundational work
2. After Foundational completion, one developer can own US1 while another starts US3 because it does not depend on date-mode range work
3. Once US1 lands, US2 and then US4 can layer on the date-mode experience without blocking the already-independent non-date sort improvements

---

## Notes

- [P] tasks touch different files and can be worked concurrently
- All tasks use exact file paths so they are directly executable
- TDD is the default approach for this feature: fail a narrow test first, implement, then widen validation at the checkpoint and final phase
