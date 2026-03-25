# Tasks: Frontend Formatting

**Input**: Design documents from `/specs/004-frontend-formatting/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/message-rendering-api.yaml`, `quickstart.md`

**Tests**: Tests are included because the feature spec explicitly requires acceptance validation for formatted markdown, structured payload rendering, and graceful fallback behavior.

**Organization**: Tasks are grouped by setup, shared foundations, and user story so each story can be implemented and validated independently once the blocking foundation is complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel when dependencies are satisfied and files do not overlap
- **[Story]**: Maps a task to a user story (`US1`, `US2`, `US3`)
- Every task below includes exact file paths

---

## Phase 1: Setup

**Purpose**: Prepare dependencies and reusable fixtures for the formatted transcript feature.

- [ ] T001 Add markdown rendering dependencies for the web app in `web/package.json`
- [ ] T002 [P] Add formatted-message fixture builders and mixed-content payload samples in `api/tests/conftest.py` and `web/__tests__/mocks/handlers.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared segment contract and rendering primitives required by all user stories.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [ ] T003 Extend message response models with `RenderSegment` support in `api/models/responses.py` and `web/src/types/index.ts`
- [ ] T004 [P] Create the segment-building service scaffold and parsing helpers in `api/services/formatting_service.py`
- [ ] T005 [P] Create reusable markdown and fallback rendering primitives in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/components/conversations/FallbackBlock.tsx`
- [ ] T006 Wire segment generation into conversation detail responses in `api/services/archive_service.py` and `api/routers/conversations.py`
- [ ] T007 [P] Extend API client handling for segmented messages in `web/src/services/api.ts` and `web/__tests__/services/api.test.ts`
- [ ] T008 [P] Add foundational contract coverage for segmented conversation responses in `api/tests/test_conversations.py` and `api/tests/test_formatting_service.py`

**Checkpoint**: The conversation API returns the new segment contract, and the web app has the shared components needed to render it.

---

## Phase 3: User Story 1 - Read Formatted Messages (Priority: P1) 🎯 MVP

**Goal**: Render markdown-style message content as formatted transcript content instead of raw markdown source.

**Independent Test**: Open a conversation containing headings, lists, emphasis, links, blockquotes, inline code, and fenced code blocks. The conversation view should render formatted content instead of literal markdown markers, and plain-text messages should remain readable.

### Tests for User Story 1

- [ ] T009 [P] [US1] Add backend contract and parser tests for supported markdown segmentation in `api/tests/test_conversations.py` and `api/tests/test_formatting_service.py`
- [ ] T010 [P] [US1] Add frontend markdown renderer tests for headings, lists, links, inline code, and fenced code blocks in `web/__tests__/components/MarkdownRenderer.test.tsx`

### Implementation for User Story 1

- [ ] T011 [US1] Implement markdown segment extraction for plain and mixed prose messages in `api/services/formatting_service.py`
- [ ] T012 [US1] Emit markdown segments for text-only and mixed-content messages in `api/services/archive_service.py`
- [ ] T013 [US1] Update the conversation bubble to render segment-first markdown content in `web/src/components/conversations/MessageBubble.tsx`
- [ ] T014 [US1] Add readable markdown presentation for code, quotes, lists, links, and mobile overflow in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/components/conversations/MessageBubble.tsx`
- [ ] T015 [P] [US1] Extend browser coverage for formatted markdown conversations in `web/__tests__/e2e/conversation.spec.ts`

**Checkpoint**: User Story 1 is independently functional and demonstrates formatted markdown without raw markdown markers.

---

## Phase 4: User Story 2 - Hide Raw Structured Payloads (Priority: P2)

**Goal**: Replace raw structured payload blobs with attachment UI or readable structured-content blocks while preserving prose order.

**Independent Test**: Open a conversation that currently shows raw asset-pointer dictionaries. The conversation view should replace those payloads with readable attachment or content blocks, and surrounding prose should remain in the correct order.

### Tests for User Story 2

- [ ] T016 [P] [US2] Add backend tests for asset-payload classification and prose-plus-attachment ordering in `api/tests/test_formatting_service.py` and `api/tests/test_conversations.py`
- [ ] T017 [P] [US2] Add frontend tests for attachment segments and hidden raw payloads in `web/__tests__/components/MessageBubble.test.tsx` and `web/__tests__/e2e/conversation.spec.ts`

### Implementation for User Story 2

- [ ] T018 [US2] Classify recognized structured asset payloads into attachment segments and transport-only rendering decisions in `api/services/formatting_service.py`
- [ ] T019 [US2] Align segment attachment indexes with the existing attachment extraction flow in `api/services/formatting_service.py` and `api/services/media_service.py`
- [ ] T020 [US2] Render attachment and structured fallback blocks inline with prose in `web/src/components/conversations/MessageBubble.tsx` and `web/src/components/conversations/FallbackBlock.tsx`
- [ ] T021 [US2] Add structured payload fixtures for API and browser tests in `api/tests/conftest.py` and `web/__tests__/mocks/handlers.ts`
- [ ] T022 [US2] Verify the segmented message response remains aligned with the API contract in `api/tests/test_conversations.py` and `web/__tests__/services/api.test.ts`

**Checkpoint**: User Stories 1 and 2 work independently, and supported structured payloads no longer leak into the transcript as raw dict-like text.

---

## Phase 5: User Story 3 - Graceful Rendering Fallbacks (Priority: P3)

**Goal**: Ensure malformed markdown, unsupported structured payloads, and incomplete attachment metadata degrade gracefully instead of breaking the transcript.

**Independent Test**: Open conversations with malformed markdown, unsupported structured payloads, or partial attachment metadata. The UI should show readable fallback blocks instead of blank sections, broken layout, or raw transport text.

### Tests for User Story 3

- [ ] T023 [P] [US3] Add backend tests for malformed markdown, unsupported payloads, and missing metadata fallbacks in `api/tests/test_formatting_service.py` and `api/tests/test_conversations.py`
- [ ] T024 [P] [US3] Add frontend tests for fallback labels, invalid attachment indexes, and oversized code block behavior in `web/__tests__/components/MessageBubble.test.tsx` and `web/__tests__/components/MarkdownRenderer.test.tsx`

### Implementation for User Story 3

- [ ] T025 [US3] Implement fallback segment generation for malformed or unsupported structured content in `api/services/formatting_service.py`
- [ ] T026 [US3] Guard attachment rendering against invalid indexes and incomplete metadata in `web/src/components/conversations/MessageBubble.tsx` and `web/src/components/conversations/FallbackBlock.tsx`
- [ ] T027 [US3] Add resilient rendering and overflow handling for malformed or oversized markdown blocks in `web/src/components/conversations/MarkdownRenderer.tsx`
- [ ] T028 [P] [US3] Extend Playwright coverage for malformed content and missing attachment metadata in `web/__tests__/e2e/conversation.spec.ts`

**Checkpoint**: All three user stories are independently functional, and the conversation view remains readable across malformed and legacy content.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish documentation, regression coverage, and implementation validation across stories.

- [ ] T029 [P] Document segmented conversation responses and fallback behavior in `docs/API.md` and `docs/REST-API.md`
- [ ] T030 [P] Document developer validation and troubleshooting for formatted transcripts in `README.md` and `docs/TROUBLESHOOTING.md`
- [ ] T031 Add regression coverage for the text-only fast path and mixed-content order preservation in `api/tests/test_conversations.py` and `web/__tests__/components/MessageBubble.test.tsx`
- [ ] T032 Run backend validation for `api/tests/test_conversations.py` and `api/tests/test_formatting_service.py`
- [ ] T033 Run frontend validation for `web/__tests__/services/api.test.ts`, `web/__tests__/components/MessageBubble.test.tsx`, `web/__tests__/components/MarkdownRenderer.test.tsx`, and `web/__tests__/e2e/conversation.spec.ts`
- [ ] T034 Run the end-to-end quickstart validation from `specs/004-frontend-formatting/quickstart.md` against representative markdown and structured payload conversations
- [ ] T035 Add source-parity fixtures and regression coverage for generated assistant content versus imported historical content in `api/tests/conftest.py`, `api/tests/test_formatting_service.py`, and `web/__tests__/mocks/handlers.ts`
- [ ] T036 Add backend and frontend tests for raw HTML and unsafe embedded-content payload handling in `api/tests/test_formatting_service.py`, `api/tests/test_conversations.py`, and `web/__tests__/components/MarkdownRenderer.test.tsx`
- [ ] T037 Configure markdown rendering and fallback handling so raw HTML and unsafe embedded content render as inert text or fallback blocks in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/components/conversations/FallbackBlock.tsx`
- [ ] T038 Extend browser coverage with explicit desktop and mobile viewport assertions for formatted transcript readability in `web/__tests__/e2e/conversation.spec.ts`
- [ ] T039 Update validation coverage and quickstart checks to include source-parity and unsafe-content scenarios in `web/__tests__/services/api.test.ts` and `specs/004-frontend-formatting/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKING
    ↓
┌───────────────┬───────────────┬───────────────┐
↓               ↓               ↓
US1             US2             US3
(P1)            (P2)            (P3)
↓               ↓               ↓
Phase 6 (Polish & Cross-Cutting Concerns)
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (Read Formatted Messages) | Foundational | Phase 2 complete |
| US2 (Hide Raw Structured Payloads) | Foundational | Phase 2 complete |
| US3 (Graceful Rendering Fallbacks) | Foundational | Phase 2 complete |

### Within Each User Story

- Story tests should be written first and should fail before implementation begins.
- Backend segment generation should land before frontend rendering changes that depend on the new segment shape.
- Frontend rendering updates should land before end-to-end validation for the same story.

### Parallel Opportunities

- T001 and T002 can run in parallel during Setup.
- T004, T005, T007, and T008 can run in parallel once T003 defines the shared segment contract.
- T009 and T010 can run in parallel for US1.
- T016 and T017 can run in parallel for US2.
- T023 and T024 can run in parallel for US3.
- T029 and T030 can run in parallel during Polish.
- T035 and T036 can run in parallel during Polish.
- T038 and T039 can run in parallel after the new security and parity coverage lands.

---

## Parallel Example: User Story 1

```text
Task: T009 Add backend contract and parser tests in api/tests/test_conversations.py and api/tests/test_formatting_service.py
Task: T010 Add frontend markdown renderer tests in web/__tests__/components/MarkdownRenderer.test.tsx
```

## Parallel Example: User Story 2

```text
Task: T016 Add backend asset-payload ordering tests in api/tests/test_formatting_service.py and api/tests/test_conversations.py
Task: T017 Add frontend attachment-segment tests in web/__tests__/components/MessageBubble.test.tsx and web/__tests__/e2e/conversation.spec.ts
```

## Parallel Example: User Story 3

```text
Task: T023 Add backend fallback tests in api/tests/test_formatting_service.py and api/tests/test_conversations.py
Task: T024 Add frontend fallback and overflow tests in web/__tests__/components/MessageBubble.test.tsx and web/__tests__/components/MarkdownRenderer.test.tsx
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Deliver User Story 1.
3. Validate formatted markdown rendering independently before moving to structured payload cleanup.

### Incremental Delivery

1. Finish shared segment infrastructure.
2. Add markdown rendering for US1 and validate plain-text compatibility.
3. Add structured payload cleanup for US2 and validate mixed prose-plus-attachment ordering.
4. Add resilient fallback behavior for US3 and validate malformed-content handling.
5. Finish with docs and full regression validation.

### Task Count Summary

- Total tasks: 39
- Setup: 2
- Foundational: 6
- US1: 7
- US2: 7
- US3: 6
- Polish & Cross-Cutting Concerns: 11

### Suggested MVP Scope

- Complete through Phase 3 (User Story 1) for the first delivery.

---

## Notes

- All task lines follow the required checklist format: checkbox, sequential ID, optional `[P]`, required story label inside user story phases, and exact file paths.
- User stories remain independently testable after the shared foundational phase.
- The live contract referenced by these tasks is `specs/004-frontend-formatting/contracts/message-rendering-api.yaml`.