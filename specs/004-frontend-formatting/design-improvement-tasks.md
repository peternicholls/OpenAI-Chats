# Tasks: Design Improvements for Frontend Formatting

**Input**: Design notes from `/specs/004-frontend-formatting/design-improvment-notes.md`
**Purpose**: Translate the design notes into implementation work without losing fidelity, over-specifying engineering choices, or forcing everything into user-story framing.

[ ] to do
[P] in progress
[X] done

## Task Writing Rules

1. Write tasks in the imperative.
2. Keep tasks aligned to the design notes, not to invented feature slices.
3. Preserve note intent where the design is still exploratory, incomplete, or explicitly open-ended.
4. Treat implementation choices as engineering decisions unless the notes make them product requirements.
5. Preserve raw-content fidelity for all copy actions.
6. Document interpretations and deferred items in the remediation report.

## Validation Rules

1. Run `cd web && npx tsc --noEmit` before rebuilding for `web/` changes.
2. Use `cd web && npm run build` as the default rebuild step unless a task specifically requires container validation.
3. Verify browser-facing changes in the built-in browser against the running app.
4. Record whether each completed task was implemented directly, implemented with interpretation, or deferred due to unresolved design direction.
5. Only mark a task complete when the behavior is visible in the active localhost route, not merely because a component or helper exists in the codebase.

## Phase 1: Baseline and Coverage

**Purpose**: Establish current-state coverage before changing transcript and sidebar presentation.

- [X] T001 Build or refresh transcript fixtures covering long user prompts, nested lists, markdown tables, explicit horizontal rules, and fenced code blocks in multiple languages in `web/__tests__/components/MarkdownRenderer.test.tsx`, `web/__tests__/components/MessageBubble.test.tsx`, and `web/__tests__/e2e/conversation.spec.ts`
- [X] T002 Audit the current frontend against every section of the design notes and record mismatches, ambiguities, already-satisfied items, and likely sequencing constraints in `specs/004-frontend-formatting/remediation-report.md`

## Phase 2: Code Blocks

**Purpose**: Improve code readability while preserving raw-copy and raw-selection fidelity.

- [X] T003 Render code blocks with language-aware syntax highlighting and a copy button in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/app/globals.css`
- [X] T004 Increase font size and line height to improve readability in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/app/globals.css`
- [X] T005 Wrap code blocks to the container width without introducing horizontal scrolling, while preserving indentation and raw-copy fidelity, in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/app/globals.css`
- [X] T006 Add line numbers with clear visual separation, exclude them from drag selection, exclude them from copy output, and document how the note's optional toggle requirement is implemented in `web/src/components/conversations/MarkdownRenderer.tsx`, `web/src/app/globals.css`, and any necessary existing transcript settings or state files
- [X] T007 Add or update automated coverage for code highlighting, code-block copy behavior, wrapped presentation, and line-number behavior in `web/__tests__/components/MarkdownRenderer.test.tsx` and `web/__tests__/e2e/conversation.spec.ts`

## Phase 3: Tables, Lists, and Rule Lines

**Purpose**: Improve structured markdown readability and remove visual noise.

- [ ] T008 Render markdown tables as HTML tables with a copy action, readable header and row treatments, increased spacing, and horizontal separation only in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/app/globals.css`
- [ ] T009 Reduce the gap between list item heading and content, and increase spacing after each list item, in `web/src/components/conversations/MarkdownRenderer.tsx` and `web/src/app/globals.css`
- [ ] T010 Render horizontal rules only when they are explicitly present in markdown source, and remove any automatic rule-line insertion between turns, in `web/src/components/conversations/MarkdownRenderer.tsx`, `web/src/components/conversations/MessageBubble.tsx`, and `web/src/app/globals.css`
- [ ] T011 Add or update automated coverage for tables, list spacing, and explicit rule-line rendering in `web/__tests__/components/MarkdownRenderer.test.tsx`, `web/__tests__/components/MessageBubble.test.tsx`, and `web/__tests__/e2e/conversation.spec.ts`

## Phase 4: Turn Actions and Long User Prompts

**Purpose**: Improve utility and readability at the message-turn level.

- [ ] T012 Add a turn-level copy action that copies raw turn content and a turn-level text-to-speech action that reads the turn content in `web/src/components/conversations/MessageBubble.tsx`, related conversation components, and any shared turn-action component introduced for this feature
- [ ] T013 Add a long-user-prompt treatment for user turns only, using truncation plus a "Read more" affordance, and document any interpretation needed because the note presents this as a consideration rather than a locked requirement in `web/src/components/conversations/MessageBubble.tsx` and `web/src/app/globals.css`
- [ ] T014 Add or update automated coverage for turn-level copy, speech, and long-user-prompt expansion behavior in `web/__tests__/components/MessageBubble.test.tsx`, related component tests, and `web/__tests__/e2e/conversation.spec.ts`

## Phase 5: Accessibility, Dark Mode, and Responsive Layout

**Purpose**: Apply accessibility, dark-mode, and responsive improvements across the updated transcript and navigation UI.

- [ ] T015 Research and apply accessibility improvements for the changed UI, including contrast, font sizing, screen-reader clarity, keyboard navigation, ARIA labeling, alt text, semantics, and focus handling, in the affected transcript and navigation components under `web/src/components/` and `web/src/app/`
- [ ] T016 Update dark-mode styling so it reads as a natural extension of the light-mode design, and replace conflicting legacy dark-mode styling, in `web/src/app/globals.css` and affected frontend components
- [ ] T017 Validate and fix layout behavior across mobile and desktop widths so transcript content, action bars, and sidebar layout remain readable and usable in the affected frontend components under `web/src/components/` and `web/src/app/`
- [ ] T018 Add or update automated coverage for accessibility-critical and responsive behavior introduced by this work in the relevant tests under `web/__tests__/`

## Phase 6: Sidebar Navigation and Conversation List

**Purpose**: Rework sidebar information architecture and conversation-list behavior to match the design notes.

- [ ] T019 Move the search bar into the sidebar directly below the site title in `web/src/components/layout/Sidebar.tsx`, `web/src/components/search/SearchBar.tsx`, and any related page wiring that currently owns the search experience
- [ ] T020 Make the sidebar collapsible in a way that is clear, accessible, and low-noise in `web/src/components/layout/Sidebar.tsx` and any existing persisted settings or layout state files needed to support the chosen behavior
- [ ] T021 Move tags into the sidebar navigation as an expandable or collapsible section only when tags exist, while preserving current tag formatting, in `web/src/components/layout/Sidebar.tsx` and existing tags components used by the sidebar
- [ ] T022 Add a favorites section to the sidebar when favorites exist, and make its expandable or collapsible behavior consistent with the sidebar notes, in `web/src/components/layout/Sidebar.tsx` and any existing favorites-related UI already used by the app
- [ ] T023 Adjust sidebar layout so upper controls stay fixed, the conversation list scrolls independently, and lower actions remain pinned in place in `web/src/components/layout/Sidebar.tsx`, related list components, and `web/src/app/globals.css`
- [ ] T024 Update the conversation list so it emphasizes titles, reveals metadata on hover, supports ascending and descending ordering, and shows an inviting empty state when no conversation is selected in the relevant conversation-list, card, and page components under `web/src/components/conversations/` and `web/src/app/`
- [ ] T025 Add or update automated coverage for search placement, sidebar collapse, collapsible sections, independent list scrolling, ordering controls, hover metadata, and the no-selection empty state in the relevant tests under `web/__tests__/`

## Phase 7: Final Validation and Documentation

**Purpose**: Confirm that the implemented work matches the notes and capture any remaining ambiguity or deferral.

- [ ] T026 Run the targeted frontend validation sequence for this feature: `cd web && npx tsc --noEmit`, `cd web && npm run build`, and the relevant Vitest and Playwright coverage for transcript and sidebar behavior
- [ ] T027 Verify transcript formatting, turn actions, long user prompts, dark mode, responsive layout, sidebar behavior, and conversation-list interactions in the built-in browser against the local app
- [ ] T028 Update `specs/004-frontend-formatting/remediation-report.md` with task completion status, exact design-note sections satisfied, documented interpretations, deferred items, and unresolved design questions

## Traceability Matrix

- Design note 1.1 to 1.4 Code Blocks: T003 to T007
- Design note 2 Tables: T008, T011
- Design note 3 Lists and 3.4 Rule lines: T009 to T011
- Design note 4 Turn Blocks: T012, T014
- Design note 5 Accessibility: T015, T018
- Design note 6 Dark Mode: T016
- Design note 7 Very long user prompts: T013, T014
- Design note 8 Search Bar: T019, T025
- Design note 9 Sidebar Navigation and Items: T020 to T023, T025
- Design note 10 Conversation List: T023 to T025, T027
- Further considerations: T002, T026 to T028

## Open Decisions To Preserve During Implementation

- Decide whether optional code line numbers are controlled by a persisted setting, a local toggle, or a default-only presentation choice
- Decide how strictly to implement long-user-prompt truncation, since the note frames it as something to consider rather than a finalized requirement
- Decide the exact dark-mode treatment while the design is still acknowledged as unfinished
- Decide the final sidebar item order beyond the note's example layout
- Confirm any new dependency required for syntax highlighting or related rendering support before adding it
