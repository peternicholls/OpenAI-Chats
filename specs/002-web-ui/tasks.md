# Tasks: Web UI for ChatGPT Archive

**Input**: Design documents from `/specs/002-web-ui/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests ARE included — see Phase 9 for comprehensive test coverage (118 test cases).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Web application architecture:
- Backend: `api/` directory
- Frontend: `web/` directory
- Docker: `docker/` directory
- Data: `~/.chatgpt-archive/` (host mount via `${HOME}/.chatgpt-archive:/data`)

**Next.js Component Guidelines**: Use server components for data fetching (pages, layouts); use client components (`'use client'`) for interactivity (forms, buttons, SSE listeners, state management).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per plan.md (api/, web/, docker/ directories)
- [x] T002 Initialize Python FastAPI project with dependencies in api/pyproject.toml
- [x] T003 [P] Initialize Next.js 14+ (React/TypeScript) project in web/ using `npx create-next-app@latest`
- [x] T004 [P] Configure Python linting (ruff) and formatting (black) in api/
- [x] T005 [P] Configure TypeScript/ESLint/Prettier in web/
- [x] T006 [P] Add .gitignore for api/ (venv, __pycache__, .env)
- [x] T007 [P] Add .gitignore for web/ (node_modules, .next, .env.local)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Create FastAPI application entry point in api/main.py with basic app initialization
- [x] T009 [P] Setup API routing structure with router imports in api/routers/__init__.py
- [x] T010 [P] Configure CORS middleware in api/middleware/cors.py (allow localhost:3000 in dev, configure via CORS_ORIGINS env var in production for Docker networking)
- [x] T011 [P] Create Pydantic base models in api/models/responses.py (ConversationSummary, Message, PaginatedResponse, ErrorResponse)
- [x] T012 [P] Create Pydantic request models in api/models/requests.py (SearchRequest, TagRequest, ExportRequest)
- [x] T013 Create archive service adapter in api/services/archive_service.py (adapter pattern over chatgpt_archive library — not logic duplication per FR-012)
- [x] T014 [P] Create settings service in api/services/settings_service.py for persistent user settings in ~/.chatgpt-archive/settings.json
- [x] T015 Add health check endpoint in api/routers/health.py (GET /api/health) - check: API responds, DB file accessible, return 200 OK with status
- [x] T016 [P] Initialize shadcn/ui CLI in web/ with Tailwind CSS (shadcn generates source files — not an npm dependency)
- [x] T017 [P] Create TypeScript types in web/src/types/index.ts matching API contracts
- [x] T018 [P] Create API client service in web/src/services/api.ts with fetch wrapper
- [x] T019 [P] Create React Query configuration in web/src/lib/react-query.ts
- [x] T020 [P] Create query keys structure in web/src/hooks/queryKeys.ts
- [x] T021 Create root layout in web/src/app/layout.tsx with Header and Sidebar
- [x] T022 [P] Create Header component in web/src/components/layout/Header.tsx
- [x] T023 [P] Create Sidebar component in web/src/components/layout/Sidebar.tsx
- [x] T024 [P] Generate shadcn/ui Button via `npx shadcn-ui add button` into web/src/components/ui/
- [x] T025 [P] Generate shadcn/ui Card via `npx shadcn-ui add card` into web/src/components/ui/
- [x] T026 [P] Generate shadcn/ui Dialog via `npx shadcn-ui add dialog` into web/src/components/ui/
- [x] T027 [P] Generate shadcn/ui Badge via `npx shadcn-ui add badge` into web/src/components/ui/
- [x] T028 [P] Add shared LoadingSpinner component in web/src/components/common/LoadingSpinner.tsx
- [x] T029 Create error boundary in web/src/app/error.tsx for graceful error handling
- [x] T030 [P] Create Dockerfile for backend in docker/api.Dockerfile (Python 3.11 slim, multi-stage build)
- [x] T031 [P] Create Dockerfile for frontend in docker/web.Dockerfile (Node 20, static export with nginx)
- [x] T032 Create docker-compose.yml with api and web services, volume mount using ${HOME}/.chatgpt-archive:/data for host data persistence
- [x] T033 [P] Create .env.example files for both api/ and web/ with required environment variables
- [x] T034_NEW [P] Add input validation middleware in api/middleware/validation.py (sanitize query params, validate request bodies)
- [x] T035_NEW [P] Configure Content Security Policy headers in api/middleware/cors.py (restrict script sources, prevent XSS)
- [x] T036_NEW Add environment variable validation on startup in api/main.py (check required vars: DB_PATH, CORS_ORIGINS)
- [x] T171 Validate SQLite schema compatibility in api/services/archive_service.py: verify conversations, messages, embeddings tables exist with expected column types (id, title, create_time, etc.)
- [x] T172 [P] Add settings loading on FastAPI startup in api/main.py (load ~/.chatgpt-archive/settings.json if exists, use defaults if missing/corrupted, log warning on parse errors)
- [x] T173 [P] Add startup warning log in api/main.py if server binds to 0.0.0.0 (log level: WARNING, format: "Security: API exposed on all interfaces (0.0.0.0)")

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Import and View Conversations (Priority: P1) 🎯 MVP

**Goal**: Users can import ChatGPT archives and browse conversation history through the web interface

**Independent Test**: Upload a ChatGPT export ZIP, verify import completes, browse conversation list, view individual conversation details

### Implementation for User Story 1

#### Backend API

- [x] T037 [P] [US1] Create conversation router in api/routers/conversations.py with GET /api/conversations endpoint (single endpoint, query params: offset, limit, sort, order, tag_filter)
- [x] T038 [P] [US1] Add GET conversation by ID endpoint in api/routers/conversations.py
- [x] T039 [P] [US1] Add DELETE conversation endpoint in api/routers/conversations.py
- [x] T040 [P] [US1] Create import router in api/routers/import.py with POST import endpoint
- [x] T041 [US1] Add import progress tracking with in-memory state in api/services/archive_service.py
- [x] T042 [P] [US1] Create SSE progress stream endpoint in api/routers/progress.py (GET /api/import/progress with EventSource support)
- [x] T043 [US1] (depends on T013) Integrate chatgpt_archive.importer.Importer in archive_service.py: instantiate Importer, call import_archive(zip_path, db_path), wire progress callbacks
- [x] T044 [US1] Add file upload handling (multipart/form-data) in import endpoint
- [x] T045 [US1] Add pagination logic to conversation list endpoint (offset, limit parameters)
- [x] T046 [US1] Add sorting to conversation list (by date, title, message_count)
- [x] T047 [US1] Add error handling and validation for all US1 endpoints

#### Frontend UI

- [x] T048 [P] [US1] Create conversation list page in web/src/app/page.tsx (server component)
- [x] T049 [P] [US1] Create ConversationCard component in web/src/components/conversations/ConversationCard.tsx
- [x] T050 [P] [US1] Create Pagination component in web/src/components/common/Pagination.tsx
- [x] T051 [P] [US1] Create conversation detail page in web/src/app/conversation/[id]/page.tsx
- [x] T052 [P] [US1] Create MessageBubble component in web/src/components/conversations/MessageBubble.tsx
- [x] T053 [P] [US1] Create ConversationHeader component in web/src/components/conversations/ConversationHeader.tsx
- [x] T054 [P] [US1] Create import page in web/src/app/import/page.tsx
- [x] T055 [US1] Create ImportDialog component in web/src/components/import/ImportDialog.tsx (client component with file upload: accept .zip only, max 500MB, show upload progress bar)
- [x] T056 [US1] Create ImportProgress component in web/src/components/import/ImportProgress.tsx with progress bar (display: file name, progress %, current step, error recovery UI)
- [x] T057 [US1] (depends on T042) Implement SSE listener hook in web/src/hooks/useSSE.ts for import progress (EventSource with auto-reconnect on connection drop)
- [x] T058 [US1] Create useConversations hook in web/src/hooks/useConversations.ts with React Query
- [x] T059 [US1] Add API client methods for conversations in web/src/services/api.ts (list, getById, delete)
- [x] T060 [US1] Add API client method for import in web/src/services/api.ts (uploadArchive, getProgress)
- [x] T061 [US1] Add list filtering UI (sort dropdown, order toggle) in conversation list page
- [x] T062 [US1] Add delete confirmation dialog using shadcn/ui AlertDialog
- [x] T063 [US1] Add navigation between list and detail views
- [x] T064 [P] [US1] Add error states for conversation list in web/src/app/page.tsx (empty state, network error, retry button)
- [x] T065 [P] [US1] Add loading skeletons for conversation list using shadcn/ui Skeleton in web/src/components/conversations/ConversationListSkeleton.tsx
- [x] T066 [P] [US1] Add error states for conversation detail in web/src/app/conversation/[id]/page.tsx (not found, network error, retry button)
- [x] T067 [P] [US1] Add error states for import in ImportDialog component (invalid file type, file too large, upload failed, corrupted ZIP)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Run quickstart.md validation for US1 scope.

---

## Phase 4: User Story 2 - Search Conversations (Priority: P2)

**Goal**: Users can quickly find specific conversations or messages by searching through their archive

**Independent Test**: Enter search queries, verify results appear within 500ms, test result navigation

### Implementation for User Story 2

#### Backend API

- [x] T068 [P] [US2] Create search router in api/routers/search.py with POST search endpoint
- [x] T069 [US2] Integrate chatgpt_archive.search module in archive_service.py search method
- [x] T070 [US2] Add search result preview generation (snippet extraction) in search endpoint
- [x] T071 [US2] Add search filtering by date range in search endpoint
- [x] T072 [US2] Add pagination to search results
- [x] T073 [US2] Add error handling and validation for search requests

#### Frontend UI

- [x] T074 [P] [US2] Create search page in web/src/app/search/page.tsx
- [ ] T075 [P] [US2] Generate shadcn/ui DatePicker components via CLI: `npx shadcn-ui add calendar popover` into web/src/components/ui/
- [ ] T076 [US2] (depends on T075) Create SearchFilters component in web/src/components/search/SearchFilters.tsx (date range using DatePicker, search type dropdown)
- [ ] T077 [US2] (depends on T075) Create SearchBar component in web/src/components/search/SearchBar.tsx (client component with 500ms debounce using lodash.debounce or custom useDebounce hook)
- [ ] T078 [P] [US2] Create SearchResults component in web/src/components/search/SearchResults.tsx
- [x] T079 [P] [US2] Add shadcn/ui Select component for search type selector
- [x] T080 [US2] Create useSearch hook in web/src/hooks/useSearch.ts with React Query and debounce
- [x] T081 [US2] Add search API client method in web/src/services/api.ts
- [ ] T082 [P] [US2] Implement search term highlighting in SearchResults using react-highlight-words library (highlight matched keywords in result snippets)
- [ ] T083 [US2] Implement 500ms debounce logic in SearchBar input (use useDebounce custom hook)
- [x] T084 [US2] Add search result click navigation to conversation detail
- [x] T085 [US2] Add empty state for no results
- [x] T086 [US2] Add global search bar in Header component linking to search page

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Run quickstart.md validation for US1+US2 scope.

---

## Phase 5: User Story 3 - Export Conversations (Priority: P3)

**Goal**: Users can export conversations in various formats for backup, sharing, or analysis

**Independent Test**: Select conversation, choose export format, verify download in correct format

### Implementation for User Story 3

#### Backend API

- [x] T087 [P] [US3] Create export router in api/routers/export.py with GET export endpoint
- [x] T088 [US3] Integrate chatgpt_archive.exporters in archive_service.py export method
- [x] T089 [US3] Add file response handling for each format (md, json, yaml, html, xml, csv, xlsx)
- [x] T090 [US3] Add Content-Disposition headers for download filenames
- [ ] T091 [US3] Add multi-conversation export support in export endpoint (accept comma-separated conversation IDs, generate combined export)
- [ ] T092 [US3] Add error handling for unsupported formats and missing conversations

#### Frontend UI

- [x] T093 [P] [US3] Create ExportDialog component in web/src/components/export/ExportDialog.tsx
- [x] T094 [P] [US3] Add shadcn/ui DropdownMenu for format selection
- [x] T095 [US3] Add export button to conversation detail header
- [x] T096 [US3] Add export API client method in web/src/services/api.ts
- [x] T097 [US3] Implement file download trigger in ExportDialog
- [ ] T098 [P] [US3] Create multi-select UI in conversation list: add checkbox to ConversationCard, track selected IDs in page state
- [ ] T099 [P] [US3] Add batch export button to conversation list toolbar (visible when conversations selected)
- [ ] T100 [P] [US3] Add export success toast notification using shadcn/ui Toast (generate and add via CLI)
- [ ] T101 [P] [US3] Add export error handling with user-friendly messages (format not supported, conversation not found, server error)
- [ ] T102 [US3] Add validation test: export all 7 formats (md, json, yaml, html, xml, csv, xlsx) with multi-conversation selection, verify each downloads correctly

**Checkpoint**: All three user stories (US1, US2, US3) should now be independently functional. Run quickstart.md validation for US1-US3 scope.

---

## Phase 6: User Story 4 - Manage Tags and Favorites (Priority: P3)

**Goal**: Users can organize conversations with tags and mark favorites for quick re-access

**Independent Test**: Create tags, apply to conversations, mark favorites, filter by tags/favorites

### Implementation for User Story 4

#### Backend API

- [x] T103 [P] [US4] Create tags router in api/routers/tags.py with GET all tags endpoint
- [x] T104 [P] [US4] Add GET tags for conversation endpoint in tags router
- [x] T105 [P] [US4] Add POST add tag endpoint in tags router
- [x] T106 [P] [US4] Add DELETE remove tag endpoint in tags router
- [x] T107 [P] [US4] Create favorites router in api/routers/favorites.py with POST toggle favorite endpoint (uses conversations.is_favorite INTEGER column)
- [x] T108 [P] [US4] Add GET favorites list endpoint in favorites router (WHERE is_favorite = 1)
- [x] T109 [US4] Extend ConversationSummary model with is_favorite: bool field in api/models/responses.py
- [x] T110 [US4] Add favorite status to conversation list query in archive_service.py
- [ ] T111 [US4] Add tag filtering to conversation list endpoint in api/routers/conversations.py (filter by tag name via query param: ?tag=work)
- [ ] T112 [US4] Add tag validation in tags router: alphanumeric + hyphens/underscores only, max 50 chars, case-insensitive uniqueness

#### Frontend UI

- [ ] T113 [P] [US4] Create favorites page in web/src/app/favorites/page.tsx (reuse ConversationCard, filter conversations where is_favorite=true)
- [ ] T114 [P] [US4] Create FavoriteButton component in web/src/components/favorites/FavoriteButton.tsx (star icon toggle, optimistic updates)
- [ ] T115 [P] [US4] Create TagList component in web/src/components/tags/TagList.tsx for sidebar (display all tags with counts, clickable to filter)
- [ ] T116 [P] [US4] Create TagEditor component in web/src/components/tags/TagEditor.tsx (add/remove tags, uses Popover + Input with autocomplete)
- [x] T117 [P] [US4] Add shadcn/ui Popover for tag editor
- [x] T118 [P] [US4] Add shadcn/ui Input with autocomplete for tag input
- [x] T119 [US4] Create useTags hook in web/src/hooks/useTags.ts with React Query
- [x] T120 [US4] Create useFavorites hook in web/src/hooks/useFavorites.ts with React Query
- [x] T121 [US4] Add tag API client methods in web/src/services/api.ts (list, add, remove)
- [x] T122 [US4] Add favorites API client methods in web/src/services/api.ts (toggle, list)
- [ ] T123 [US4] (depends on T114) Add favorite button to ConversationCard component
- [ ] T124 [US4] (depends on T114) Add favorite button to conversation detail header
- [ ] T125 [US4] (depends on T116) Add tag badges to ConversationCard component (display tags, click to filter)
- [ ] T126 [US4] (depends on T116) Add tag editor to conversation detail page header
- [ ] T127 [US4] (depends on T115) Add tag filter to sidebar (clickable tag list)
- [x] T128 [US4] Add favorites link to sidebar navigation
- [ ] T129 [US4] Implement optimistic updates for favorite toggle (update UI immediately, rollback on error)
- [ ] T130 [US4] Add tag autocomplete with existing tags (filter taglist as user types)
- [ ] T131 [P] [US4] Add error handling: display message when removing last tag from filtered view
- [ ] T132 [P] [US4] Add "no tags" empty state in sidebar TagList component
- [ ] T133 [P] [US4] Add tag limit validation: warn user if attempting to add more than 10 tags per conversation

**Checkpoint**: All four user stories (US1-US4) should be independently functional. Run quickstart.md validation for US1-US4 scope.

---

## Phase 7: User Story 5 - Generate Semantic Search Embeddings (Priority: P4)

**Goal**: Users can enable semantic search by generating embeddings for conversations

**Independent Test**: Provide OpenAI API credentials, initiate embedding generation, verify semantic search works

### Implementation for User Story 5

#### Backend API

- [x] T134 [P] [US5] Create embeddings router in api/routers/embeddings.py with POST generate endpoint
- [x] T135 [P] [US5] Add GET estimate endpoint for cost calculation in embeddings router
- [x] T136 [US5] Integrate chatgpt_archive.embeddings module in archive_service.py
- [ ] T137 [US5] Add OpenAI API key validation in embeddings router before starting generation (make test API call to verify key validity and sufficient quota)
- [x] T138 [US5] Add background task support for embedding generation (FastAPI BackgroundTasks — in-memory only, lost on server restart; acceptable for single-user deployment)
- [ ] T139 [US5] (similar to T042) Add SSE progress stream for embedding generation in api/routers/embeddings.py (reuse pattern from import progress endpoint)
- [ ] T140 [US5] Add semantic search support to search endpoint (search_type parameter: "keyword" | "semantic")
- [ ] T141 [US5] Add error handling for API quota exceeded, invalid credentials, rate limits
- [ ] T142 [P] [US5] Add cancel/pause endpoint for embedding generation in embeddings router (set cancellation flag, gracefully stop after current batch)
- [ ] T143 [P] [US5] Add cost limit safeguard in embeddings router (accept max_cost param, stop if estimate exceeds limit)
- [ ] T144 [P] [US5] Add OpenAI API key encryption for settings storage in api/services/settings_service.py (use cryptography.fernet with server-side key)

#### Frontend UI

- [ ] T145 [P] [US5] Create settings page in web/src/app/settings/page.tsx (client component for API key input)
- [ ] T146 [P] [US5] Create SettingsForm component in web/src/components/settings/SettingsForm.tsx (tabbed interface for different settings)
- [ ] T147 [P] [US5] Create ApiCredentials component in web/src/components/settings/ApiCredentials.tsx (password input for API key, test connection button)
- [x] T148 [P] [US5] Add shadcn/ui Tabs for settings sections
- [x] T149 [US5] Create useSettings hook in web/src/hooks/useSettings.ts with React Query
- [x] T150 [US5] Add settings API client methods in web/src/services/api.ts (get, update)
- [x] T151 [US5] Add embeddings API client methods in web/src/services/api.ts (estimate, generate, progress)
- [ ] T152 [US5] Add embedding generation UI to settings page (start button, progress bar, cancel button)
- [ ] T153 [US5] Add cost estimate display before generation (show: total messages, estimated tokens, cost in USD, confirm button)
- [ ] T154 [US5] Add semantic search type option to SearchFilters component (radio group: keyword/semantic)
- [ ] T155 [US5] (depends on T139) Add SSE listener for embedding progress in settings page (reuse useSSE hook pattern)
- [ ] T156 [US5] Add OpenAI API key input with secure storage indication (show lock icon, "encrypted at rest" message)
- [ ] T157 [US5] Persist user settings to backend settings service (save on change, optimistic updates)
- [ ] T158 [US5] Add "Embeddings not generated" info message in semantic search mode (suggest going to settings)
- [ ] T159 [P] [US5] Add cost limit input to embedding generation UI (max spend in USD, default $5.00)
- [ ] T160 [P] [US5] Add resume support UI: detect incomplete embedding generation, offer "Resume" button

**Checkpoint**: All five user stories should now be independently functional. Run quickstart.md validation for full feature scope.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

**Note**: Priority markers: P1 = critical for launch, P2 = nice-to-have, P3 = optional

- [ ] T161 [P] Update README.md with project overview, features, and deployment instructions
- [ ] T162 [P] Update docs/API.md with complete API documentation (if not using OpenAPI docs)
- [ ] T163 [P] Add environment variable documentation to docker-compose.yml comments
- [ ] T164 [P] Add favicon and app metadata to web/src/app/layout.tsx
- [ ] T165 [P] Optimize Docker images (reduce size below 500MB total, multi-stage builds)
- [x] T166 Add nginx configuration in docker/nginx.conf for production frontend serving
- [ ] T167 [P] [Priority: P2] Add loading states and skeletons to all data-fetching components (nice-to-have UX polish)
- [ ] T168 [P] [Priority: P2] Add responsive design breakpoints for mobile/tablet views (optional unless targeting mobile users)
- [ ] T169 [P] [Priority: P2] Add dark mode support using Next.js themes and Tailwind dark mode classes (UX polish)
- [ ] T170 [Priority: P2] Add keyboard shortcuts for common actions (/, Ctrl+K for search) (power user feature)
- [ ] T171 [P] [Priority: P2] Add toast notifications for all remaining user actions (import success, tag added, etc.)
- [ ] T172 [Priority: P1] Optimize conversation list with virtualization for 1000+ conversations (REQUIRED for SC-009: render 5000+ items with <16ms frame time, use react-window or @tanstack/react-virtual)
- [ ] T173 [Priority: P1] Add rate limiting middleware in api/middleware/rate_limit.py (100 requests/minute per IP, 429 status on exceed)
- [ ] T174 Add request logging middleware in api/middleware/logging.py (JSON format to stdout for Docker log aggregation: timestamp, method, path, status, duration_ms)
- [ ] T175 [P] [Priority: P3] Add analytics/telemetry hooks (optional, privacy-respecting, disabled by default)
- [ ] T176 [Priority: P1] Run full quickstart.md validation on fresh Docker deployment (checkpoint after each user story completion)
- [ ] T177 [P] Add code comments and documentation for complex functions (focus on archive_service.py, embedding logic)
- [ ] T178 [P] Run linting and formatting on all code (ruff, black, eslint, prettier)
- [ ] T179 [Priority: P1] Verify all shadcn/ui components follow accessibility guidelines (test: all interactive elements have ARIA labels, verify VoiceOver/NVDA screen reader compatibility, ensure keyboard-only navigation works for all workflows)
- [ ] T180 [Priority: P1] Add Content Security Policy headers in api/middleware/cors.py (restrict script-src, style-src to 'self', prevent inline scripts except for Next.js hydration)
- [ ] T181 [P] Create deployment guide in docs/DEPLOYMENT.md (one-command Docker deployment with security notices: 0.0.0.0 exposure, default credentials warnings)
- [ ] T182 [Priority: P1] Verify data persistence across Docker container restarts (test: stop/start containers, verify ~/.chatgpt-archive/archive.db and settings.json survive)
- [ ] T183 Add health check endpoints to docker-compose.yml (api: wget http://localhost:8000/api/health, interval: 30s, timeout: 10s, retries: 3)
- [ ] T184 [P] Add troubleshooting section to docs/TROUBLESHOOTING.md (common issues: port 3000/8000 conflicts, permission denied on volume mount, CORS errors)
- [ ] T185 [P] Final review and cleanup of unused dependencies (check for orphaned imports, unused packages)
- [ ] T186 [P] Add Browserslist config in web/package.json and verify Chrome, Firefox, Safari, Edge (last 2 versions)
- [ ] T187 [Priority: P1] Conduct 3-user walkthrough test for SC-010 (document: task completion rates, avg time per task, user pain points, suggestions) and record findings for iteration

### Code Review Fixes (from Phase 1-3 Review)

**Purpose**: Address issues identified during code review of Phase 1-3 implementation

- [ ] T_CR001 [Priority: P1] Apply validation middleware functions to API routes — functions in api/middleware/validation.py exist but are not called in route handlers (validate_query_param, validate_tag_name, validate_conversation_id)
- [ ] T_CR002 [P] [Priority: P2] Add loading state during delete operation in web/src/app/conversation/[id]/page.tsx — handleDelete() should show spinner/disable button while awaiting API response
- [ ] T_CR003 [P] [Priority: P3] Standardize Python type annotations across api/ — replace mixed `Optional[str]` and `str | None` syntax with consistent `str | None` (Python 3.10+)
- [ ] T_CR004 [P] [Priority: P2] Handle SSE client disconnection in api/routers/progress.py — check for client disconnect in event_generator() loop to avoid orphaned async tasks
- [ ] T_CR005 [P] [Priority: P3] Make page size configurable in web/src/app/page.tsx — move PAGE_SIZE to user settings or environment variable instead of hardcoded constant
- [ ] T_CR006 [P] [Priority: P3] Add warning log in api/services/archive_service.py if temp file cleanup fails in import_archive_from_zip() finally block

---

## Phase 9: Test Coverage (Priority: P1) 🧪

**Purpose**: Comprehensive test suite for all layers — Python library, API backend, and frontend

**Reference**: [contracts/test-specs.md](contracts/test-specs.md) for detailed test case specifications

### Test Setup

- [ ] T188 Add test dependencies to pyproject.toml: pytest>=8.0, pytest-asyncio>=0.23, pytest-cov>=4.1, httpx>=0.27, pytest-mock>=3.12
- [ ] T189 [P] Add test dependencies to web/package.json: vitest, @testing-library/react, @testing-library/jest-dom, @testing-library/user-event, jsdom, msw
- [ ] T190 [P] Add Playwright dependencies to web/package.json: @playwright/test (for E2E tests)
- [ ] T191 [P] Create tests/conftest.py with shared fixtures: tmp_db, sample_conversation, api_client, mock_openai_client
- [ ] T192 [P] Create tests/fixtures/sample_conversation.json with minimal valid conversation (user + assistant messages)
- [ ] T193 [P] Create tests/fixtures/sample_archive/ directory with conversations.json (3 conversations), user.json
- [ ] T194 [P] Create tests/fixtures/test_archive.zip from sample_archive/ for import testing
- [ ] T195 [P] Create test data generator script in tests/fixtures/generate_test_data.py (generate conversations with varying sizes: 10, 100, 1000 messages)
- [ ] T196 [P] Create web/vitest.config.ts with jsdom environment, react plugin, coverage settings (target: 70%+)
- [ ] T197 [P] Create web/vitest.setup.ts with @testing-library/jest-dom matchers
- [ ] T198 [P] Create web/__tests__/mocks/handlers.ts with MSW request handlers for all API endpoints (conversations, search, tags, favorites, import, export, embeddings)
- [ ] T199 [P] Create web/playwright.config.ts with browser configs (chromium, webkit), base URL, test timeout
- [ ] T200 [P] Setup OpenAI API mocking in tests/conftest.py using pytest-mock (mock embeddings endpoint, return fake vectors)

### End-to-End Tests (Playwright)

- [ ] T201 Write Playwright E2E test for US1 import flow in web/__tests__/e2e/import.spec.ts (upload ZIP, wait for progress, verify conversations appear)
- [ ] T202 [P] Write Playwright E2E test for US1 conversation list in web/__tests__/e2e/conversations.spec.ts (view list, pagination, sorting)
- [ ] T203 [P] Write Playwright E2E test for US1 conversation detail in web/__tests__/e2e/conversation-detail.spec.ts (click conversation, view messages, navigate back)
- [ ] T204 [P] Write Playwright E2E test for US2 search flow in web/__tests__/e2e/search.spec.ts (type query, verify debounce, check results, click result)
- [ ] T205 [P] Write Playwright E2E test for US3 export flow in web/__tests__/e2e/export.spec.ts (open export dialog, select format, verify download)
- [ ] T206 [P] Write Playwright E2E test for US4 favorites flow in web/__tests__/e2e/favorites.spec.ts (toggle favorite, filter favorites page)
- [ ] T207 [P] Write Playwright E2E test for US4 tags flow in web/__tests__/e2e/tags.spec.ts (add tag, remove tag, filter by tag)
- [ ] T208 [P] Write Playwright E2E test for US5 embeddings flow in web/__tests__/e2e/embeddings.spec.ts (add API key, view cost estimate, start generation)
- [ ] T209 Write Playwright E2E test for data persistence in web/__tests__/e2e/persistence.spec.ts (import data, restart containers via docker-compose, verify data survives)

### Python Unit Tests (chatgpt_archive/)

#### tests/unit/test_exporters.py — 14 tests

- [ ] T210 [P] Implement EXP-001: test_markdown_export_single_conversation in tests/unit/test_exporters.py
- [ ] T211 [P] Implement EXP-002: test_markdown_export_multipart_content in tests/unit/test_exporters.py
- [ ] T212 [P] Implement EXP-003: test_json_export_structure in tests/unit/test_exporters.py
- [ ] T213 [P] Implement EXP-004: test_json_export_special_chars in tests/unit/test_exporters.py
- [ ] T214 [P] Implement EXP-005: test_yaml_export_structure in tests/unit/test_exporters.py
- [ ] T215 [P] Implement EXP-006: test_html_export_structure in tests/unit/test_exporters.py
- [ ] T216 [P] Implement EXP-007: test_html_export_xss_prevention in tests/unit/test_exporters.py
- [ ] T217 [P] Implement EXP-008: test_xml_export_structure in tests/unit/test_exporters.py
- [ ] T218 [P] Implement EXP-009: test_xml_export_special_chars in tests/unit/test_exporters.py
- [ ] T219 [P] Implement EXP-010: test_csv_export_structure in tests/unit/test_exporters.py
- [ ] T220 [P] Implement EXP-011: test_csv_export_commas_in_content in tests/unit/test_exporters.py
- [ ] T221 [P] Implement EXP-012: test_excel_export_structure in tests/unit/test_exporters.py
- [ ] T222 [P] Implement EXP-013: test_excel_export_binary in tests/unit/test_exporters.py
- [ ] T223 [P] Implement EXP-014: test_export_empty_conversation in tests/unit/test_exporters.py

#### tests/unit/test_search.py — 8 tests

- [ ] T224 [P] Implement SCH-001: test_fts_search_basic in tests/unit/test_search.py
- [ ] T225 [P] Implement SCH-002: test_fts_search_phrase in tests/unit/test_search.py
- [ ] T226 [P] Implement SCH-003: test_fts_search_no_results in tests/unit/test_search.py
- [ ] T227 [P] Implement SCH-004: test_fts_search_special_chars in tests/unit/test_search.py
- [ ] T228 [P] Implement SCH-005: test_search_with_date_filter in tests/unit/test_search.py
- [ ] T229 [P] Implement SCH-006: test_search_result_preview in tests/unit/test_search.py
- [ ] T230 [P] Implement SCH-007: test_search_match_count in tests/unit/test_search.py
- [ ] T231 [P] Implement SCH-008: test_search_performance in tests/unit/test_search.py (verify <500ms)

#### tests/unit/test_embeddings.py — 5 tests

- [ ] T232 [P] Implement EMB-001: test_estimate_tokens in tests/unit/test_embeddings.py
- [ ] T233 [P] Implement EMB-002: test_estimate_cost in tests/unit/test_embeddings.py
- [ ] T234 [P] Implement EMB-003: test_batch_messages in tests/unit/test_embeddings.py
- [ ] T235 [P] Implement EMB-004: test_store_embedding in tests/unit/test_embeddings.py
- [ ] T236 [P] Implement EMB-005: test_embedding_mock_api in tests/unit/test_embeddings.py (mock OpenAI)

### Python Integration Tests (api/)

#### tests/integration/test_api_conversations.py — 8 tests

- [ ] T216 [P] Implement API-CONV-001: test_list_conversations_empty in tests/integration/test_api_conversations.py
- [ ] T217 [P] Implement API-CONV-002: test_list_conversations_paginated in tests/integration/test_api_conversations.py
- [ ] T218 [P] Implement API-CONV-003: test_list_conversations_sorted_date in tests/integration/test_api_conversations.py
- [ ] T219 [P] Implement API-CONV-004: test_list_conversations_sorted_title in tests/integration/test_api_conversations.py
- [ ] T220 [P] Implement API-CONV-005: test_get_conversation_exists in tests/integration/test_api_conversations.py
- [ ] T221 [P] Implement API-CONV-006: test_get_conversation_not_found in tests/integration/test_api_conversations.py
- [ ] T222 [P] Implement API-CONV-007: test_delete_conversation in tests/integration/test_api_conversations.py
- [ ] T223 [P] Implement API-CONV-008: test_delete_conversation_not_found in tests/integration/test_api_conversations.py

#### tests/integration/test_api_search.py — 4 tests

- [ ] T224 [P] Implement API-SCH-001: test_search_keyword in tests/integration/test_api_search.py
- [ ] T225 [P] Implement API-SCH-002: test_search_empty_query in tests/integration/test_api_search.py
- [ ] T226 [P] Implement API-SCH-003: test_search_date_filter in tests/integration/test_api_search.py
- [ ] T227 [P] Implement API-SCH-004: test_search_limit in tests/integration/test_api_search.py

#### tests/integration/test_api_export.py — 9 tests

- [ ] T228 [P] Implement API-EXP-001: test_export_markdown in tests/integration/test_api_export.py
- [ ] T229 [P] Implement API-EXP-002: test_export_json in tests/integration/test_api_export.py
- [ ] T230 [P] Implement API-EXP-003: test_export_yaml in tests/integration/test_api_export.py
- [ ] T231 [P] Implement API-EXP-004: test_export_html in tests/integration/test_api_export.py
- [ ] T232 [P] Implement API-EXP-005: test_export_xml in tests/integration/test_api_export.py
- [ ] T233 [P] Implement API-EXP-006: test_export_csv in tests/integration/test_api_export.py
- [ ] T234 [P] Implement API-EXP-007: test_export_excel in tests/integration/test_api_export.py
- [ ] T235 [P] Implement API-EXP-008: test_export_invalid_format in tests/integration/test_api_export.py
- [ ] T236 [P] Implement API-EXP-009: test_export_not_found in tests/integration/test_api_export.py

#### tests/integration/test_api_tags.py — 6 tests

- [ ] T237 [P] Implement API-TAG-001: test_list_tags_empty in tests/integration/test_api_tags.py
- [ ] T238 [P] Implement API-TAG-002: test_list_tags_with_counts in tests/integration/test_api_tags.py
- [ ] T239 [P] Implement API-TAG-003: test_add_tag in tests/integration/test_api_tags.py
- [ ] T240 [P] Implement API-TAG-004: test_add_tag_duplicate in tests/integration/test_api_tags.py
- [ ] T241 [P] Implement API-TAG-005: test_remove_tag in tests/integration/test_api_tags.py
- [ ] T242 [P] Implement API-TAG-006: test_remove_tag_not_found in tests/integration/test_api_tags.py

#### tests/integration/test_api_favorites.py — 4 tests

- [ ] T243 [P] Implement API-FAV-001: test_toggle_favorite_on in tests/integration/test_api_favorites.py
- [ ] T244 [P] Implement API-FAV-002: test_toggle_favorite_off in tests/integration/test_api_favorites.py
- [ ] T245 [P] Implement API-FAV-003: test_list_favorites in tests/integration/test_api_favorites.py
- [ ] T246 [P] Implement API-FAV-004: test_list_favorites_empty in tests/integration/test_api_favorites.py

#### tests/integration/test_api_import.py — 4 tests

- [ ] T247 [P] Implement API-IMP-001: test_import_valid_zip in tests/integration/test_api_import.py
- [ ] T248 [P] Implement API-IMP-002: test_import_invalid_file in tests/integration/test_api_import.py
- [ ] T249 [P] Implement API-IMP-003: test_import_progress in tests/integration/test_api_import.py
- [ ] T250 [P] Implement API-IMP-004: test_import_corrupted_zip in tests/integration/test_api_import.py

#### tests/integration/test_api_settings.py — 4 tests

- [ ] T251 [P] Implement API-SET-001: test_get_settings in tests/integration/test_api_settings.py
- [ ] T252 [P] Implement API-SET-002: test_update_theme in tests/integration/test_api_settings.py
- [ ] T253 [P] Implement API-SET-003: test_update_openai_key in tests/integration/test_api_settings.py
- [ ] T254 [P] Implement API-SET-004: test_update_invalid in tests/integration/test_api_settings.py

### Frontend Tests (web/)

#### web/__tests__/services/api.test.ts — 15 tests

- [ ] T255 [P] Implement FE-API-001: test_listConversations in web/__tests__/services/api.test.ts
- [ ] T256 [P] Implement FE-API-002: test_listConversations_params in web/__tests__/services/api.test.ts
- [ ] T257 [P] Implement FE-API-003: test_getConversation in web/__tests__/services/api.test.ts
- [ ] T258 [P] Implement FE-API-004: test_getConversation_error in web/__tests__/services/api.test.ts
- [ ] T259 [P] Implement FE-API-005: test_search in web/__tests__/services/api.test.ts
- [ ] T260 [P] Implement FE-API-006: test_search_filters in web/__tests__/services/api.test.ts
- [ ] T261 [P] Implement FE-API-007: test_listTags in web/__tests__/services/api.test.ts
- [ ] T262 [P] Implement FE-API-008: test_addTag in web/__tests__/services/api.test.ts
- [ ] T263 [P] Implement FE-API-009: test_removeTag in web/__tests__/services/api.test.ts
- [ ] T264 [P] Implement FE-API-010: test_toggleFavorite in web/__tests__/services/api.test.ts
- [ ] T265 [P] Implement FE-API-011: test_uploadArchive in web/__tests__/services/api.test.ts
- [ ] T266 [P] Implement FE-API-012: test_getImportProgress in web/__tests__/services/api.test.ts
- [ ] T267 [P] Implement FE-API-013: test_exportConversation in web/__tests__/services/api.test.ts
- [ ] T268 [P] Implement FE-API-014: test_healthCheck in web/__tests__/services/api.test.ts
- [ ] T269 [P] Implement FE-API-015: test_error_handling in web/__tests__/services/api.test.ts

#### web/__tests__/hooks/useConversations.test.ts — 5 tests

- [ ] T270 [P] Implement FE-HOOK-001: test_useConversations_loading in web/__tests__/hooks/useConversations.test.ts
- [ ] T271 [P] Implement FE-HOOK-002: test_useConversations_success in web/__tests__/hooks/useConversations.test.ts
- [ ] T272 [P] Implement FE-HOOK-003: test_useConversations_refetch in web/__tests__/hooks/useConversations.test.ts
- [ ] T273 [P] Implement FE-HOOK-004: test_useConversations_error in web/__tests__/hooks/useConversations.test.ts
- [ ] T274 [P] Implement FE-HOOK-005: test_useConversation_detail in web/__tests__/hooks/useConversations.test.ts

#### web/__tests__/hooks/useSearch.test.ts — 5 tests

- [ ] T275 [P] Implement FE-HOOK-006: test_useSearch_idle in web/__tests__/hooks/useSearch.test.ts
- [ ] T276 [P] Implement FE-HOOK-007: test_useSearch_debounce in web/__tests__/hooks/useSearch.test.ts
- [ ] T277 [P] Implement FE-HOOK-008: test_useSearch_results in web/__tests__/hooks/useSearch.test.ts
- [ ] T278 [P] Implement FE-HOOK-009: test_useSearch_error in web/__tests__/hooks/useSearch.test.ts
- [ ] T279 [P] Implement FE-HOOK-010: test_useSearch_clear in web/__tests__/hooks/useSearch.test.ts

#### web/__tests__/hooks/useFavorites.test.ts — 3 tests

- [ ] T280 [P] Implement FE-HOOK-011: test_useFavorites_list in web/__tests__/hooks/useFavorites.test.ts
- [ ] T281 [P] Implement FE-HOOK-012: test_useFavorites_toggle in web/__tests__/hooks/useFavorites.test.ts
- [ ] T282 [P] Implement FE-HOOK-013: test_useFavorites_invalidate in web/__tests__/hooks/useFavorites.test.ts

#### web/__tests__/hooks/useTags.test.ts — 4 tests

- [ ] T283 [P] Implement FE-HOOK-014: test_useTags_list in web/__tests__/hooks/useTags.test.ts
- [ ] T284 [P] Implement FE-HOOK-015: test_useTags_add in web/__tests__/hooks/useTags.test.ts
- [ ] T285 [P] Implement FE-HOOK-016: test_useTags_remove in web/__tests__/hooks/useTags.test.ts
- [ ] T286 [P] Implement FE-HOOK-017: test_useTags_invalidate in web/__tests__/hooks/useTags.test.ts

#### web/__tests__/components/ConversationCard.test.tsx — 7 tests

- [ ] T287 [P] Implement FE-COMP-001: test_renders_title in web/__tests__/components/ConversationCard.test.tsx
- [ ] T288 [P] Implement FE-COMP-002: test_renders_untitled in web/__tests__/components/ConversationCard.test.tsx
- [ ] T289 [P] Implement FE-COMP-003: test_renders_date in web/__tests__/components/ConversationCard.test.tsx
- [ ] T290 [P] Implement FE-COMP-004: test_renders_message_count in web/__tests__/components/ConversationCard.test.tsx
- [ ] T291 [P] Implement FE-COMP-005: test_click_navigates in web/__tests__/components/ConversationCard.test.tsx
- [ ] T292 [P] Implement FE-COMP-006: test_favorite_icon in web/__tests__/components/ConversationCard.test.tsx
- [ ] T293 [P] Implement FE-COMP-007: test_tags_displayed in web/__tests__/components/ConversationCard.test.tsx

#### web/__tests__/components/MessageBubble.test.tsx — 6 tests

- [ ] T294 [P] Implement FE-COMP-008: test_user_message_style in web/__tests__/components/MessageBubble.test.tsx
- [ ] T295 [P] Implement FE-COMP-009: test_assistant_message_style in web/__tests__/components/MessageBubble.test.tsx
- [ ] T296 [P] Implement FE-COMP-010: test_content_rendered in web/__tests__/components/MessageBubble.test.tsx
- [ ] T297 [P] Implement FE-COMP-011: test_markdown_rendered in web/__tests__/components/MessageBubble.test.tsx
- [ ] T298 [P] Implement FE-COMP-012: test_code_highlighted in web/__tests__/components/MessageBubble.test.tsx
- [ ] T299 [P] Implement FE-COMP-013: test_empty_content in web/__tests__/components/MessageBubble.test.tsx

#### web/__tests__/components/SearchBar.test.tsx — 5 tests

- [ ] T300 [P] Implement FE-COMP-014: test_renders_input in web/__tests__/components/SearchBar.test.tsx
- [ ] T301 [P] Implement FE-COMP-015: test_typing_calls_onChange in web/__tests__/components/SearchBar.test.tsx
- [ ] T302 [P] Implement FE-COMP-016: test_clear_button in web/__tests__/components/SearchBar.test.tsx
- [ ] T303 [P] Implement FE-COMP-017: test_loading_spinner in web/__tests__/components/SearchBar.test.tsx
- [ ] T304 [P] Implement FE-COMP-018: test_placeholder in web/__tests__/components/SearchBar.test.tsx

### Test CI/CD Integration

- [ ] T305 Add npm test script to web/package.json: "test": "vitest run"
- [ ] T306 [P] Add npm test:coverage script to web/package.json: "test:coverage": "vitest run --coverage"
- [ ] T307 [P] Add npm test:watch script to web/package.json: "test:watch": "vitest"
- [ ] T308 Create .github/workflows/test.yml with Python and frontend test jobs
- [ ] T309 [P] Add pytest.ini with asyncio_mode = auto and coverage settings
- [ ] T310 Run full test suite and verify 70%+ coverage on Python, all frontend tests pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4 → US5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete
- **Test Coverage (Phase 9)**: Can begin after Foundational phase; tests can be written alongside implementation

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 but benefits from having conversations imported
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent but requires conversations to export
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Independent of US1-3
- **User Story 5 (P4)**: Can start after Foundational (Phase 2) - Enhances US2 (search) but is independent

### Test Dependencies

- **Test Setup (T188-T200)**: Must complete before writing tests
- **E2E Tests (T201-T209)**: Requires full application stack running
- **Python Unit Tests (T210-T236)**: Can run in parallel, no API dependencies
- **Python Integration Tests (T237-T254)**: Requires API endpoints to be implemented
- **Frontend Tests (T255-T304)**: Requires frontend components to be implemented
- **CI/CD Integration (T305-T310)**: Should complete after tests are passing locally

### Within Each User Story

- Backend API endpoints before frontend components that consume them
- Base components (Button, Card) before complex components that use them
- Server components before client components that depend on them
- API client methods before React hooks that use them
- Core implementation before polish/optimization

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks marked [P] can run in parallel
**Phase 2 (Foundational)**: All tasks marked [P] can run in parallel (max parallelism ~25 tasks)
**Phase 3+ (User Stories)**: Once Foundational phase completes, all user stories can start in parallel if team capacity allows
**Phase 9 (Tests)**: All unit tests can run in parallel; integration tests can run in parallel per endpoint group

Within each user story, tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1 Backend

```bash
# After Foundational completes, launch all US1 backend tasks together:
Task T037: "Create conversation router in api/routers/conversations.py"
Task T038: "Add GET conversation by ID endpoint"
Task T039: "Add DELETE conversation endpoint"
Task T040: "Create import router in api/routers/import.py"
Task T042: "Create SSE progress stream endpoint"

# All work on different files or independent functions
```

## Parallel Example: User Story 1 Frontend

```bash
# After backend APIs are done, launch frontend components in parallel:
Task T048: "Create conversation list page"
Task T049: "Create ConversationCard component"
Task T050: "Create Pagination component"
Task T051: "Create conversation detail page"
Task T052: "Create MessageBubble component"
Task T053: "Create ConversationHeader component"

# All create different component files
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T036_NEW, T171-T173) **← CRITICAL BLOCKER**
3. Complete Phase 3: User Story 1 (T037-T067)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Run quickstart validation (T176)
6. Deploy via Docker and verify data persistence
7. **Demo-ready MVP** ✅

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **Deploy/Demo (MVP!)**
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 (optional) → Test independently → Deploy/Demo
7. Polish (Phase 8) → Final production release
8. Test Coverage (Phase 9) → CI/CD ready

### Test-Driven Development (TDD) Option

For teams preferring TDD, Phase 9 can be interleaved:

1. Setup + Foundational → Foundation ready
2. Test Setup (T188-T200) → Test infrastructure ready
3. For each User Story:
   - Write integration tests first (API tests)
   - Implement API endpoints to pass tests
   - Write frontend tests
   - Implement frontend components to pass tests
4. Continuous coverage monitoring via pytest-cov and vitest coverage

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (32 + 7 = 39 tasks)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (Import & View) - 31 tasks
   - **Developer B**: User Story 2 (Search) - 19 tasks
   - **Developer C**: User Story 4 (Tags & Favorites) - 31 tasks
   - **Developer D**: Setup Docker + Polish - 27 tasks
   - **Developer E**: Test Coverage (Phase 9) - 143 tasks
3. Integrate and test together
4. Add User Stories 3 and 5 as needed

---

## Task Count Summary

| Phase | Task Count | Parallelizable | Notes |
|-------|-----------|----------------|-------|
| Phase 1: Setup | 7 | 5 (71%) | Unchanged |
| Phase 2: Foundational | 32 | 26 (81%) | +3 new security tasks, +3 improved specs |
| Phase 3: User Story 1 (MVP) | 31 | 23 (74%) | +3 error handling tasks (split T061) |
| Phase 4: User Story 2 | 19 | 13 (68%) | Reorganized, added dependencies |
| Phase 5: User Story 3 | 16 | 9 (56%) | +1 validation task, reorganized multi-export |
| Phase 6: User Story 4 | 31 | 17 (55%) | +3 error handling/validation tasks |
| Phase 7: User Story 5 | 27 | 12 (44%) | +5 safeguard tasks (cancel, cost limit, encryption) |
| Phase 8: Polish | 33 | 24 (73%) | +6 code review fixes (T_CR001-T_CR006) |
| Phase 9: Test Coverage | 143 | 136 (95%) | +13 tasks (E2E tests, test data generation, mocking) |
| **TOTAL** | **339** | **265 (78%)** | +29 tasks added overall |

**MVP Tasks** (Phases 1-3): 70 tasks (+6)  
**Full Feature Set** (Phases 1-7): 163 tasks (+15)  
**Full Feature + Tests** (Phases 1-7, 9): 306 tasks (+28)  
**Production Ready** (All phases): 339 tasks (+29)

### Phase 9 Test Breakdown

| Category | Test Count |
|----------|------------|
| Test Setup & Infrastructure | 13 (+5 new: Playwright, test data gen, mocking) |
| E2E Tests (Playwright) | 9 (NEW: moved from Phase 8 + added persistence test) |
| Python Unit Tests (exporters) | 14 |
| Python Unit Tests (search) | 8 |
| Python Unit Tests (embeddings) | 5 |
| Python Integration Tests (API) | 39 |
| Frontend Service Tests | 15 |
| Frontend Hook Tests | 17 |
| Frontend Component Tests | 18 |
| CI/CD Integration | 6 |
| **Total Test Tasks** | **143** | (+13 from original 130)

---

## Improvements Summary

### Security Enhancements (Phase 2)
- **T034_NEW**: Input validation middleware (sanitize query params, validate request bodies)
- **T035_NEW**: Content Security Policy headers (prevent XSS)
- **T036_NEW**: Environment variable validation on startup

### Specifications Added
- **T171**: SQLite schema validation with specific column checks
- **T172**: Settings loading with error handling for corrupted files
- **T173**: Security warning logs with specific format
- **T051-T053**: Import UI with file type/size limits
- **T055-T056**: Import components with detailed specs
- **T077**: Search highlighting using react-highlight-words
- **T082-T083**: Debounce implementation details
- **T091-T092**: Multi-export with combined generation
- **T111-T112**: Tag filtering and validation rules
- **T137**: OpenAI API key validation before embedding generation
- **T144**: API key encryption using cryptography.fernet
- **T172**: Virtualization with performance targets (<16ms frame time)
- **T179**: Accessibility with specific testing requirements

### Error Handling & Edge Cases
- **T064-T067**: Split from T061 - specific error states per component
- **T098-T101**: Export UI with comprehensive error messages
- **T131-T133**: Tag/favorite error scenarios and limits
- **T141-T143**: Embedding safeguards (cancel, cost limits)

### Test Infrastructure
- **T190**: Playwright setup for E2E tests
- **T194-T195**: Test data generation (ZIP files, varying sizes)
- **T200**: OpenAI API mocking setup
- **T201-T209**: Comprehensive E2E test suite covering all user stories

---

## Notes

**📋 Task List Version**: 2.1 (Updated with code review fixes)

**Recent Improvements** (29 new tasks added):
- ✅ Security: Input validation, CSP headers, environment validation
- ✅ Specifications: Detailed implementation approaches for 20+ tasks
- ✅ Error Handling: Split generic tasks into specific error scenarios
- ✅ Testing: E2E tests, test data generation, API mocking setup
- ✅ Safeguards: Embedding cost limits, cancellation, API key encryption
- ✅ Priorities: P1/P2/P3 markers on Polish tasks
- ✅ Code Review: Phase 1-3 review findings added as T_CR001-T_CR006 (validation middleware integration, loading states, type standardization, SSE cleanup)

**Task Format Requirements**:
- [P] tasks work on different files or independent functions - safe to parallelize
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **Tests ARE included** in Phase 9 (143 tasks, 131 test cases) — see [contracts/test-specs.md](contracts/test-specs.md)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tasks reference exact file paths from plan.md structure
- All tasks are specific and actionable - ready for LLM execution

### Test Coverage Targets

| Layer | Target | Tool |
|-------|--------|------|
| Python unit tests | 80%+ | pytest-cov |
| Python integration | 100% endpoints | pytest |
| Frontend services | 100% methods | vitest |
| Frontend hooks | 80%+ | vitest |
| Frontend components | 70%+ | vitest |

### Running Tests

```bash
# Python tests
pytest tests/unit -v                     # Unit tests only
pytest tests/integration -v              # Integration tests
pytest --cov --cov-report=term-missing   # With coverage

# Frontend tests
cd web && npm test                       # Run all
cd web && npm run test:coverage          # With coverage
cd web && npm run test:watch             # Watch mode
```
