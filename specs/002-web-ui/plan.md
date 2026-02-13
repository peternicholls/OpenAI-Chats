# Implementation Plan: Web UI for ChatGPT Archive

**Branch**: `002-web-ui` | **Date**: 2026-02-12 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-web-ui/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a beautiful, modern web UI that exposes all ChatGPT Archive functionality (import, search, list, view, export, tag management, favorites, embedding generation, user settings) within a consistent, well-designed interface. Use Next.js with shadcn/ui for the frontend, FastAPI for the backend API, Server-Sent Events for real-time progress updates, and Docker for deployment. Data persists to ~/.chatgpt-archive/ for easy backup. Single-user personal deployment with no authentication required.

## Technical Context

**Language/Version**: 
- Backend: Python 3.11+ (existing codebase compatibility)
- Frontend: TypeScript with Next.js 14+ (React framework)

**Primary Dependencies**: 
- Backend: FastAPI (REST API layer over existing CLI/library), Uvicorn (ASGI server)
- Frontend: Next.js, shadcn/ui (accessible components), Tailwind CSS, React Query (state/caching)
- Container: Docker, Docker Compose

**Storage**: 
- SQLite (existing - single file database from feature 001), no schema changes required
- Database & data files persisted via host mount at ~/.chatgpt-archive/
- User settings stored in JSON file alongside database

**Testing**: 
- Frontend: Vitest + React Testing Library
- Backend: pytest (existing test suite)
- E2E: Playwright

**Target Platform**: 
- Containerized web application (Docker)
- Browser targets: Modern evergreen browsers (Chrome, Firefox, Safari, Edge - last 2 versions)
- Deployment: Docker containers on Linux servers

**Project Type**: Web application (frontend + backend API)

**Performance Goals**: 
- Search response time: <500ms (matches CLI requirement from constitution)
- Page load time: <2s initial, <500ms navigation
- UI interactions: <100ms response time
- Import operations: Background processing, progress indication

**Constraints**: 
- MUST use existing Python chatgpt_archive package (preserve CLI-first principle)
- MUST preserve SQLite database compatibility (single-file, portable)
- MUST support offline deployment (no external service dependencies except optional OpenAI API for embeddings)
- MUST maintain all export formats (md, json, yaml, html, xml, csv, xlsx)
- UI framework MUST provide consistent design system/components (using shadcn/ui)
- Single-user deployment, no authentication (assumes trusted network environment)
- Data persisted to ~/.chatgpt-archive/ for easy backup and portability

**Scale/Scope**: 
- Single-user personal deployment (no multi-tenancy)
- Handle archives with 1000+ conversations efficiently
- Support concurrent read operations, single-writer (SQLite limitation acceptable)
- ~15-20 UI screens/views covering all CLI functionality plus favorites/settings

**Real-Time Communication**:
- Server-Sent Events (SSE) for progress updates during import and embedding generation
- EventSource API on frontend with automatic reconnection

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Data-First Architecture
- **Status**: PASS
- Web UI operates via API that uses existing chatgpt_archive library
- Original JSON export remains untouched, database is derived index
- No new storage layer introduced

### ✅ Principle II: CLI-First Interface
- **Status**: PASS  
- All CLI functionality from 001 already implemented and working
- Web UI is an additional interface layer on top of existing CLI
- Satisfies "before any GUI" requirement (CLI came first in 001)

### ✅ Principle III: Fast Search & Retrieval
- **Status**: PASS (with monitoring requirement)
- Web UI calls existing search backend which meets <500ms requirement
- Must include performance monitoring in UI (loading states, timings)
- No additional performance overhead expected from REST API layer

### ✅ Principle IV: Format-Agnostic Export
- **Status**: PASS
- Constitution mandates minimum 5 formats (md, json, yaml, html, xml) — all supported ✅
- Feature 001 already extended with CSV and Excel — web UI exposes all 7 existing formats
- Export handled by existing exporters, served as file downloads

### ⚠️  Principle V: Simplicity & Composability
- **Status**: CONDITIONAL PASS - Requires justification
- **New complexity introduced**: Web framework, API layer, Docker orchestration, frontend build system
- **Justification**: 
  - User explicitly requested web UI with Docker deployment
  - Web UI significantly improves accessibility and user experience vs CLI for non-technical users
  - Maintains composability: API can be consumed by other clients, frontend is decoupled
  - Docker containers provide deployment simplicity
- **Mitigation**: 
  - Reuse existing Python library (no logic duplication)
  - Minimal API layer (thin adapter over CLI functions — adapter pattern, not logic duplication)
  - Use framework with built-in component system (avoid custom design system)
  - Single Docker Compose file for entire stack
  - **Alternative considered and rejected**: Flask + Jinja2 SSR would be simpler but cannot deliver the rich client-side interactions required (debounced search, SSE progress bars, optimistic updates, virtualized lists) without essentially reimplementing a SPA framework
  - **Complexity budget**: 3 runtime services maximum (API, web, nginx); no message queue, no cache layer, no background worker process

### Summary
**GATE RESULT**: ✅ **PASS** - All principles satisfied. Complexity addition (Principle V) is justified by explicit user requirement and improves accessibility while maintaining architectural integrity.

## Clarifications from Spec Refinement

The following clarifications were resolved during specification review (2026-02-12):

1. **Authentication Model**: Single-user personal deployment with no authentication. System assumes trusted network environment (localhost or private network).

2. **Architecture Pattern**: Separate backend and frontend communicating via REST API. Backend is FastAPI (Python), frontend is Next.js (React/TypeScript).

3. **Database Persistence**: SQLite database and all data files persist to host directory mounted at ~/.chatgpt-archive/ (or platform equivalent). This enables easy backup, data portability, and survival across container restarts.

4. **UI Component Library**: shadcn/ui with Tailwind CSS. Copy-paste accessible components built on Radix UI primitives. No heavy npm dependencies, full customization control.

5. **Progress Communication**: Server-Sent Events (SSE) for real-time progress updates during import and embedding generation. Frontend uses EventSource API with automatic reconnection.

6. **User Settings**: Persistent settings stored in JSON file alongside database. Includes UI preferences, default export format, OpenAI API credentials, and other configuration.

7. **Favorites Feature**: Users can mark conversations as favorites for quick re-access without repeated searching. Favorites view shows starred conversations.

## Project Structure

### Documentation (this feature)

```text
specs/002-web-ui/
├── plan.md              # This file
├── research.md          # Phase 0: Technology choices for frontend framework & component library
├── data-model.md        # Phase 1: UI state models, API request/response schemas
├── quickstart.md        # Phase 1: Setup and development guide
└── contracts/           # Phase 1: OpenAPI spec, component contracts
    ├── api.yaml         # REST API specification
    └── components.md    # Frontend component architecture
```

### Source Code (repository root)

```text
# Web application structure
api/
├── main.py                    # FastAPI application entry point
├── routers/
│   ├── __init__.py
│   ├── conversations.py       # Conversation CRUD endpoints
│   ├── search.py              # Search endpoints
│   ├── export.py              # Export endpoints
│   ├── tags.py                # Tag management endpoints
│   ├── favorites.py           # Favorites management endpoints
│   ├── settings.py            # User settings endpoints
│   ├── embeddings.py          # Embedding generation endpoints
│   └── progress.py            # SSE progress stream endpoints
├── models/
│   ├── __init__.py
│   ├── requests.py            # Pydantic request models
│   └── responses.py           # Pydantic response models
├── services/
│   ├── __init__.py
│   ├── archive_service.py     # Wrapper around chatgpt_archive library
│   └── settings_service.py    # User settings persistence
├── middleware/
│   ├── __init__.py
│   └── cors.py                # CORS configuration
└── tests/
    ├── __init__.py
    ├── test_conversations.py
    ├── test_search.py
    ├── test_favorites.py
    ├── test_settings.py
    └── test_export.py

web/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Layout.tsx
│   │   ├── conversations/
│   │   │   ├── ConversationList.tsx
│   │   │   ├── ConversationView.tsx
│   │   │   └── ConversationCard.tsx
│   │   ├── search/
│   │   │   ├── SearchBar.tsx
│   │   │   ├── SearchResults.tsx
│   │   │   └── SearchFilters.tsx
│   │   ├── import/
│   │   │   ├── ImportDialog.tsx
│   │   │   └── ImportProgress.tsx
│   │   ├── export/
│   │   │   └── ExportDialog.tsx
│   │   ├── tags/
│   │   │   ├── TagList.tsx
│   │   │   ├── TagEditor.tsx
│   │   │   └── TagBadge.tsx
│   │   ├── favorites/
│   │   │   ├── FavoriteButton.tsx
│   │   │   └── FavoritesList.tsx
│   │   ├── settings/
│   │   │   ├── SettingsForm.tsx
│   │   │   └── ApiCredentials.tsx
│   │   └── common/
│   │       ├── Button.tsx         # shadcn/ui components
│   │       ├── Card.tsx
│   │       ├── Modal.tsx
│   │       ├── LoadingSpinner.tsx
│   │       └── ProgressBar.tsx    # For SSE progress display
│   ├── pages/
│   │   ├── index.tsx              # Home/conversation list
│   │   ├── favorites.tsx          # Favorites view
│   │   ├── search.tsx             # Search page
│   │   ├── conversation/[id].tsx  # Conversation detail
│   │   ├── import.tsx             # Import page
│   │   └── settings.tsx           # Settings page
│   ├── services/
│   │   └── api.ts                 # API client
│   ├── hooks/
│   │   ├── useConversations.ts
│   │   ├── useSearch.ts
│   │   ├── useTags.ts
│   │   ├── useFavorites.ts
│   │   ├── useSettings.ts
│   │   └── useSSE.ts              # Server-Sent Events hook
│   ├── types/
│   │   └── index.ts               # TypeScript type definitions
│   ├── styles/
│   │   └── globals.css
│   └── utils/
│       ├── formatters.ts
│       └── constants.ts
├── public/
│   └── favicon.ico
├── package.json
├── tsconfig.json
└── next.config.js (or equivalent framework config)

# Docker configuration
docker/
├── api.Dockerfile         # Backend container
├── web.Dockerfile         # Frontend container (production: static export served by nginx)
└── nginx.conf             # Production reverse proxy (dev uses Next.js dev server directly)

docker-compose.yml         # Orchestration for entire stack

# Data directory (host mount)
~/.chatgpt-archive/        # Host directory for data persistence
├── chatgpt.db             # SQLite database
├── settings.json          # User settings
└── uploads/               # Uploaded archive files

# Shared/existing
chatgpt_archive/           # Existing Python package (unchanged)
tests/                     # Existing tests (unchanged)
```

**Structure Decision**: Web application architecture with separate frontend and backend. The API serves as a thin REST adapter (adapter pattern — not logic duplication per FR-012) around the existing `chatgpt_archive` Python library, while the frontend provides the user interface. Docker Compose orchestrates both services. Data persists to ~/.chatgpt-archive/ on the host for portability. Server-Sent Events enable real-time progress updates. This structure maintains clean separation of concerns and allows independent scaling/development of frontend and backend.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Next.js framework + TypeScript build | User explicitly requested web UI with beautiful, consistent UX; Next.js provides routing, SSR, optimizations | Plain HTML/CSS insufficient for rich interactions, component consistency, and state management across 15-20 views |
| FastAPI/REST layer | Decouple frontend from Python backend, enable HTTP-based access | Direct Python CLI integration from browser impossible; WebAssembly Python too experimental for production |
| Docker containers | User explicitly requested Docker deployment | Manual setup would be error-prone; Docker provides consistent environment and easy deployment |
| shadcn/ui component library | Needed for accessible, consistent design system without custom CSS framework | Building custom components would be time-consuming and less accessible; other libraries (MUI, Chakra) add heavier dependencies |
| Server-Sent Events (SSE) | Real-time progress updates for long operations with simpler architecture than WebSockets | Polling adds unnecessary server load and worse UX; WebSockets overkill for one-way communication |

---

## Post-Design Constitution Check (Phase 1 Complete)

*Re-evaluation after research.md, data-model.md, contracts/, and quickstart.md are complete.*

### ✅ Principle I: Data-First Architecture
- **Status**: PASS (confirmed)
- **Design validation**: 
  - API endpoints (see [contracts/api.yaml](contracts/api.yaml)) wrap existing `chatgpt_archive` library
  - No new database tables or schema changes
  - SQLite database remains single source of truth
  - Data model ([data-model.md](data-model.md)) confirms reuse of existing schema

### ✅ Principle II: CLI-First Interface  
- **Status**: PASS (confirmed)
- **Design validation**:
  - All API endpoints map directly to existing CLI commands
  - FastAPI routes in [contracts/api.yaml](contracts/api.yaml) expose same functionality
  - CLI remains fully functional, web UI is additive

### ✅ Principle III: Fast Search & Retrieval
- **Status**: PASS (confirmed)
- **Design validation**:
  - Search endpoint calls existing `search.py` module (<500ms)
  - Frontend uses debouncing (500ms) to avoid excessive API calls
  - React Query caching reduces redundant requests
  - Next.js component architecture will include loading states
  - SSE provides real-time feedback for long operations

### ✅ Principle IV: Format-Agnostic Export
- **Status**: PASS (confirmed)
- **Design validation**:
  - Export endpoint supports all 7 formats: md, json, yaml, html, xml, csv, xlsx
  - Next.js ExportDialog component provides format selection UI
  - No new exporters added, reuses existing `exporters/` modules
  - Downloads handled via FastAPI file responses

### ✅ Principle V: Simplicity & Composability
- **Status**: PASS (justified complexity validated)
- **Design validation**:
  - Technology stack finalized (see Clarifications section above):
    - **Next.js**: Modern React framework, SSR, routing built-in, TypeScript support
    - **shadcn/ui + Tailwind**: Copy-paste components, no heavy library dependencies
    - **FastAPI**: Minimal API layer, auto-generates OpenAPI docs
    - **Server-Sent Events**: Simpler than WebSockets for one-way progress updates
    - **Vitest + Playwright**: Modern testing tools
  - API is RESTful, can be consumed by other clients (composability maintained)
  - Frontend and backend are decoupled (can evolve independently)
  - Single `docker-compose.yml` for deployment (simplicity)
  - Data persists to ~/.chatgpt-archive/ for easy backup
  - **No custom design system built** (uses shadcn/ui off-the-shelf)

### Additional Checks

#### Data Integrity (Constitution)
- **Status**: PASS
- Database validation happens at API layer (Pydantic schemas)
- Import endpoint preserves idempotency (reuses existing importer)
- No destructive operations without confirmation (delete requires user confirmation)

#### Export Formats (Constitution)
- **Status**: PASS
- All required formats supported: ✅ Markdown, ✅ JSON, ✅ YAML, ✅ HTML, ✅ XML, ✅ CSV, ✅ XLSX
- Export API endpoint documented in [contracts/api.yaml](contracts/api.yaml)

### Summary
**POST-DESIGN GATE RESULT**: ✅ **PASS**

All constitutional principles remain satisfied after technology selection and architecture design:
1. ✅ Data-First Architecture preserved
2. ✅ CLI-First Interface maintained (web UI is additive)
3. ✅ Fast Search & Retrieval designed for <500ms
4. ✅ Format-Agnostic Export with all 7 formats
5. ✅ Simplicity & Composability with justified, minimal complexity

**Technology Stack** (finalized 2026-02-12):
- **Backend**: FastAPI + Uvicorn (Python 3.11+)
- **Frontend**: Next.js 14+ (React/TypeScript)
- **UI Components**: shadcn/ui + Tailwind CSS
- **Real-time**: Server-Sent Events (SSE)
- **Testing**: Vitest + React Testing Library + Playwright
- **Deployment**: Docker + Docker Compose
- **Data Persistence**: Host mount at ~/.chatgpt-archive/

**Architecture Principles**:
- Separate backend and frontend communicating via REST API
- Single-user personal deployment (no authentication)
- Reuse existing chatgpt_archive Python library (no logic duplication)
- Favorites and user settings for improved organization
- Real-time progress updates via SSE

**No architectural concerns** identified. Specification is complete and ready for Phase 0 (research.md), Phase 1 (data-model.md, contracts/, quickstart.md), and Phase 2 (tasks.md generation via `/speckit.tasks`).
