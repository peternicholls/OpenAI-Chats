# Tasks: Design Improvements for Frontend Formatting

**Input**: Design notes from `/specs/004-frontend-formatting/design-improvment-notes.md`
**Prerequisites**: not required.

**Tests**: Tests are included because these improvements are presentation, interaction, accessibility, and responsiveness changes that require component, settings, and browser validation.

**Organization**: Tasks are grouped by shared foundations and improvement area so transcript rendering, turn actions, and sidebar/navigation changes can be implemented and validated in controlled slices.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel when dependencies are satisfied and files do not overlap
- **[Story]**: Maps a task to a design improvement slice (`US1`, `US2`, `US3`, `US4`)
- Every task includes exact file paths

---

## ⛔ Scope Rules — Read Before Every Task

These rules apply to every task in this file without exception.

1. **Only edit the files listed in the task.** Do not touch any other file.
2. **Only make the change described in the task.** If the task says "add a copy button", add a copy button. Do not reorganise the component, rename props, restructure the JSX tree, or change anything else.
3. **Do not refactor, rename, or restructure existing code** unless the task description explicitly says to do so.
4. **Do not change the visual appearance** of any element not named in the task description.
5. **Do not change routing, data fetching, API calls, or state management** beyond what the task explicitly requires.
6. **Preserve all existing behavior** that the task does not describe changing.
7. **Do not add new dependencies** (npm packages, Python packages) without confirming with the user first.
8. **Do not create new files** other than those named in the task.
9. **The task description is the complete specification.** Do not infer additional changes from the design notes, other tasks, or general best-practice judgement.
10. **If a task requires touching a shared component**, change only the specific piece described. Leave all other parts of that component exactly as they are.
11. **After every implementation task, verify the change in a real browser.** Run `cd web && npm run dev` (or use the running Docker stack at `http://localhost/`), open the page, and visually confirm the change works exactly as described. If anything looks wrong, is broken, or does not match the task description, fix it before marking the task complete. Repeat the build-and-check cycle until the browser output matches the spec. Do not mark a task done based on code review alone.
12. ** When completed and verified, mark the task done by checking the box.** Do not check a task until you have completed the implementation and verified it in the browser. This is critical for accurate progress tracking and reporting. Then COMMIT with a message that includes the task ID and a brief description of the change, e.g. "T008 [US1] Add copy button to code blocks". Do not combine multiple tasks into one commit. This discipline allows us to track progress, identify blockers, and maintain a clear history of changes.

---

## Phase 1: Setup

**Purpose**: Write test fixtures and extend settings contracts before any UI work begins.

- [x] T001 Write test fixtures covering long user prompts (>500 chars), dense nested lists, markdown tables, and fenced code blocks in at least three languages in `web/__tests__/components/MarkdownRenderer.test.tsx`, `web/__tests__/components/MessageBubble.test.tsx`, and `web/__tests__/e2e/conversation.spec.ts`
- [x] T002 [P] Add two persisted settings fields — `codeLineNumbers: boolean` and `longPromptTruncation: boolean` — to the settings schema, API route, TypeScript types, API client, and settings form in `api/services/settings_service.py`, `api/routers/settings.py`, `web/src/types/index.ts`, `web/src/services/api.ts`, and `web/src/components/settings/SettingsForm.tsx`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the shared CSS tokens, action component, and sidebar structure that every user story depends on.

**⚠️ CRITICAL**: Do not start any user story task until all Phase 2 tasks are complete.

- [ ] T003 Create `TurnActions.tsx` as a new file containing a single component that accepts a `text: string` prop and renders a copy-to-clipboard button and a text-to-speech button; add `copyToClipboard(text: string)` and `speakText(text: string)` utility functions to `web/src/lib/utils.ts`; do not modify any existing component or file other than appending to `utils.ts` in `web/src/components/conversations/TurnActions.tsx` and `web/src/lib/utils.ts`
- [ ] T004 [P] Define CSS custom properties for transcript surface, table surface, code block surface, and sidebar surface colors in both light and dark themes in `web/src/app/globals.css`
- [ ] T005 [P] Change the CSS layout of `Sidebar.tsx` so the existing site-title area is `position: sticky; top: 0`, the existing conversation list area is `overflow-y: auto; flex: 1`, and the existing footer area is `position: sticky; bottom: 0`; add a full-width `<hr>` after the site title and another `<hr>` before the footer; add a `sidebarCollapsed: boolean` field to the settings schema and persist it via the API; do not rename, move, or remove any existing JSX elements, props, or child components inside `Sidebar.tsx` in `web/src/components/layout/Sidebar.tsx`, `api/services/settings_service.py`, `api/routers/settings.py`, `web/src/types/index.ts`, and `web/src/components/settings/SettingsForm.tsx`

**Checkpoint**: Run `cd web && npm run dev` and open `http://localhost:3000` in a browser. Confirm the app loads without console errors. Confirm the sidebar renders with its three layout regions and the two `<hr>` separators visible. Confirm `TurnActions` can be imported without error. Fix any build or runtime error before proceeding.

---

## Phase 3: User Story 1 — Transcript Formatting Readability (Priority: P1) 🎯 MVP

**Scope**: Code blocks, tables, and lists render with correct syntax highlighting, wrapping, copy behavior, and spacing. Rule lines appear only where the author wrote a markdown separator.

**Acceptance check**: Run the app in the browser. Open a conversation that contains fenced code in at least two languages, a long single line of code, a markdown table, a bullet list, a numbered list, and an explicit `---` separator. Visually verify in the browser: code is highlighted with language-specific colours, has a copy button, wraps within the container with no horizontal scrollbar, and optionally shows a line-number gutter; the table has no vertical grid lines; list items have correct spacing; the `---` renders as a visible rule but no rules appear between turns. Fix any visual discrepancy before marking the phase complete.

### Tests for User Story 1

- [ ] T006 [P] [US1] Write tests that assert: syntax highlighting classes are applied per language, the copy button copies raw code only (no ANSI or HTML), long lines wrap without a horizontal scrollbar, line numbers toggle on/off, tables render as `<table>` elements without vertical borders, list-item spacing matches spec, and `<hr>` elements appear only when the source markdown contains `---` in `web/__tests__/components/MarkdownRenderer.test.tsx`, `web/__tests__/components/MessageBubble.test.tsx`, and `web/__tests__/e2e/conversation.spec.ts`

### Implementation for User Story 1

- [ ] T007 [US1] In `MarkdownRenderer.tsx`, update only the `code` renderer: swap the current background value for `var(--code-surface)` and add `lineHeight: '1.6'`; integrate a syntax highlighting library (e.g. `react-syntax-highlighter`) for language-aware token colouring; do not change any other renderer (headings, paragraphs, blockquotes, images, links, or any other element type) and do not change any surrounding component structure in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/app/globals.css`
- [ ] T008 [US1] Add a copy button to each code block that writes the raw source string (no formatting, no line numbers) to the clipboard using the `TurnActions` copy utility in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/components/conversations/TurnActions.tsx`
- [ ] T009 [US1] Implement an optional line-number gutter: the gutter column is separated from the code by a 1px vertical divider and a distinct background shade; the gutter uses `user-select: none` so it is excluded from drag selection; the copy button writes only the code text, not the line numbers; the gutter is visible only when the `codeLineNumbers` setting is `true` in `web/src/components/conversations/MarkdownRenderer.tsx`, `web/src/app/globals.css`, and `web/src/components/settings/SettingsForm.tsx`
- [ ] T010 [US1] Set `white-space: pre-wrap` and `word-break: break-all` on code blocks so long lines wrap to the container width with no horizontal scrollbar; the copy button still writes the original unbroken source string in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/app/globals.css`
- [ ] T011 [US1] In `MarkdownRenderer.tsx`, update only the `table` renderer to produce a `<table>` with `<thead>` and `<tbody>`, a copy button above it (copies the raw markdown table string), CSS for a distinct header-row background, alternating body-row backgrounds, increased cell padding, `border-collapse: collapse`, and horizontal-only `<tr>` borders; do not change any other renderer and do not change any surrounding component structure in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/app/globals.css`
- [ ] T012 [US1] Reduce the margin between a list item marker and its text to `0.15em`; set bottom padding on each `<li>` to `0.4em`; remove any `<hr>` that is injected between turns automatically — only render `<hr>` when the markdown source contains an explicit `---`, `***`, or `___` separator in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/app/globals.css`

**Checkpoint**: All T006 tests pass. Then open the app in the browser, load a conversation with code, tables, and lists, and visually confirm each item in the acceptance check above. Fix anything that fails the visual check before moving to Phase 4.

---

## Phase 4: User Story 2 — Turn-Level Actions and Long Prompt Handling (Priority: P2)

**Scope**: Every turn exposes a copy button and a text-to-speech button. User-authored turns longer than 500 characters are collapsed to 500 characters with a "Read more" expand toggle.

**Acceptance check**: Run the app in the browser. Open a conversation with a user prompt longer than 500 characters and at least one assistant reply. Visually verify: the user turn is truncated at 500 characters with a visible "Read more" button; clicking "Read more" expands to the full text; both user and assistant turns show a copy button and a speak button; clicking copy writes the full raw text to the clipboard (paste it somewhere to verify); clicking speak produces audible output via the browser speech API. Fix any visual or functional discrepancy before marking the phase complete.

### Tests for User Story 2

- [ ] T013 [P] [US2] Write tests that assert: the copy button on each turn writes the full raw text to the clipboard; the speak button calls `window.speechSynthesis.speak`; user turns with text longer than 500 characters render with truncated content and a "Read more" button; clicking "Read more" renders the full text; assistant turns are never truncated in `web/__tests__/components/MessageBubble.test.tsx`, `web/__tests__/components/ThinkingBlock.test.tsx`, and `web/__tests__/e2e/conversation.spec.ts`

### Implementation for User Story 2

- [ ] T014 [US2] Mount `TurnActions` at the bottom of every rendered turn with a copy button (copies full raw message text) and a speak button (calls `window.speechSynthesis.speak` with the raw text) in `web/src/components/conversations/TurnActions.tsx`, `web/src/components/conversations/MessageBubble.tsx`, and `web/src/components/conversations/AssistantTurn.tsx`
- [ ] T015 [US2] In `MessageBubble`, when the turn role is `user` and the raw text length exceeds 500 characters, display only the first 500 characters followed by a "Read more" button; clicking the button replaces the truncated view with the full text and a "Show less" button; the copy button always writes the full untruncated text in `web/src/components/conversations/MessageBubble.tsx` and `web/src/app/globals.css`

**Checkpoint**: All T013 tests pass. Then open the app in the browser, load a conversation with a long user prompt, and visually confirm each item in the acceptance check above. Fix anything that fails before moving to Phase 5.

---

## Phase 5: User Story 3 — Sidebar Navigation and Conversation List (Priority: P1)

**Scope**: The sidebar has the layout defined in T005. The search input is inside the sidebar below the site title. Tags and favorites are collapsible sidebar sections. The conversation list is scrollable and title-only by default. Ordering controls and an empty-state message are present in the main pane.

**Acceptance check**: Run the app in the browser with a populated archive. Visually confirm each of the following in the browser — fix each one that fails before marking the phase complete:
- The search input appears below the site title in the sidebar.
- Clicking the collapse toggle collapses the sidebar; reloading the page keeps it collapsed.
- The tags section is visible only when tags exist; clicking its header collapses it.
- The favorites section is visible only when favorites exist; clicking its header collapses it.
- The conversation list scrolls independently while the sidebar header and footer stay fixed on screen.
- Each list item shows only the title by default; hovering over it reveals the date.
- "Oldest first" and "Newest first" buttons are visible and reorder the list.
- The main pane shows the empty-state message when no conversation is selected.

### Tests for User Story 3

- [ ] T016 [P] [US3] Write tests that assert: the search input renders inside the sidebar below the site title; the sidebar collapse toggle toggles a collapsed CSS class and persists the value; the tags section renders only when tag data is present; the favorites section renders only when favorites are present; both sections toggle open/closed; conversation list items show only the title until hovered; ordering controls render and change list order; the main pane shows an empty-state element when no conversation is selected in `web/__tests__/components/SearchBar.test.tsx`, `web/__tests__/components/ConversationCard.test.tsx`, `web/__tests__/e2e/home.spec.ts`, `web/__tests__/e2e/search.spec.ts`, `web/__tests__/e2e/favorites.spec.ts`, and `web/__tests__/e2e/tags.spec.ts`

### Implementation for User Story 3

- [ ] T017 [US3] Move the `SearchBar` component into the sidebar scrollable body, directly below the site title; when the user submits a query from the sidebar search, navigate to `/search?q=...` using the same route that the dedicated search page uses in `web/src/components/layout/Sidebar.tsx`, `web/src/components/search/SearchBar.tsx`, and `web/src/app/search/page.tsx`
- [ ] T018 [US3] Add a collapse/expand toggle button to the sidebar header; toggling it sets a `sidebar-collapsed` CSS class on the sidebar root element and saves the boolean to the `sidebarCollapsed` settings field introduced in T005; on page load, read the persisted value and apply the class before first paint in `web/src/components/layout/Sidebar.tsx`, `api/services/settings_service.py`, `api/routers/settings.py`, `web/src/types/index.ts`, and `web/src/components/settings/SettingsForm.tsx`
- [ ] T019 [US3] Inside `Sidebar.tsx`, insert a collapsible "Tags" section (renders only when the tags list is non-empty) and a collapsible "Favorites" section (renders only when the favorites list is non-empty) into the existing scrollable body area defined in T005; reuse the existing `TagList` component and existing tag pill styles exactly as-is without any visual modification; do not change the `TagList` component itself, do not change `favorites/page.tsx`, and do not alter anything else in the sidebar in `web/src/components/layout/Sidebar.tsx`, `web/src/components/tags/TagList.tsx`, and `web/src/app/favorites/page.tsx`
- [ ] T020 [US3] Set the sidebar header to `position: sticky; top: 0` and the sidebar footer to `position: sticky; bottom: 0` so both remain visible while the conversation list scrolls; set the conversation list container to `overflow-y: auto; flex: 1` so it is the only element that scrolls in `web/src/components/layout/Sidebar.tsx` and `web/src/components/conversations/VirtualizedConversationList.tsx`
- [ ] T021 [US3] In `ConversationCard.tsx`, set subtitle/snippet/date elements to `visibility: hidden` by default and `visibility: visible` on `:hover`; do not remove those elements from the DOM, do not change their content, do not change the card's dimensions, padding, font, or color, do not change the active or hover background, and do not modify `VirtualizedConversationList.tsx` unless a CSS class change is required to target the hover state in `web/src/components/conversations/ConversationCard.tsx` and `web/src/components/conversations/VirtualizedConversationList.tsx`
- [ ] T022 [US3] Add two sort buttons ("Oldest first" and "Newest first") immediately above the conversation list inside `Sidebar.tsx`; clicking a button re-sorts the existing list data in state without any page navigation or API call; in `web/src/app/page.tsx`, add a centered empty-state `<div>` containing an icon and the text "Select a conversation to begin" that is shown only when no conversation ID is active; do not change any other part of `page.tsx`, `conversation/[id]/page.tsx`, or `Sidebar.tsx` in `web/src/app/page.tsx`, `web/src/app/conversation/[id]/page.tsx`, and `web/src/components/layout/Sidebar.tsx`

**Checkpoint**: All T016 tests pass. Then open the app in the browser and work through every item in the acceptance check above. Fix any item that fails before moving to Phase 6.

---

## Phase 6: User Story 4 — Accessibility, Responsiveness, and Dark Mode (Priority: P1)

**Scope**: All elements introduced in the previous phases have correct ARIA attributes, keyboard operability, and focus management. Dark-mode tokens mirror the light-mode structure. Layouts function at 320 px, 768 px, and 1280 px viewport widths.

**Acceptance check**: Open the app in the browser and verify the following — fix each failure before marking the phase complete:
- Tab through the entire page using keyboard only; every interactive element (copy, speak, collapse, sort) must receive visible focus and activate on Enter/Space.
- Open browser DevTools → Accessibility panel (or run `axe` in the console) and confirm zero critical violations.
- Switch the OS or browser to dark mode; visually inspect code blocks, tables, conversation cards, and the sidebar and confirm no elements have illegible contrast or missing backgrounds.
- Resize the browser to 320 px width; confirm the sidebar, transcript, and action buttons are usable and nothing is clipped or overflows.

### Tests for User Story 4

- [ ] T023 [P] [US4] Write tests that assert: all interactive elements (copy buttons, speak buttons, collapse toggles, sort controls) have `aria-label` values; focus moves correctly after modal open/close; dark-mode CSS tokens produce contrast ratios ≥ 4.5:1 for text on background; transcript and sidebar layouts are not clipped at 320 px viewport width in `web/__tests__/components/MarkdownRenderer.test.tsx`, `web/__tests__/components/SearchBar.test.tsx`, `web/__tests__/components/ConversationCard.test.tsx`, `web/__tests__/e2e/conversation.spec.ts`, and `web/__tests__/e2e/home.spec.ts`

### Implementation for User Story 4

- [ ] T024 [US4] Add `aria-label` to every icon-only button (copy, speak, collapse, expand, sort); add `role` and `aria-expanded` to every collapsible section; ensure that after a modal closes, focus returns to the element that triggered it in `web/src/components/conversations/MarkdownRenderer.tsx`, `web/src/components/conversations/MessageBubble.tsx`, `web/src/components/search/SearchBar.tsx`, and `web/src/components/layout/Sidebar.tsx`
- [ ] T025 [US4] Replace any hard-coded dark-mode color values with the dark-theme variants of the CSS custom properties defined in T004, so that code blocks, table surfaces, conversation cards, and sidebar backgrounds all switch via the same token layer in `web/src/app/globals.css`
- [ ] T026 [US4] Verify and fix layout at the 320 px, 768 px, and 1280 px breakpoints: the sidebar must not overlap the main content; the `TurnActions` bar must not overflow its container; truncated user prompts must not clip; wrapped code must not cause horizontal page scroll in `web/src/components/layout/Sidebar.tsx`, `web/src/components/conversations/MessageBubble.tsx`, `web/src/components/conversations/MarkdownRenderer.tsx`, `web/src/components/conversations/ConversationCard.tsx`, and `web/src/app/layout.tsx`
- [ ] T027 [US4] Set a descriptive `alt` attribute on every `<img>` in the transcript; for decorative images set `alt=""`; for images where no alt text is available, set `alt="Attached image"` in `web/src/components/conversations/AttachmentImage.tsx`, `web/src/components/conversations/ImageModal.tsx`, and `web/src/components/conversations/MessageBubble.tsx`

**Checkpoint**: All T023 tests pass. Then open the app in the browser and work through every item in the acceptance check above. Fix any item that fails before moving to Phase 7.

---

## Phase 7: Final Validation and Documentation

**Purpose**: Run the full regression suite across all affected flows and record outcomes.

- [ ] T028 [P] Run the full Playwright suite and confirm all tests pass for transcript rendering, sidebar navigation, search, favorites, tags, and settings in `web/__tests__/e2e/conversation.spec.ts`, `web/__tests__/e2e/home.spec.ts`, `web/__tests__/e2e/search.spec.ts`, `web/__tests__/e2e/favorites.spec.ts`, `web/__tests__/e2e/tags.spec.ts`, and `web/__tests__/e2e/persistence.spec.ts`
- [ ] T029 Write the implementation summary in `specs/004-frontend-formatting/remediation-report.md` listing: each task ID and its completion status, any requirements that were deferred and why, and any known remaining issues

---

## Dependencies and Execution Order

- T001 and T002 (Phase 1) must be complete before any Phase 2 work starts.
- T003, T004, and T005 (Phase 2) must all be complete before any user story task starts.
- T007–T012 (US1) and T014–T015 (US2) can run in parallel once T003 and T004 are done.
- T017–T022 (US3) must wait for T005.
- T024–T027 (US4) must wait for US1, US2, and US3 to be complete, because US4 fixes and validates their output.
- T028 and T029 (Phase 7) run last, after all US4 tasks pass.