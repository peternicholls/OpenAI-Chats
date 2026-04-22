# Implementation Plan: Inline Media in Conversation View

**Branch**: `003-inline-media` | **Date**: 2026-02-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-inline-media/spec.md`

## Summary

Serve OpenAI export archive media files (images, audio, documents) via a new API media endpoint, parse `sediment://` and `file-service://` asset pointer URIs from stored message content at response time, and render the resolved attachments inline in the web UI `MessageBubble` component. No database schema changes required.

The key architectural finding from research: the API import flow currently extracts archives to a temp directory and deletes them; archive media files are not persisted after import. The design must solve the **archive persistence problem** — ensuring media files are accessible to the API at request time — without touching the DB. The solution chosen is a permanent media store directory, written during import and pointed at via an env var / settings entry (`CHATGPT_ARCHIVE_DIR`).

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript / Next.js 15 (frontend)  
**Primary Dependencies**: FastAPI (API), SQLite via `chatgpt_archive.db` (data layer), React + Tailwind CSS (web UI)  
**Storage**: SQLite (no schema changes); local filesystem (permanent archive media store)  
**Testing**: pytest + pytest-asyncio (API), vitest + React Testing Library (frontend)  
**Target Platform**: macOS (development), Linux (production/Docker)  
**Project Type**: Web application — `api/` backend + `web/` Next.js frontend  
**Performance Goals**: Media file serving <200ms p95 on same-host requests; conversation load time unaffected for text-only conversations  
**Constraints**: No SQLite schema changes; no full archive re-scan at startup; on-demand per-request file resolution; no external CDN or image proxy  
**Scale/Scope**: Single-user self-hosted; 1,778 conversations; ~150+ media files in current archive

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Data-First** — archive is source of truth, DB is derived index | ✅ PASS | Media files served directly from archive; DB not modified |
| **I. Data-First** — import MUST be idempotent | ✅ PASS | Media store is additive; existing files preserved |
| **II. CLI-First** — every capability accessible via CLI before GUI | ⚠️ CONDITIONAL | New `CHATGPT_ARCHIVE_DIR` env var enables CLI use; no GUI-only gate |
| **V. Simplicity** — single SQLite DB, YAGNI, complexity justified | ✅ PASS | No new DB tables; media store is just a directory; no abstraction layers |
| **V. Simplicity** — complexity beyond principles must be justified | ✅ PASS | New endpoint + parser + UI components are minimal and necessary |
| **Data Integrity** — import MUST validate JSON before processing | ✅ PASS | Asset pointer parsing is read-only and resilient |

**No gate violations. Constitution check PASSES.**

**Post-Phase 1 re-check**: ✅ The design (see research.md and data-model.md) does not introduce new database tables, does not require full directory scanning at startup, and degrades gracefully for missing files. All principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/003-inline-media/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Option 2: Web application
api/
├── routers/
│   └── media.py                  # NEW: GET /api/media/{conv_id}/{file_id}
│                                 #      GET /api/media/root/{file_id}
├── services/
│   └── media_service.py          # NEW: asset pointer resolver + file lookup
├── models/
│   └── responses.py              # MODIFIED: Message.attachments field added
└── tests/
    └── test_media.py             # NEW

web/src/
├── components/conversations/
│   ├── MessageBubble.tsx         # MODIFIED: render attachments
│   ├── AttachmentImage.tsx       # NEW: inline image with fallback
│   ├── AttachmentFile.tsx        # NEW: download card
│   └── AttachmentAudio.tsx       # NEW: inline audio player
├── types/
│   └── index.ts                  # MODIFIED: Attachment type, Message.attachments
└── services/
    └── api.ts                    # MODIFIED: media URL helper
```

**Structure Decision**: Option 2 (web application). Backend changes are isolated to a new router and service; frontend changes evolve the existing `MessageBubble` component with new attachment sub-components. No new projects or packages introduced.

## Complexity Tracking

No constitution violations requiring justification. The one decision worth noting:

| Decision | Why | Simpler Alternative Rejected Because |
|----------|-----|--------------------------------------|
| Parse message content at API response time | Avoids DB schema change; archive remains source of truth | Storing resolved URLs in DB would couple schema to archive layout and break sync on new imports |
| Permanent media store directory (not temp) | Media files must survive after import ZIP is cleaned up | Re-uploading ZIP on every image request is not viable; streaming from ZIP archive adds complexity |
