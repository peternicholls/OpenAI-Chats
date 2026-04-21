# Visual Review & Design Improvement Plan — Phase 004 Recap

**Date:** 21 April 2026
**Branch:** `004-frontend-formatting`
**Scope:** Full walkthrough of the running app at `http://localhost/`, covering welcome, conversation (text / code / image / reasoning / tool-heavy / branches), search, settings, import, and the sidebar at desktop width. Dark theme only (the running stack has no light mode asset to test — see F4).

This document captures what was observed, what works well, and a prioritised plan of improvements. It supplements `design-improvment-notes.md` and `remediation-report.md`; nothing here contradicts a locked spec decision — items marked **[proposal]** are open for discussion.

---

## 1. What works well (don't regress these)

- **Sidebar IA.** Search at the top, conversation list in the middle, collapsible Tags/Favorites, utilities pinned at the bottom in a 2-col grid reads cleanly. Collapsing the sidebar to a rail is smooth and the rail width is right.
- **Collapsible section persistence.** Tags/Favorites remember their open state per `localStorage` key.
- **Code blocks** have language label, copy button, optional line numbers, wrap instead of scroll horizontally, and the dark palette is readable.
- **Tool-noise reduction (T012a).** "3 tool calls" and "Reasoning and web search" pills collapse what used to be long vertical stacks. This is a huge readability win.
- **Turn actions** (copy raw / TTS) appear on every turn in a consistent spot.
- **Markdown fidelity** for ordered lists, bold inline emphasis, and inline code is solid.
- **Keyboard affordances** — "Skip to main content" link, visible focus rings, ARIA roles on the sidebar complementary region. Good baseline accessibility.

---

## 2. High-priority issues (bugs / clear regressions)

### H1. Duplicate turns from conversation branches leak into the transcript
**Seen on:** `/conversation/544a9c4c-...` (the PHP "Expert Laravel Developer" conversation).
Four consecutive "You" turns at 12:17 / 12:31 / 12:31 / 12:38 AM show near-identical content. This matches the known issue tracked in spec `005-conversation-tree-fidelity`: the importer captures all branches and the renderer walks them all instead of the active leaf path.

The formatting work in 004 sits on top of this, so the transcript reads as if the user sent the same prompt four times.

**Fix:** land Spec 005 (active-leaf selection in the backend `segments` pipeline). Until then, at minimum the frontend should visually cluster same-role consecutive turns from the same `parent_id` chain under a single header with a "1/4" branch indicator — not stack them as independent turns.

### H2. Raw citation tokens are exposed to readers
**Seen on:** `/conversation/68e06336-...` (AI image check).
Strings like `【167580331394512†L104-L123】` and `【567417716240138†L213-L220】` appear inline throughout assistant prose. These are ChatGPT's internal source-citation sentinels; they were meant to be rendered as footnote links or stripped.

**Fix:** in `formatting_service.py` (or the frontend `MarkdownRenderer`), replace `【<id>†L<a>-L<b>】` with either (a) nothing, if we have no resolvable source, or (b) a superscript `[n]` linking to a footnote list at the end of the turn.

### H3. `{{file:file-XXXX}}` placeholders rendered literally
**Seen on:** `/conversation/6971a870-...` (Laravel SQL Conversion).
A user message contained `{{file:file-6exRfSqW2y8xuCLXhkaYZj}}` visible as raw text.

**Fix:** resolve this placeholder against the attachments table at render time; if unresolved, swap for a small "Referenced file (unavailable)" chip rather than leaking the token.

### H4. "Reasoning and web search" pill appears on **user** turns
**Seen on:** `/conversation/68e06336-...` — a user turn containing an image is prefaced by a "Reasoning and web search" pill, which makes no sense for a user message.

**Fix:** the reasoning/tool pill assembly in `AssistantTurn.tsx` / `turnContent.ts` is leaking pre-message reasoning into the following user turn. Scope pill rendering to `author_role === 'assistant'` only.

### H5. Inline images are undersized and look abandoned in their bubble
**Seen on:** the gymnast image in 68e06336.
The image renders at ~280 px wide inside a full-width user bubble, with a large empty gutter to its right. Captioning and filename are absent.

**Fix (proposal):** give `AttachmentImage` a responsive width cap (e.g. `min(520px, 100%)`) and remove the surrounding bubble's right-hand flex fill so the image sits naturally. Optional: show the original filename as a small caption below.

---

## 3. Medium-priority improvements

### M1. Search duplication / mental model is unclear
The sidebar search and `/search` both exist. The sidebar search filters the visible conversation list; the `/search` page runs FTS across messages. Users land on `/search` and see two search boxes stacked.

**Proposal:** pick one of:
- Keep both but rename sidebar input to "Filter conversations…" (it already filters titles) and hide it when on `/search`.
- Fold `/search` into an expanded-results surface inside the sidebar, so there is only one search entry.

### M2. Irrelevant "Score: 0.00" badge on every keyword search result
Keyword search doesn't compute a meaningful score, so every result shows `Score: 0.00`. This is noise.

**Fix:** hide the score badge when mode is `keyword`. Show it only for `semantic`/`hybrid` (or remove until semantic search ships a real score).

### M3. Search-result card density is too low
Each result consumes ~260 vertical px for a title, date, match count, one snippet line. On a 1440p screen the user sees ~5 results without scrolling.

**Proposal:** Halve vertical padding, put metadata on one row with the title, and use 2-line clamped snippet. Target ~120 px per card.

### M4. Conversation list shows **all conversations** on /search, /settings, /import etc.
The sidebar pulls 100+ conversation titles on every route. For users with large archives this is cognitively heavy and scrolls far beyond the visible content.

**Proposal:** When not on `/` or `/conversation/*`, collapse the conversation list to a "Recent (5)" preview with "Show all" toggle, freeing sidebar vertical space for context relevant to the current route.

### M5. Welcome page hero has weak affordance hierarchy
Four quasi-identical ghost buttons (Search archive / Favourites / Bulk export / Import). All look the same weight. For a user with zero conversations, Import is the only useful action; for a user with many, Search or the sidebar list is.

**Proposal:** Make the CTA adapt to state. Empty archive → big primary "Import ChatGPT export". Populated archive → a "Jump back in" primary card listing the 3 most recently updated conversations, with Search/Favorites/Export as secondary links.

### M6. Settings "Save Settings" friction
Theme, sidebar-collapsed, and truncate-long-prompts are already live-persisting settings elsewhere. Forcing a user to click Save after toggling a single checkbox is inconsistent with the rest of the shell.

**Proposal:** Auto-save per-field with a subtle "Saved" toast. Remove the Save button from General entirely; keep it on API / Embeddings where secrets/config must be validated before commit.

### M7. Import page is barren — no drop target, no format hint
Currently: just a "Choose Archive" button and one sentence.
ChatGPT exports are large ZIPs and users expect drag-and-drop.

**Proposal:** Replace the card with a dashed drop zone (click or drop), list supported formats ("ChatGPT export ZIP, typically ~50 MB–5 GB"), and show a bulleted preview of what happens next ("We extract the archive → import conversations → index for search"). Include recent import history below.

### M8. Timestamps are time-only, divorced from date context
Every turn shows `12:58 AM` with no date. Long conversations spanning days, or the browsing experience of archived chats from years ago, benefit from at least day context.

**Proposal:** Insert a `DateSeparator` chip (the component already exists) whenever the calendar date changes between turns. On the first turn, show the full date. Keep the header's date summary as-is.

### M9. Conversation header metadata is thin
The header shows date, message count, model. Missing: tags inline (there is an "Add Tag" button but existing tags are not shown alongside), favorite toggle's current state is a star icon with no state text, and there is no "Jump to top/bottom" or "Outline" affordance for long transcripts.

**Proposal:** Show existing tag pills inline next to the "+ Add Tag" button; add a right-aligned "Outline" button that opens a panel listing assistant-turn first-line summaries for fast intra-conversation navigation.

### M10. "Sort oldest first" button label & icon
The sidebar sort toggle shows an up/down arrow icon. The aria-label is "Sort oldest first" (the *action*), but users read it as the *current state*. Accessibility convention is to label it with current state ("Sorted newest first").

**Fix:** Match the pattern used for the sidebar collapse toggle — label should describe current state, not action.

---

## 4. Low-priority / polish / future direction

### L1. Assistant and user avatar icons are visually identical in weight
Both are simple single-colour line icons of a person / bot. Dark palette makes them blend together. Not a bug, but subtle differentiation (e.g. accent-tinted ring on the assistant, filled vs outlined variant) would help transcript skimming.

### L2. User-message filled bubble vs. assistant no-bubble asymmetry
User turns sit on a filled dark-blue panel; assistant turns flow directly on the page background. This asymmetry currently *emphasises* the user. For an archive viewer where the user likely wants the assistant output to dominate (it's usually the useful content), consider flipping: a subtle tinted surface for assistant, plain bg for user. Or drop both bubbles and use avatar + role label alone (ChatGPT's own UI).

### L3. "Read more" for long user prompts expands cleanly, but the collapsed state provides no visual cue that there's more
The threshold (500 chars) cuts mid-sentence. A gradient fade on the collapsed prompt would better signal truncation than an abrupt cut.

### L4. Light theme
The Settings dropdown offers Light/Dark/System, but the bulk of styling work in phase 004 assumed dark. We should either:
  - a. Run the T016 dark-mode work in reverse for light, validating WCAG contrast (code syntax palette in particular), or
  - b. Disable light mode in Settings until it is fully verified (hide the option rather than ship a broken theme).

### L5. "Help" in the sidebar goes to GitHub
It opens in the same tab. Small thing: `target="_blank" rel="noopener noreferrer"` so users don't lose their place.

### L6. Favorites section empty-state handling
The section hides when empty (good). But the welcome-page "Favourites" CTA still routes to `/favorites` when there are none — users click and see an empty state they could have avoided. Disable / hide that CTA when favorite count is 0.

### L7. Conversation-list item metadata visible states
The design target reveals metadata on hover. On touch devices there is no hover. Verify the behavior on iPad/mobile: either always-show compact metadata on narrow widths, or expose it with tap/long-press. (Not verified in this review because `setViewportSize` didn't repaint in the chromium embed.)

### L8. Code-block line numbers — defaulting
The setting is off by default. For code-heavy archives (many of mine), on-by-default would be more useful. Consider an "advanced presentation" Settings sub-group with default-on and a toggle.

### L9. Copy feedback
Turn-level copy and table-level copy don't appear to emit any visible confirmation. A 1-second "Copied" label on the button itself prevents the "did it work?" second click.

### L10. Attachments tab / filter in search
FTS currently searches message text. Users exporting/filtering archives often want "all conversations that contained an image" or "all with audio" — add filter chips on the search page (Type: Text / Image / Audio / Code-heavy).

---

## 5. Recommended plan

A suggested sequencing that front-loads user-visible correctness wins before polish.

**Sprint A (fix the leaks):** H1 (or interim cluster), H2, H3, H4, H5, M10.
**Sprint B (search & entry points):** M1, M2, M3, M5.
**Sprint C (navigation & context):** M4, M8, M9, M6, M7.
**Sprint D (polish / future):** L1–L10 and L4 light-theme validation, plus the remainder of H1 if not completed (Spec 005 integration).

Each sprint ends with the validation sequence from `design-improvement-tasks.md` Phase 7: `cd web && npx tsc --noEmit` → `npm run build` → visual check in the built-in browser → update `remediation-report.md`.

---

## 6. Out of scope for this review

- Performance profiling of the virtualised conversation list (needs a 1000+ conversation import to meaningfully test).
- Playwright a11y audit (axe-core) — recommended as a separate task.
- Mobile responsive verification — the embedded browser in this session didn't honour viewport resize. Needs a real device or a headed Playwright run.
- Any spec 005 (conversation tree fidelity) work — referenced only insofar as it blocks H1.
