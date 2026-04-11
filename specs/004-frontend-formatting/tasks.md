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

- [ ] T001 Add markdown and math rendering dependencies for the web app in `web/package.json`: `react-markdown`, `remark-breaks`, `remark-math`, `rehype-katex`, and `katex`
- [ ] T002 [P] Add formatted-message fixture builders and mixed-content payload samples in `api/tests/conftest.py` and `web/__tests__/mocks/handlers.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared segment contract and rendering primitives required by all user stories.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [ ] T003 Extend message response models with `RenderSegment` support in `api/models/responses.py` and `web/src/types/index.ts` to match the per-kind `oneOf` schema already defined in `specs/004-frontend-formatting/contracts/message-rendering-api.yaml` (`MarkdownSegment`, `AttachmentSegment`, `FallbackSegment`)
- [ ] T004 [P] Create the segment-building service scaffold and parsing helpers in `api/services/formatting_service.py`
- [ ] T005 [P] Create reusable markdown and fallback rendering primitives in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/components/conversations/FallbackBlock.tsx`; configure `react-markdown` without `rehype-raw` from creation — safe rendering is a creation-time requirement, not a Phase 6 retrofit
- [ ] T005a [P] Create `web/src/components/conversations/ThinkingBlock.tsx`: a collapsible block component that accepts `activityType: 'reasoning' | 'search' | 'both'` and renders a collapsed pill labelled "Reasoning", "Searched the web", or "Reasoning and web search" respectively; when expanded, shows a disclosure note that detailed content is not available in this export format; default state is collapsed; add basic tests in `web/__tests__/components/ThinkingBlock.test.tsx` covering each activity type label and the expand/collapse toggle; **can run in parallel with T004, T007, T008 after T003**
- [ ] T005b [P] Create `web/src/components/conversations/DateSeparator.tsx`: a presentational component that accepts a `date: Date` prop and renders a subtle centred date label (e.g. "Saturday 15 January 2026") as a horizontal divider between message groups; add basic tests in `web/__tests__/components/DateSeparator.test.tsx` asserting the formatted date string is rendered; **can run in parallel with T005a**
- [ ] T005c [P] Create `web/src/components/conversations/ImageModal.tsx`: a modal overlay component that accepts an `attachment: Attachment` and `src: string` prop plus an `onClose` callback; renders the full-size image, filename, available metadata (dimensions, size, MIME type), a download link, and a close button; dismisses on backdrop click, close-button click, or Escape key; uses `createPortal` to mount at `document.body` (avoids stacking-context clipping inside message bubbles); update `web/src/components/conversations/AttachmentImage.tsx` to show a fixed-size thumbnail (`h-32 w-48 object-cover`) instead of a full-size image, and open `ImageModal` on click; add tests in `web/__tests__/components/ImageModal.test.tsx` covering: modal opens on thumbnail click, close button dismisses it, backdrop click dismisses it, Escape dismisses it, download link has correct `href` and `download` attributes, metadata fields render when present, metadata fields are absent when values are null; **can run in parallel with T005a, T005b**
- [ ] T006 Wire segment generation into conversation detail responses in `api/services/archive_service.py` and `api/routers/conversations.py`
- [ ] T006a Implement internal processing turn handling in `api/services/archive_service.py` (FR-015, FR-016): (1) suppress nodes where `is_hidden = 1` (already done by DB query; verify still applies); (2) suppress empty assistant bootstrap nodes (`author_role = 'assistant'`, `content_type = 'text'`, `content` null/empty); (3) for each remaining cluster of consecutive processing turns (`content_type IN ('thoughts', 'reasoning_recap')`, `author_role = 'assistant' AND content_type = 'code'`, `author_role = 'tool'` with empty content) within a response exchange, produce a single `ThinkingSegment` with `activity_type` set to `'reasoning'` (only `thoughts`/`reasoning_recap` present), `'search'` (only search `code`/`tool` present), or `'both'` (mixed); attach the `ThinkingSegment` as the first segment of the subsequent user-visible assistant message; add test coverage in `api/tests/test_conversations.py` asserting each suppressed bootstrap/hidden type produces no segment, each thinking cluster produces exactly one `ThinkingSegment` with correct `activity_type`, and user-visible messages pass through unmodified; **depends on T006**
- [ ] T006b Fix the message count query in `api/services/archive_service.py` (FR-020): update the `COUNT(*)` subquery (or equivalent) used to populate the message count in `ConversationDetail` so it counts only user-visible messages — nodes that would produce at least one render segment after applying the same suppression predicate used in T006a (i.e. exclude `is_hidden = 1` nodes, empty bootstrap assistant nodes, and pure processing turn nodes); add a test in `api/tests/test_conversations.py` asserting the returned count for a fixture conversation matches the number of user-visible messages and is lower than the raw DB row count when processing turns are present; **can run in parallel with T006a after T006**
- [ ] T007 [P] Extend API client handling for segmented messages in `web/src/services/api.ts` and `web/__tests__/services/api.test.ts`
- [ ] T008 [P] Add foundational contract coverage for segmented conversation responses in `api/tests/test_conversations.py` and `api/tests/test_formatting_service.py`; include assertions that: hidden nodes (`is_hidden=1`) produce zero segments; empty bootstrap assistant nodes produce zero segments; reasoning/search clusters produce exactly one `ThinkingSegment` with correct `activity_type`; user-visible text messages produce at least one `MarkdownSegment`; **can run in parallel with T004, T005, T007 after T003**

**Checkpoint**: The conversation API returns the new segment contract, and the web app has the shared components needed to render it.

---

## Phase 3: User Story 1 - Read Formatted Messages (Priority: P1) 🎯 MVP

**Goal**: Render markdown-style message content as formatted transcript content instead of raw markdown source.

**Independent Test**: Open a conversation containing headings, lists, emphasis, links, blockquotes, inline code, and fenced code blocks. The conversation view should render formatted content instead of literal markdown markers, and plain-text messages should remain readable.

### Tests for User Story 1

- [ ] T009 [P] [US1] Add backend contract and parser tests for supported markdown segmentation in `api/tests/test_conversations.py` and `api/tests/test_formatting_service.py`; include an explicit assertion that segment `text` values containing backslash sequences (e.g. `\[`, `\(`, `\prod`) are stored and returned verbatim without double-escaping or stripping
- [ ] T010 [P] [US1] Add frontend renderer and fallback component tests for headings, lists, links, inline code, fenced code blocks, fallback label rendering, display math (`\[...\]`), inline math (`\(...\)`), citation token stripping, and `ThinkingBlock` variants in `web/__tests__/components/MarkdownRenderer.test.tsx`, `web/__tests__/components/FallbackBlock.test.tsx`, and `web/__tests__/components/ThinkingBlock.test.tsx`; include the Erdős–Graham sample from the real archive as a regression fixture; include a fixture with `\uE200cite\uE202turn0search3\uE201` tokens asserting they are absent from rendered output and surrounding prose is preserved; include fixtures for each `activityType` value of `ThinkingBlock`

### Implementation for User Story 1

- [ ] T011 [US1] Implement markdown segment extraction for plain and mixed prose messages in `api/services/formatting_service.py`
- [ ] T012 [US1] Emit markdown segments for text-only and mixed-content messages in `api/services/archive_service.py`
- [ ] T013 [US1] Update the conversation bubble to render segment-first content, including `ThinkingBlock` segments, in `web/src/components/conversations/MessageBubble.tsx`
- [ ] T013a [US1] Integrate date-related display improvements into the conversation view: (1) update the conversation detail header component to show start date only (no time) and additionally show "Updated [date]" when `update_time` falls on a different calendar date than `create_time` (FR-018); (2) update the conversation transcript component that renders the message list to insert `DateSeparator` between consecutive rendered messages when their `create_time` dates fall on different calendar days (FR-019); add `DateSeparator.test.tsx` fixture assertions that cover the date-change boundary condition and the no-separator-before-first-message rule (SC-011); **depends on T005b**
- [ ] T014 [US1] Add readable markdown presentation for code, quotes, lists, links, and mobile overflow in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/components/conversations/MessageBubble.tsx`
- [ ] T014a [US1] Add KaTeX math rendering to `web/src/components/conversations/MarkdownRenderer.tsx`: add `remark-math` and `rehype-katex` to the existing `react-markdown` pipeline; add a pre-processing function that normalises `\[...\]` → `$$...$$` and `\(...\)` → `$...$` before parsing; import KaTeX CSS in `web/src/app/layout.tsx`; add KaTeX test fixtures to `web/__tests__/components/MarkdownRenderer.test.tsx` (display math, inline math, math mixed with prose); wrap KaTeX render calls so `\begin{...}...\end{...}` blocks that generate a parse error are caught and emitted as labeled fallback text rather than crashing or displaying blank output
- [ ] T014b [US1] Add citation token stripping to the pre-processing step in `web/src/components/conversations/MarkdownRenderer.tsx`: remove PUA sequences matching `\uE200(file)?cite(\uE202turnN(search|view|file)M)+\uE201` before the markdown pipeline; add test fixtures to `web/__tests__/components/MarkdownRenderer.test.tsx` asserting tokens are absent from rendered output and surrounding prose is preserved (use the `\uE200cite\uE202turn2view0\uE201` and `\uE200filecite\uE202turn0file0\uE201` variants from the real archive)
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
- [ ] T020 [US2] Render attachment and structured fallback blocks inline with prose in `web/src/components/conversations/MessageBubble.tsx` and `web/src/components/conversations/FallbackBlock.tsx`; image attachments MUST use the thumbnail-and-modal pattern from T005c rather than a full-size inline render (FR-021)
- [ ] T021 [US2] Extend the T002 fixtures with structured payload samples (asset-pointer dicts, mixed prose-plus-payload messages) for API and browser tests in `api/tests/conftest.py` and `web/__tests__/mocks/handlers.ts`
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
- [ ] T030 [P] Document developer validation and troubleshooting for formatted transcripts in `README.md` and `docs/user-guide/troubleshooting.md`
- [ ] T031 Add regression coverage for the text-only fast path, mixed-content order preservation, and thinking block correctness in `api/tests/test_conversations.py` and `web/__tests__/components/MessageBubble.test.tsx`; include a fixture built from the "Staving off Height Loss" conversation node set and assert that 0 out of the rendered message bubbles show `[No content]` and that at least one `ThinkingBlock` element is present with the correct activity type
- [ ] T032 Run backend validation for `api/tests/test_conversations.py` and `api/tests/test_formatting_service.py`
- [ ] T033 Run frontend validation for `web/__tests__/services/api.test.ts`, `web/__tests__/components/MessageBubble.test.tsx`, `web/__tests__/components/MarkdownRenderer.test.tsx`, `web/__tests__/components/FallbackBlock.test.tsx`, `web/__tests__/components/ThinkingBlock.test.tsx`, `web/__tests__/components/DateSeparator.test.tsx`, `web/__tests__/components/ImageModal.test.tsx`, and `web/__tests__/e2e/conversation.spec.ts`
- [ ] T034 Run the end-to-end quickstart validation from `specs/004-frontend-formatting/quickstart.md` against representative markdown and structured payload conversations
- [ ] T035 Add source-parity fixtures and regression coverage for generated assistant content versus imported historical content in `api/tests/conftest.py`, `api/tests/test_formatting_service.py`, and `web/__tests__/mocks/handlers.ts`
- [ ] T036 Add backend and frontend tests for raw HTML and unsafe embedded-content payload handling in `api/tests/test_formatting_service.py`, `api/tests/test_conversations.py`, and `web/__tests__/components/MarkdownRenderer.test.tsx`
- [ ] T037 Verify and harden markdown rendering: confirm `MarkdownRenderer.tsx` was built without `rehype-raw`, audit that no unsafe plugins have been introduced, and verify `FallbackBlock.tsx` escapes all user-supplied label text — T005 owns the initial safe configuration; this task is a hardening audit in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/components/conversations/FallbackBlock.tsx`
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
- T004, T005, T005a, T005b, T005c, T007, and T008 can run in parallel once T003 defines the shared segment contract.
- T006a and T006b both depend on T006 and can follow immediately; T006a and T006b can run in parallel with each other; T006a test coverage overlaps with T008 — coordinate to avoid duplicate fixtures.
- T009 and T010 can run in parallel for US1.
- T014a and T014b must both follow T014 (they extend the `MarkdownRenderer` built in T014); T014a and T014b can run in parallel with each other once T014 is complete.
- T016 and T017 can run in parallel for US2.
- T023 and T024 can run in parallel for US3.
- T029 and T030 can run in parallel during Polish.
- T035 and T036 can run in parallel during Polish.
- T039 can run alongside T035/T036.

---

## Parallel Example: User Story 1

```text
Task: T009 Add backend contract and parser tests in api/tests/test_conversations.py and api/tests/test_formatting_service.py
Task: T010 Add frontend renderer and fallback component tests in web/__tests__/components/MarkdownRenderer.test.tsx and web/__tests__/components/FallbackBlock.test.tsx
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

- Total tasks: 46
- Setup: 2 (T001–T002)
- Foundational: 11 (T003–T008, includes T005a — ThinkingBlock; T005b — DateSeparator; T005c — ImageModal + AttachmentImage thumbnail; T006a — processing turn grouping; T006b — user-visible message count)
- US1: 10 (T009–T015, includes T013a — date separator integration + header date simplification; T014a — KaTeX math rendering; T014b — citation token stripping)
- US2: 7 (T016–T022)
- US3: 6 (T023–T028)
- Polish & Cross-Cutting Concerns: 10 (T029–T037, T039; T038 removed — was mobile viewport E2E, out of scope)

### Suggested MVP Scope

- Complete through Phase 3 (User Story 1) for the first delivery.

---

## Notes

- All task lines follow the required checklist format: checkbox, sequential ID, optional `[P]`, required story label inside user story phases, and exact file paths.
- User stories remain independently testable after the shared foundational phase.
- The live contract referenced by these tasks is `specs/004-frontend-formatting/contracts/message-rendering-api.yaml`.
