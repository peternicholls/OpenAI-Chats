# Sprint 004 Remediation Report

## Reconciliation Basis

This report reflects the current state of branch `004-frontend-formatting` as reviewed on 21 April 2026 against:

- the current task tracker in `specs/004-frontend-formatting/design-improvement-tasks.md`
- the actual code paths used by the live conversation route
- the localhost browser rendering observed during review

The review was grounded in the current active route implementation, not older report language.

## Evidence Reviewed

### Code paths

- `web/src/app/conversation/[id]/page.tsx`
- `web/src/components/conversations/AssistantTurn.tsx`
- `web/src/components/conversations/MessageBubble.tsx`
- `web/src/components/conversations/MarkdownRenderer.tsx`
- `web/src/components/conversations/ThinkingBlock.tsx`
- `web/src/components/conversations/ToolBlock.tsx`
- `web/src/components/layout/Sidebar.tsx`
- `api/services/archive_service.py`

### Browser evidence

- Home/index view at `http://localhost/`
- Conversation view for `Pub Manager Conflict`
- Conversation view for `Laravel SQL Conversion`

## Current Status Summary

### Confirmed complete

- T001: Fixture and test coverage groundwork exists for markdown-oriented transcript rendering.
- T002: The codebase has now been reviewed against the design notes and the gaps are documented here.
- T012: Turn-level copy and speech actions are live in the active conversation route and visible in the localhost browser.
- T012a: Tool-heavy assistant turns are condensed in the active conversation route instead of rendering long stacks of repeated tool pills.
- T013: Long-user-prompt truncation is live and browser-validated with real archive data. The `Read more` / `Show less` toggle is visible for user turns over 500 characters, and the live route now respects the saved `long_prompt_truncation` setting.
- T014: Coverage is complete across `MessageBubble.test.tsx` (26 tests), `AssistantTurn.test.tsx` (3 tests), `ThinkingBlock.test.tsx` (8 tests), and `MarkdownRenderer.test.tsx` (21 tests). The long-prompt expansion behavior is covered by an E2E test in `conversation.spec.ts`. Tooltip, sidebar, and infinite-loading coverage were expanded in this branch, and all 158 frontend tests pass.
- T008: Markdown tables render as readable HTML tables with copy support.
- T009: List spacing and within-item spacing have been tightened for better readability.
- T010: Horizontal rules now render only when explicitly present in message content rather than being inserted automatically between turns.
- T011: Automated coverage exists for table rendering, list spacing, and explicit rule-line handling.
- T015: Accessibility improvements for the changed transcript and sidebar UI are in place, including ARIA labeling, disclosure semantics, and keyboard-reachable controls.
- T016: Dark-mode styling has been reconciled with the updated transcript and sidebar presentation.
- T017: Responsive layout behavior has been validated across the updated transcript and sidebar shell.
- T018: Automated coverage for the accessibility-critical and responsive changes introduced in Sprint 004 is in place.
- T019: Sidebar search is live directly beneath the site title in the active shell.
- T020: Sidebar collapse is live, persisted, and browser-validated.
- T021: Tags are rendered as a collapsible sidebar section when present.
- T022: Favorites are rendered as a collapsible sidebar section when present.
- T023: Sidebar controls remain pinned while the conversation list scrolls independently.
- T024: The conversation list now emphasizes titles, exposes metadata on hover, supports ascending and descending ordering, and automatically loads additional conversation pages at the bottom of the list.
- T025: Automated coverage exists for sidebar search placement, collapse behavior, section rendering, ordering controls, and infinite conversation loading.
- T026: TypeScript clean (`npx tsc --noEmit`), production build (`npm run build`), and full Vitest suite (158/158 passing) all confirmed.
- T027: Browser validation now includes transcript formatting, long-user-prompt handling, sidebar behavior, and dynamic sidebar loading after rebuilding the local Docker web service.
- T028: This report.

### Confirmed in progress

- None.

### Confirmed not yet complete

- None within the scope of Sprint 004.

## What Is Actually Shipping

### Transcript and formatting progress that is real

- Segment-based transcript rendering is active in the conversation route.
- Basic markdown rendering is active.
- KaTeX preprocessing for ChatGPT delimiter normalization is present.
- Date-aware conversation headers are present.
- `ThinkingBlock`, `ToolBlock`, `DateSeparator`, `AttachmentImage`, and `ImageModal` components exist.
- Dedicated tests now exist for `ThinkingBlock`, `DateSeparator`, and `ImageModal`.

### Browser-visible evidence of progress

- The `Pub Manager Conflict` conversation renders readable formatted transcript content rather than raw markdown.
- The conversation header shows start date and updated date behavior.
- Assistant content renders headings and lists with clear formatting.

## Design Task Reconciliation Notes

### 1. Tool-heavy conversations are now materially calmer

The active route no longer renders a long vertical stack of repeated tool pills for the synthetic tool-heavy browser fixture used during validation.

Current route behavior:

- `AssistantTurn` now groups consecutive `tool` role messages into a single summarized `ToolBlock`.
- The localhost browser shows a single `3 tool calls` disclosure instead of three stacked `Tool call` pills.

Interpretation:

- This satisfies the intent of T012a by reducing low-value transcript noise while still allowing users to see that tool activity occurred.
- The chosen behavior is condensation rather than full suppression.

### 2. Code block work is now complete

`MarkdownRenderer` currently provides:

- a code-block header
- a language label
- a copy button
- syntax highlighting via `react-syntax-highlighter`
- wrapped code lines with a line-number gutter that avoids horizontal scrolling

Current code state:

- a syntax-highlighting renderer is active in the live component
- code cells wrap instead of forcing horizontal overflow
- code blocks expose a stable copy affordance and readable language header

Implication:

- T003 through T007 are complete.

### 3. Turn-level actions are live, and long user prompt treatment is wired through the active route

Both active turn-rendering paths now mount end-of-turn actions:

- `MessageBubble` renders turn-level copy and text-to-speech controls
- `AssistantTurn` renders the same controls for grouped assistant turns

Browser-visible evidence:

- The localhost conversation route shows icon-only copy and speech buttons with accessible names and hover labels.
- Raw-turn copy and speech actions are visible for both user and assistant turns.

Resolution (T013 and T014):

Root cause of the original failure: the `isPlainTextMessage` guard used `!message.segments` as the truncation condition. Real API data always carries `segments: [{kind: "markdown", text: ...}]` on every user message, so the guard was always false and truncation never activated.

Fix applied: the guard was rewritten to `isTextOnlyUserMessage` — a user turn with no attachments whose segments are exclusively `kind: "markdown"`. This matches the real API data shape and allows truncation for plain text user messages.

Route integration: the active conversation page now reads the saved `long_prompt_truncation` setting and passes it into `MessageBubble`, so the browser behavior matches the user's saved preference instead of always defaulting to truncation.

Browser validation: Verified with the "Pub Manager Conflict" conversation from the real archive database. The user message at 1282 characters shows the truncated form with a `Read more` button on first view; clicking expands to full text with a `Show less` button.

E2E test update: the long-prompt mock in `conversation.spec.ts` was updated to include a `segments` array matching the real API shape, and a second browser test now verifies that the route leaves long user prompts expanded when the saved setting disables truncation.

Implication:

- T012 is complete.
- T013 is complete.
- T014 is complete.

### 4. Sidebar and conversation-list redesign is live

The active shell now shows:

- the search input directly beneath the site title in the sidebar
- collapsible favorites and tags sections when those sections have content
- a conversation list whose controls stay pinned while the list itself scrolls independently
- title-first conversation rows with metadata revealed on hover
- automatic fetching of additional conversation pages when the bottom sentinel is reached

Implication:

- T019 through T025 are complete in real browser behavior.
- The current shell now matches the sidebar information architecture described in the design notes closely enough for completion.

### 5. The previous remediation report was stale

The previous version of this file no longer matched the branch state. It incorrectly claimed some tests were missing even though dedicated tests for `ThinkingBlock`, `DateSeparator`, and `ImageModal` are now present.

Implication:

- This report should now be treated as the source of truth for current remediation status.
- Older findings based on missing component tests should be discarded.

## Reconciled Task Interpretation

### Phase 1

- T001: done
- T002: done

### Phase 2

- T003: done
- T004: done
- T005: done
- T006: done
- T007: done

### Phase 3

- T008: done
- T009: done
- T010: done
- T011: done

### Phase 4

- T012: done
- T012a: done
- T013: done
- T014: done

### Phase 5

- T015: done
- T016: done
- T017: done
- T018: done

### Phase 6

- T019: done
- T020: done
- T021: done
- T022: done
- T023: done
- T024: done
- T025: done

### Phase 7

- T026: done
- T027: done
- T028: done

## Notes On Active Rendering Paths

The branch currently contains more than one transcript rendering path, and that matters for progress tracking.

- `MessageBubble.tsx` contains one segment-aware message renderer.
- The active conversation route also uses `AssistantTurn.tsx` to group assistant and tool messages into turns.

This means status should always be judged against the route-level browser output, not from reading a single component in isolation.

## Test Infrastructure Notes

During T014 completion, three pre-existing test environment issues were resolved:

### MSW base URL mismatch

The API client uses a relative base URL (`""`) in browser context (commit `0e6ecd1`, "fix(api-client): use relative URL in browser"). The MSW handlers in `__tests__/mocks/handlers.ts` were still pointing to `http://localhost:8000`. Two changes fixed this:

1. `handlers.ts`: changed `API_URL` from `http://localhost:8000` to `http://localhost`.
2. `vitest.config.ts`: added `environmentOptions.jsdom.url: 'http://localhost'` so jsdom resolves relative fetch URLs against `http://localhost` (matching the MSW handler origin).

One `api.test.ts` assertion (`should build absolute media URLs for relative paths`) was also updated to expect the relative path returned by the browser-mode API client instead of the old absolute `http://localhost:8000/…` form.

### ResizeObserver polyfill

Radix UI Tooltip (used by `TurnActions`) calls `ResizeObserver` which does not exist in jsdom. A no-op polyfill was added to `vitest.setup.ts` to prevent uncaught exceptions during full-suite runs.

### AssistantTurn TooltipProvider

`AssistantTurn.test.tsx` was failing with "Tooltip must be used within TooltipProvider" after `TurnActions` adopted a Radix tooltip. A `renderWithTooltip` helper wrapping renders in `<TooltipProvider>` was added, matching the existing pattern in `MessageBubble.test.tsx`.

These changes brought the total passing count from 122 to 152 (30 previously failing tests in `api.test.ts` and the hooks test files now pass).

## Recommended Next Work Order

1. Keep documentation and screenshots aligned if Sprint 004 follow-up polish changes the shell or transcript presentation.
2. Treat future sidebar or transcript changes as cross-layer work touching API segments, frontend rendering, tests, and browser validation together.

## Sprint A Completion (T029-T034)

Sprint A visual-review fixes are now complete on branch `004-frontend-formatting`.

### Implemented fixes

- T029: `MarkdownRenderer` now strips bracket-style citation sentinels such as `` before markdown rendering, with fixture coverage proving surrounding prose is preserved.
- T030: `MarkdownRenderer` now replaces `{{file:...}}` placeholders with `[Referenced file (unavailable)]`, with fixture coverage confirming the raw token no longer reaches the DOM.
- T031: pending processing clusters are only converted into `ThinkingSegment`s for assistant turns in `api/services/archive_service.py`, and `MessageBubble` defensively ignores thinking segments on non-assistant turns. API and frontend tests cover both sides.
- T032: attachment thumbnails now render at a fixed `h-40` with `object-contain`, so the full image remains visible without cropping. User image turns keep the standard full-width bubble layout, and consecutive image attachments are coalesced into a single inline row so multiple images display next to each other.
- T033: the sidebar sort toggle `aria-label` now describes current state (`Sorted newest first` / `Sorted oldest first`) rather than the next action.

### Validation evidence

- TypeScript: `cd web && ./node_modules/.bin/tsc --noEmit` passed.
- Frontend tests: `cd web && npm run test` passed with `171/171` tests green.
- Frontend build: `cd web && npm run build` passed.
- API targeted validation: `source .venv/bin/activate && pytest tests/api/test_conversations.py -q` passed.
- Localhost browser validation: after rebuilding the Dockerized web target, `http://localhost/conversation/68e06336-bce4-8330-b350-f7a33ffac85e` showed no bracket citation tokens, no raw `{{file:...}}` placeholders, no reasoning pill on user turns, and the target image turn rendered inside the standard full-width user bubble with a fixed 160 px visual height and uncropped `object-contain` scaling.
- Localhost sidebar validation: the sort toggle exposed `aria-label="Sorted newest first"`, matching the current state.

## Progress Tracking Rule Going Forward

Do not mark a task complete based on component existence alone.

A task should only move to complete when:

- the active localhost route shows the behavior
- the relevant tests cover it where appropriate
- the behavior matches the design-note intent closely enough to survive browser review

## Sidebar / Navigation Redesign (T015–T025) — Implementation Notes

The sidebar, header, and home page were rebuilt in this iteration. All 152 existing Vitest tests pass; `npx tsc --noEmit` and `npm run build` succeed.

### What changed

- New building blocks: `web/src/components/layout/CollapsibleSection.tsx`, `SidebarSearch.tsx`, `SidebarConversationList.tsx`, `SidebarTagsSection.tsx`, `SidebarFavoritesSection.tsx`, and `SidebarUiContext.tsx`.
- `Sidebar.tsx` rebuilt: site title at top, collapse affordance, `SidebarSearch` directly under the title, then tag and favourite sections (rendered only when populated), then the scrolling conversation list, with Settings / Import / Export / Help pinned in a two-column footer. An icon-only collapsed rail is available on desktop.
- `Header.tsx` reduced to a mobile-only bar containing just the drawer toggle and site title. The desktop header row is gone; the sidebar carries all navigation.
- `app/layout.tsx` now wraps children in `SidebarUiProvider` and adds a `Skip to main content` link plus a focusable `<main id="main-content">` landmark.
- `app/page.tsx` ( `/` ) renders a welcome hero by default — "Pick up where you left off" with Search, Favourites, Bulk export, and Import buttons. The previous conversation-management UI (bulk export, selection mode, pagination, virtualization) is preserved behind `?manage=1`, which is also the destination of the sidebar footer's **Export** link, and still renders automatically when a `?tag=...` filter is active so tag navigation keeps working.

### Decisions captured (see "Open Decisions To Preserve")

- **Sidebar collapse persistence**: uses the server-side `sidebar_collapsed` setting via `useUpdateSettings()` so preference follows the user across devices.
- **Section open/closed persistence**: tags and favourites use `localStorage` (`sidebar-section:tags` / `sidebar-section:favorites`) because these are low-stakes per-client preferences.
- **Help link**: no `/help` route exists; the footer Help icon opens the repository README on GitHub in a new tab.
- **Sidebar order**: title → search → tags → favourites → conversations (scrolls, flex-1) → pinned footer (Settings, Import, Export, Help). Tags and favourites sections are hidden entirely when empty, per the design notes.
- **Favourites list**: reuses `SidebarConversationList` with explicit `items`, a `compact` row variant, and a max-height scrollable container so it does not crowd the main list.
- **Bulk management on `/`**: retained behind `?manage=1` (accessible from the footer Export link and the welcome CTA) rather than removed, preserving existing select/export/sort/virtualization functionality.

### Accessibility and responsive work

- Landmarks: `<aside aria-label="Primary">`, `<nav aria-label="Utilities">`, `<header role="banner">`, `<main id="main-content" tabIndex={-1}>`, `<form role="search">`.
- Disclosures expose `aria-expanded` / `aria-controls`, conversation rows expose `aria-current="page"` when active.
- Icon-only buttons have `aria-label`s and Radix tooltips; a visible skip link targets the main landmark.
- Mobile: sidebar becomes a dialog-style drawer (`role="dialog" aria-modal="true"`) triggered by the mobile header's menu button; overlay click closes it. Desktop ≥ md keeps the fixed aside. A 56 px icon rail is shown when collapsed.
- Dark mode reuses the existing `--sidebar-surface` token so the new shell inherits the established theme rather than re-declaring colours.

### Test coverage

Focused Vitest coverage was added for the redesigned sidebar after live validation exposed integration gaps:

- `web/__tests__/components/layout/Sidebar.test.tsx` covers the collapsed-desktop/mobile-drawer interaction, verifies non-navigation controls do not dismiss the drawer, and verifies actual navigation links do dismiss it.
- `web/__tests__/components/layout/SidebarConversationList.test.tsx` covers the API-safe sidebar fetch limit, ordering toggle, and navigation callback.

Full frontend validation now passes at `158/158` tests.

### Outstanding

- Live browser validation against the Dockerized app confirmed the updated shell is serving real archive data, the desktop collapsed state persists across reload, and the sidebar conversation list now renders 100 live links without the previous 422 response.
- The sidebar list originally failed because it requested `limit=200` while the backend enforces `limit <= 100`; the component now uses an API-safe limit.
- The mobile drawer originally closed on any click inside it and disappeared entirely when the desktop collapsed state was persisted. Both behaviors were fixed in the sidebar shell and covered by the new layout tests.

