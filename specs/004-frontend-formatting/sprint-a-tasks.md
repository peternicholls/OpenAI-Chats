# Sprint A Tasks: Visual Review Fixes

**Branch**: `004-frontend-formatting`
**Source**: `visual-review-2026-04-21.md` — Sprint A scope only
**Date**: 21 April 2026

[ ] to do
[P] in progress
[X] done

---

## Scope

Fix five confirmed bugs from the 21 April visual review. H1 (duplicate turns from conversation branches) is excluded — it belongs to spec 005.

| Task | Review item | Files touched |
|------|-------------|---------------|
| T029 | H2 — Bracket citation tokens visible in prose | `MarkdownRenderer.tsx`, `MarkdownRenderer.test.tsx` |
| T030 | H3 — `{{file:…}}` placeholders rendered literally | `MarkdownRenderer.tsx`, `MarkdownRenderer.test.tsx` |
| T031 | H4 — ThinkingBlock pill on user turns | `archive_service.py`, `MessageBubble.tsx`, `test_conversations.py`, `MessageBubble.test.tsx` |
| T032 | H5 — Attachment image undersized and bubble too wide | `AttachmentImage.tsx`, `MessageBubble.tsx`, `MessageBubble.test.tsx` |
| T033 | M10 — Sort toggle aria-label describes action, not state | `SidebarConversationList.tsx`, sidebar tests |
| T034 | Validation | TypeScript, Vitest, build, browser, remediation report |

---

## Validation Rules

1. Run `cd web && npx tsc --noEmit` before rebuilding after any `web/` change.
2. Run `cd web && npm run test` after each task to confirm no regressions.
3. Run `cd web && npm run build` as the final frontend rebuild step.
4. Check the browser against `http://localhost/` and the affected conversation before marking T034 done.
5. Only mark a task complete when the fix is visible in the active localhost route.

---

## Tasks

### T029 — Strip bracket-style citation tokens (H2)

**Problem**: Strings like `【167580331394512†L104-L123】` appear inline in assistant prose. These are ChatGPT internal source-citation sentinels that should never reach the reader.

**Fix**: Add a second regex to the `preprocess()` function in `MarkdownRenderer.tsx` that strips these before the markdown pipeline.

- [ ] In `web/src/components/conversations/MarkdownRenderer.tsx`, add `const BRACKET_CITATION_RE = /【\d+†L\d+-L\d+】/g;` alongside the existing `CITATION_RE` constant, and call `.replace(BRACKET_CITATION_RE, "")` inside `preprocess()` immediately after the existing `CITATION_RE` replace.
- [ ] Add fixture assertions to `web/__tests__/components/MarkdownRenderer.test.tsx`:
  - a token `【167580331394512†L104-L123】` is absent from rendered output
  - surrounding prose before and after the token is preserved

---

### T030 — Replace `{{file:…}}` placeholders (H3)

**Problem**: User messages containing `{{file:file-6exRfSqW2y8xuCLXhkaYZj}}` render the raw placeholder token.

**Fix**: Intercept in `preprocess()` and substitute a readable fallback before markdown rendering.

- [ ] In `web/src/components/conversations/MarkdownRenderer.tsx`, add `const FILE_PLACEHOLDER_RE = /\{\{file:[A-Za-z0-9_-]+\}\}/g;` and call `.replace(FILE_PLACEHOLDER_RE, "[Referenced file (unavailable)]")` inside `preprocess()`.
- [ ] Add fixture assertions to `web/__tests__/components/MarkdownRenderer.test.tsx`:
  - the raw token `{{file:file-6exRfSqW2y8xuCLXhkaYZj}}` is absent from rendered output
  - the text `Referenced file (unavailable)` is present in its place

---

### T031 — Scope ThinkingBlock to assistant turns only (H4)

**Problem**: A "Reasoning and web search" pill appears on user turns that contain an image. The processing cluster preceding an image upload is being prepended to the wrong message.

**Fix**: Backend: only attach the pending cluster as a `ThinkingSegment` when the next visible message is from the assistant. Frontend: defensive guard to skip thinking segments on non-assistant messages.

- [ ] In `api/services/archive_service.py`, in the loop body where `pending_cluster` is flushed, add a condition so the `ThinkingSegment` is only prepended when `msg["author_role"] == "assistant"`. When the next message is `"user"` or `"system"`, discard `pending_cluster` (set it to `[]`) without producing a segment.
- [ ] In `web/src/components/conversations/MessageBubble.tsx`, in `renderSegment()`, add an early-return guard: if `segment.kind === "thinking"` and `message.role !== "assistant"`, return `null`.
- [ ] Add a test in `tests/api/test_conversations.py`: a conversation where a processing cluster is followed by a user message should produce zero thinking segments on that user message.
- [ ] Add a test in `web/__tests__/components/MessageBubble.test.tsx`: a user-role message with a thinking segment in its segment list renders no ThinkingBlock.

---

### T032 — Fix attachment image sizing in user bubble (H5)

**Problem**: The gymnast image renders at `h-32 w-48` (fixed thumbnail) inside a full-width user bubble, leaving a large empty gutter to its right.

**Fix**: Increase the thumbnail to a more intentional size; shrink the bubble to fit the content.

- [ ] In `web/src/components/conversations/AttachmentImage.tsx`, change the `<img>` className from `"h-32 w-48 object-cover"` to `"h-40 w-64 object-cover"`.
- [ ] In `web/src/components/conversations/MessageBubble.tsx`, locate the user bubble's outer wrapper (the element with the `rounded-2xl bg-…` classes for user turns). Change its width behaviour from full-width (or `w-full`) to `inline-flex flex-wrap gap-2 max-w-prose` so the bubble auto-sizes to its content when it contains only an attachment.
- [ ] Update any snapshot or className assertions in `web/__tests__/components/MessageBubble.test.tsx` that reference the old thumbnail dimensions or bubble width classes.

---

### T033 — Fix sort toggle aria-label (M10)

**Problem**: The sort button's `aria-label` is `"Sort oldest first"` / `"Sort newest first"` — it describes the *action*, not the *current state*. Accessibility convention for toggle controls is to label the current state.

**Fix**: Swap the label strings to describe state.

- [ ] In `web/src/components/layout/SidebarConversationList.tsx`, change the `aria-label` on the sort `Button`:
  - `order === "desc"` → `"Sorted newest first"` (was `"Sort oldest first"`)
  - `order === "asc"` → `"Sorted oldest first"` (was `"Sort newest first"`)
- [ ] Update the corresponding `aria-label` assertions in the sidebar conversation list tests under `web/__tests__/`.

---

### T034 — Validate Sprint A (all five fixes)

Run in order after T029–T033 are all marked done.

- [ ] `cd web && npx tsc --noEmit` — zero errors
- [ ] `cd web && npm run test` — all tests pass
- [ ] `cd web && npm run build` — clean production build
- [ ] Open `http://localhost/conversation/68e06336-bce4-8330-b350-f7a33ffac85e` in the browser and confirm:
  - H2: no bracket citation tokens visible in prose
  - H3: no `{{file:…}}` tokens visible in any message
  - H4: no "Reasoning and web search" pill on user turns
  - H5: image thumbnail is larger; user bubble does not have a wide empty gutter
- [ ] Open the conversation sidebar sort toggle and verify the tooltip and aria-label reflect current state
- [ ] Update `specs/004-frontend-formatting/remediation-report.md` with Sprint A completion status
