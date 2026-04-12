# Tasks: Design Improvements for Frontend Formatting

**Input**: Design notes from `/specs/004-frontend-formatting/design-improvment-notes.md`
**Prerequisites**: `tasks.md`, `spec.md`, `plan.md`, `research.md`, `quickstart.md`

**Tests**: Tests are included because these improvements are largely presentation, interaction, accessibility, and responsiveness changes that need component, settings, and browser validation.

**Organization**: Tasks are grouped by shared foundations and improvement area so transcript rendering, turn actions, and sidebar/navigation changes can be implemented and validated in controlled slices.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel when dependencies are satisfied and files do not overlap
- **[Story]**: Maps a task to a design improvement slice (`US1`, `US2`, `US3`, `US4`)
- Every task below includes exact file paths

---

## Phase 1: Setup

**Purpose**: Add fixtures, preferences, and validation scaffolding needed to implement the design refresh safely.

- [ ] T001 Add regression fixtures for long user prompts, dense lists, markdown tables, and multi-language fenced code blocks in `web/__tests__/components/MarkdownRenderer.test.tsx`, `web/__tests__/components/MessageBubble.test.tsx`, and `web/__tests__/e2e/conversation.spec.ts`
- [ ] T002 [P] Extend persisted settings contracts for design-level transcript preferences such as code line-number visibility and long-prompt truncation in `api/services/settings_service.py`, `api/routers/settings.py`, `web/src/types/index.ts`, `web/src/services/api.ts`, and `web/src/components/settings/SettingsForm.tsx`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared styling, interaction primitives, and sidebar shell required by every design improvement slice.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [ ] T003 Create reusable transcript action primitives for raw-copy and speech controls in `web/src/components/conversations/TurnActions.tsx` and `web/src/lib/utils.ts`
- [ ] T004 [P] Consolidate transcript, table, code-block, and sidebar surface tokens for both light and dark themes in `web/src/app/globals.css`
- [ ] T005 [P] Refactor the sidebar shell into fixed header, scrollable body, and fixed footer regions with persisted collapse support in `web/src/components/layout/Sidebar.tsx`, `api/services/settings_service.py`, `api/routers/settings.py`, `web/src/types/index.ts`, and `web/src/components/settings/SettingsForm.tsx`

**Checkpoint**: Shared styling and interaction primitives are in place, and the sidebar can support the required structural changes.

---

## Phase 3: User Story 1 - Improve Transcript Formatting Readability (Priority: P1) 🎯 MVP

**Goal**: Code blocks, tables, lists, and explicit markdown rules render with editor-grade readability and without avoidable visual clutter.

**Independent Test**: Open a conversation containing fenced code, long code lines, tables, bullet and numbered lists, and explicit horizontal rules. Code should highlight cleanly, wrap within the container, offer raw copy, optionally show line numbers, and render tables and lists with improved spacing and structure.

### Tests for User Story 1

- [ ] T006 [P] [US1] Add renderer coverage for syntax highlighting, raw-code copy, wrapped long lines, line-number toggling, table rendering, list spacing, and explicit-only horizontal rules in `web/__tests__/components/MarkdownRenderer.test.tsx`, `web/__tests__/components/MessageBubble.test.tsx`, and `web/__tests__/e2e/conversation.spec.ts`

### Implementation for User Story 1

- [ ] T007 [US1] Upgrade fenced code block rendering with language-aware syntax highlighting, lighter backgrounds, and increased monospace leading in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/app/globals.css`
- [ ] T008 [US1] Add code-block copy actions that copy raw code only, never styling or line numbers, in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/components/conversations/TurnActions.tsx`
- [ ] T009 [US1] Implement optional line-number gutters with a visually separated number column that is excluded from text selection and copy flows in `web/src/components/conversations/MarkdownRenderer.tsx`, `web/src/app/globals.css`, and `web/src/components/settings/SettingsForm.tsx`
- [ ] T010 [US1] Make code blocks wrap to the transcript width without horizontal scrolling while preserving visual indentation and raw-copy fidelity in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/app/globals.css`
- [ ] T011 [US1] Render markdown tables as accessible HTML tables with a copy button, stronger header and row backgrounds, improved row spacing, and horizontal separators without vertical grid lines in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/app/globals.css`
- [ ] T012 [US1] Tighten list-item spacing and ensure rule lines render only for authored markdown separators in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/app/globals.css`

**Checkpoint**: Transcript content is materially more readable for technical conversations and long-form markdown.

---

## Phase 4: User Story 2 - Improve Turn-Level Actions and Long Prompt Handling (Priority: P2)

**Goal**: Each turn is easier to reuse or consume, and very long user prompts no longer overwhelm the transcript.

**Independent Test**: Open a conversation with long user prompts and multi-paragraph assistant replies. Each rendered turn should expose copy and speech actions, and very long user prompts should collapse behind a clear "Read more" control that preserves raw content when expanded or copied.

### Tests for User Story 2

- [ ] T013 [P] [US2] Add component and browser coverage for turn-level copy, speech controls, and user-only long-prompt truncation in `web/__tests__/components/MessageBubble.test.tsx`, `web/__tests__/components/ThinkingBlock.test.tsx`, and `web/__tests__/e2e/conversation.spec.ts`

### Implementation for User Story 2

- [ ] T014 [US2] Add a reusable turn action bar with raw-turn copy and text-to-speech controls in `web/src/components/conversations/TurnActions.tsx`, `web/src/components/conversations/MessageBubble.tsx`, and `web/src/components/conversations/AssistantTurn.tsx`
- [ ] T015 [US2] Implement very-long-user-prompt truncation with an accessible "Read more" toggle that applies only to user-authored turns in `web/src/components/conversations/MessageBubble.tsx` and `web/src/app/globals.css`

**Checkpoint**: Turn blocks support direct copy and audio playback, and user-authored walls of text are easier to scan.

---

## Phase 5: User Story 3 - Redesign Sidebar Navigation and Conversation List (Priority: P1)

**Goal**: Search, tags, favorites, and conversation navigation live in a more usable sidebar with fixed framing and a cleaner conversation list.

**Independent Test**: Load the app on desktop with a populated archive. The sidebar should place the search bar under the site title, support collapse/expand, keep top and bottom utility areas fixed, keep only the conversation list scrollable, and show title-first conversation items with hover metadata and ordering controls.

### Tests for User Story 3

- [ ] T016 [P] [US3] Add sidebar and navigation regression coverage for collapse state, embedded search, collapsible tags and favorites sections, conversation ordering controls, fixed header/footer regions, and empty main-pane invitation content in `web/__tests__/components/SearchBar.test.tsx`, `web/__tests__/components/ConversationCard.test.tsx`, `web/__tests__/e2e/home.spec.ts`, `web/__tests__/e2e/search.spec.ts`, `web/__tests__/e2e/favorites.spec.ts`, and `web/__tests__/e2e/tags.spec.ts`

### Implementation for User Story 3

- [ ] T017 [US3] Move the primary search input into the sidebar directly beneath the site title and align route behavior between sidebar search and the dedicated search page in `web/src/components/layout/Sidebar.tsx`, `web/src/components/search/SearchBar.tsx`, and `web/src/app/search/page.tsx`
- [ ] T018 [US3] Add an explicit sidebar collapse/expand control with persisted user preference and clear affordances in `web/src/components/layout/Sidebar.tsx`, `api/services/settings_service.py`, `api/routers/settings.py`, `web/src/types/index.ts`, and `web/src/components/settings/SettingsForm.tsx`
- [ ] T019 [US3] Move tags into the sidebar navigation body as a collapsible section that renders only when tags exist, and add a matching collapsible favorites section for quick access to favorited conversations in `web/src/components/layout/Sidebar.tsx`, `web/src/components/tags/TagList.tsx`, and `web/src/app/favorites/page.tsx`
- [ ] T020 [US3] Rework the sidebar layout so the search and section controls stay fixed, the conversation list scrolls independently, and footer actions remain pinned to the bottom in `web/src/components/layout/Sidebar.tsx` and `web/src/components/conversations/VirtualizedConversationList.tsx`
- [ ] T021 [US3] Simplify conversation list items to title-first rows with hover-revealed metadata, remove always-visible secondary metadata from the default card face, and preserve clear active and hover states in `web/src/components/conversations/ConversationCard.tsx` and `web/src/components/conversations/VirtualizedConversationList.tsx`
- [ ] T022 [US3] Add ascending and descending ordering controls plus an empty-state invitation in the main conversation area when nothing is selected in `web/src/app/page.tsx`, `web/src/app/conversation/[id]/page.tsx`, and `web/src/components/layout/Sidebar.tsx`

**Checkpoint**: Navigation is more discoverable, the conversation list is more scannable, and the main pane behaves correctly when idle.

---

## Phase 6: User Story 4 - Accessibility, Responsiveness, and Dark Mode Polish (Priority: P1)

**Goal**: The refreshed formatting remains accessible, responsive, and visually coherent across themes and screen sizes.

**Independent Test**: Validate the refreshed UI with keyboard-only navigation, screen-reader-friendly labels, narrow viewports, and both light and dark themes. Transcript controls, tables, code blocks, and sidebar interactions should stay readable and operable in all supported layouts.

### Tests for User Story 4

- [ ] T023 [P] [US4] Add regression coverage for keyboard navigation, focus management, ARIA labels, screen-reader text, dark-mode contrast, and responsive transcript behavior in `web/__tests__/components/MarkdownRenderer.test.tsx`, `web/__tests__/components/SearchBar.test.tsx`, `web/__tests__/components/ConversationCard.test.tsx`, `web/__tests__/e2e/conversation.spec.ts`, and `web/__tests__/e2e/home.spec.ts`

### Implementation for User Story 4

- [ ] T024 [US4] Audit and correct semantics, ARIA labeling, and focus behavior for transcript content, code controls, tables, search, and sidebar actions in `web/src/components/conversations/MarkdownRenderer.tsx`, `web/src/components/conversations/MessageBubble.tsx`, `web/src/components/search/SearchBar.tsx`, and `web/src/components/layout/Sidebar.tsx`
- [ ] T025 [US4] Rework dark-theme tokens so code blocks, table surfaces, conversation cards, and sidebar states feel like a natural extension of the light theme rather than legacy overrides in `web/src/app/globals.css`
- [ ] T026 [US4] Harden responsive layouts for transcript actions, long prompts, wrapped code, and collapsible navigation across desktop, tablet, and mobile breakpoints in `web/src/components/layout/Sidebar.tsx`, `web/src/components/conversations/MessageBubble.tsx`, `web/src/components/conversations/MarkdownRenderer.tsx`, `web/src/components/conversations/ConversationCard.tsx`, and `web/src/app/layout.tsx`
- [ ] T027 [US4] Ensure images and other rich content expose meaningful alternative text or equivalent accessible labels throughout the transcript in `web/src/components/conversations/AttachmentImage.tsx`, `web/src/components/conversations/ImageModal.tsx`, and `web/src/components/conversations/MessageBubble.tsx`

**Checkpoint**: The design refresh is accessible, responsive, and visually consistent in both light and dark themes.

---

## Phase 7: Final Validation and Documentation

**Purpose**: Close the loop on the design-improvement slice with documented outcomes and cross-story validation.

- [ ] T028 [P] Run end-to-end regression coverage for transcript rendering, sidebar navigation, search, favorites, tags, and settings after the design refresh in `web/__tests__/e2e/conversation.spec.ts`, `web/__tests__/e2e/home.spec.ts`, `web/__tests__/e2e/search.spec.ts`, `web/__tests__/e2e/favorites.spec.ts`, `web/__tests__/e2e/tags.spec.ts`, and `web/__tests__/e2e/persistence.spec.ts`
- [ ] T029 Update the follow-up design implementation summary with completed improvements, intentional deferrals, and remaining risks in `specs/004-frontend-formatting/remediation-report.md`

---

## Dependencies and Execution Order

- Complete Phase 1 before Phase 2 so fixtures and settings contracts exist before UI work starts.
- Complete Phase 2 before any user story work because the design tokens, turn actions, and sidebar shell changes are shared dependencies.
- User Stories 1 and 2 can proceed in parallel after Phase 2 if the shared transcript action primitives are stable.
- User Story 3 should begin after T005 because the sidebar shell refactor is its main blocking dependency.
- User Story 4 should validate and polish the work from User Stories 1 through 3 rather than running as a disconnected visual sweep.
- Finish with Phase 7 to document what shipped and confirm the refreshed experience works across the key user flows.