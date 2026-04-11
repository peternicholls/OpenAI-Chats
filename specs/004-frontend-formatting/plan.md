# Implementation Plan: Frontend Formatting

**Branch**: `004-frontend-formatting` | **Date**: 2026-03-25 | **Last Amended**: 2026-04-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-frontend-formatting/spec.md`

## Summary

Replace the current plain-text conversation rendering with an ordered segment-based presentation pipeline so message content can display ChatGPT-style formatted markdown, inline attachments, and readable structured-content fallbacks without exposing raw markdown markers or raw Python-dict / JSON-like payload blobs.

The concrete technical approach is to extend the conversation API response with `segments[]` for each message. The backend will derive ordered `markdown`, `attachment`, and `fallback` segments from stored message content while preserving the existing `content` and `attachments` fields for compatibility. The frontend will render those segments with a safe markdown renderer and the existing attachment components.

## Technical Context

**Language/Version**: Python 3.10+ (backend), TypeScript 5 / React 19 / Next.js 16 (frontend)  
**Primary Dependencies**: FastAPI, Pydantic, SQLite-backed archive service, React, Tailwind CSS, existing attachment components; planned addition of `react-markdown`, `remark-breaks`, `remark-math`, `rehype-katex`, and `katex` (for KaTeX CSS)  
**Storage**: SQLite for indexed archive data; filesystem-backed archive media store already introduced by feature 003; no schema changes planned  
**Testing**: pytest + pytest-asyncio (API), Vitest + React Testing Library (frontend), Playwright (end-to-end)  
**Target Platform**: macOS development, Linux/Docker deployment, responsive web UI on desktop and mobile  
**Project Type**: Web application with Python API in `api/` and Next.js client in `web/`  
**Performance Goals**: No visible regression for text-only conversations in the existing validation suite; attachment order must remain stable for all rendered messages; desktop and mobile transcript layouts must remain readable in acceptance coverage  
**Constraints**: Preserve archive data as source of truth, avoid database migrations, keep current attachment system from feature 003 intact, never execute raw HTML or unsafe embedded content, preserve compatibility for existing API clients during rollout  
**Scale/Scope**: Single-user self-hosted archive with ~1.7k conversations, mixed historical and assistant-generated content, focused on conversation detail rendering and its supporting API contract

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Data-First Architecture** | ✅ PASS | Formatting is derived at response time from stored archive content; raw archive and DB records remain unchanged |
| **II. CLI-First Interface** | ⚠️ CONDITIONAL | This is a presentation feature, but the derived `segments` contract remains inspectable through existing API responses and test fixtures; no GUI-only data source is introduced |
| **III. Fast Search & Retrieval** | ✅ PASS | Search paths are untouched; formatting only affects conversation detail rendering |
| **IV. Format-Agnostic Export** | ✅ PASS | Export formats are not changed by this feature; rendering logic is isolated to conversation detail presentation |
| **V. Simplicity & Composability** | ✅ PASS | No schema change, no new service tier, and reuse of existing attachment components keeps the design minimal |
| **Data Integrity** | ✅ PASS | Unsupported payloads fall back to readable blocks rather than being dropped or mutated |

**No gate failures.**

**Post-Phase 1 re-check**: ✅ The design artifacts keep formatting as a derived API/view concern, introduce no persistence changes, and preserve archive fidelity with explicit fallbacks for unsupported content.

## Project Structure

### Documentation (this feature)

```text
specs/004-frontend-formatting/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── message-rendering-api.yaml
└── tasks.md
```

### Source Code (repository root)

```text
api/
├── models/
│   └── responses.py                 # extend Message response with render segments
├── services/
│   ├── archive_service.py           # attach segments to conversation messages; filter internal processing turns
│   ├── media_service.py             # reused attachment extraction logic
│   └── formatting_service.py        # NEW: segment builder for markdown/attachment/fallback blocks
├── routers/
│   └── conversations.py             # response contract remains ConversationDetail
└── tests/
    ├── test_conversations.py        # extend conversation response assertions
    └── test_formatting_service.py   # NEW: segment builder coverage

web/
├── package.json                     # add markdown rendering dependencies
├── src/
│   ├── components/conversations/
│   │   ├── MessageBubble.tsx        # switch to segment-based rendering path
│   │   ├── MarkdownRenderer.tsx     # EXTEND: safe markdown presentation
│   │   ├── FallbackBlock.tsx        # EXTEND: readable structured-content fallback UI
│   │   ├── ThinkingBlock.tsx        # NEW: collapsible agent reasoning/search indicator
│   │   ├── DateSeparator.tsx        # NEW: inline calendar-date separator between message groups
│   │   ├── AttachmentImage.tsx      # EXTEND: thumbnail inline; click opens ImageModal
│   │   ├── ImageModal.tsx           # NEW: full-image modal with metadata, download, close, backdrop-dismiss
│   │   ├── AttachmentAudio.tsx      # reused
│   │   └── AttachmentFile.tsx       # reused
│   └── types/
│       └── index.ts                 # add RenderSegment types to Message
└── __tests__/
    ├── components/
    │   ├── MessageBubble.test.tsx   # extend mixed rendering assertions
    │   └── MarkdownRenderer.test.tsx# NEW
    └── e2e/
        └── conversation.spec.ts     # extend formatted transcript scenarios
```

**Structure Decision**: The existing web-application split is retained. Backend work is limited to producing a richer conversation-detail contract, and frontend work is limited to consuming that contract in the existing conversation view. No new package boundaries or infrastructure layers are introduced.

## Complexity Tracking

No constitutional violations require justification.

| Decision | Why Needed | Simpler Alternative Rejected Because |
|----------|------------|--------------------------------------|
| Add `segments[]` to message responses | Preserve exact content ordering across markdown, attachment, and fallback blocks | Rendering directly from a raw string in the browser cannot reliably distinguish prose from transport payloads without duplicating backend parsing rules |
| Use `react-markdown` with limited plugins | Safe, maintainable rendering for the supported markdown subset | Regex-based in-house formatting would be brittle and harder to secure |
| Keep legacy `content` + `attachments` alongside new `segments` during rollout | Avoid breaking current clients and simplify verification | Hard-switching the response shape would increase rollout risk for little benefit |
| Add `remark-math` + `rehype-katex` with a `\[\]`/`\(\)` → `$$`/`$` pre-pass | Archive uses non-standard LaTeX delimiters; KaTeX only interprets `$`/`$$` by default | Rendering math as a fallback plain block would leave technical conversations unreadable and contradict FR-013 |
| Strip PUA citation tokens (`\uE200(file)?cite...\uE201`) in the pre-processing step | These are internal ChatGPT retrieval markers with no user-facing meaning; they render as junk characters without removal | Labelling them as fallback blocks clutters transcripts; silent removal is the correct behaviour per FR-014 |
| Filter internal processing turns in `archive_service.py` before segment generation | Archive exports from thinking/search models contain `thoughts`, `code` (tool dispatch), `web.run`, and `reasoning_recap` nodes with all content stripped by OpenAI; `is_visually_hidden_from_conversation` only covers `system` and `user_editable_context` nodes — the rest must be identified by `content_type` and `author_role` | Filtering at display time in the frontend would push content-type knowledge into the UI layer, violating the response contract boundary; filtering at import time would be destructive |
| Render reasoning/search turns as a collapsible `ThinkingBlock` rather than suppressing silently | Suppressing these turns entirely hides the fact that the AI was reasoning or searching, which is useful context for the reader | A static `[No content]` placeholder would be visual noise; the `ThinkingBlock` preserves the activity signal with none of the clutter; grouping by activity type (reasoning vs. search vs. both) is derivable entirely from `content_type` and `author_role` already in the DB with no schema change |
| Inline date separators in conversation view derived from `message.create_time` | Conversations can span many calendar days; without orientation markers a reader loses track of when turns occurred | A sticky/floating date header would require scroll-position tracking and is out of scope; rendering the date on every bubble adds clutter; the inline separator matches iMessage/Slack convention and is a pure frontend rendering concern with no API changes required |
| Message count in conversation header derived from user-visible messages only | The current `COUNT(*)` query includes hidden system nodes, internal tool/thinking turns, and bootstrap placeholders — the raw number is misleading | Showing the raw DB count inflates the number by every suppressed node; the correct denominator is the same suppression predicate used by FR-015/FR-016, applied at the query level in `archive_service.py` |
| Image attachments rendered as thumbnails opening an `ImageModal` rather than full-size inline | Full-size images break message bubble layout at typical conversational message widths; opening-in-new-tab loses metadata and provides no download affordance | A small thumbnail preserves reading flow; the modal gives full-size view, filename, dimensions/size/MIME, and a download link without leaving the conversation view; clicking outside the modal (backdrop click + Escape) follows web platform conventions for dismissible overlays |
