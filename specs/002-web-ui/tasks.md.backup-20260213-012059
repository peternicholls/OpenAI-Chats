# Tasks: Web UI for ChatGPT Archive

**Input**: Design documents from `/specs/002-web-ui/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT included (not requested in specification).

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
- [ ] T004 [P] Configure Python linting (ruff) and formatting (black) in api/
- [x] T005 [P] Configure TypeScript/ESLint/Prettier in web/
- [x] T006 [P] Add .gitignore for api/ (venv, __pycache__, .env)
- [x] T007 [P] Add .gitignore for web/ (node_modules, .next, .env.local)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Create FastAPI application entry point in api/main.py with basic app initialization
- [x] T009 [P] Setup API routing structure with router imports in api/routers/__init__.py
- [x] T010 [P] Configure CORS middleware in api/middleware/cors.py with localhost:3000 origin
- [x] T011 [P] Create Pydantic base models in api/models/responses.py (ConversationSummary, Message, PaginatedResponse, ErrorResponse)
- [x] T012 [P] Create Pydantic request models in api/models/requests.py (SearchRequest, TagRequest, ExportRequest)
- [x] T013 Create archive service adapter in api/services/archive_service.py (adapter pattern over chatgpt_archive library — not logic duplication per FR-012)
- [x] T014 [P] Create settings service in api/services/settings_service.py for persistent user settings in ~/.chatgpt-archive/settings.json
- [x] T015 Add health check endpoint in api/routers/health.py (GET /api/health)
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
- [ ] T171 Validate SQLite schema compatibility: verify API can read existing feature 001 database without migration
- [ ] T172 [P] Add settings loading on FastAPI startup in api/main.py (load ~/.chatgpt-archive/settings.json if exists)
- [ ] T173 [P] Add startup warning log if server binds to 0.0.0.0 (security: non-localhost exposure)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Import and View Conversations (Priority: P1) 🎯 MVP

**Goal**: Users can import ChatGPT archives and browse conversation history through the web interface

**Independent Test**: Upload a ChatGPT export ZIP, verify import completes, browse conversation list, view individual conversation details

### Implementation for User Story 1

#### Backend API

- [x] T034 [P] [US1] Create conversation router in api/routers/conversations.py with GET /api/conversations endpoint (single endpoint, query params: offset, limit, sort, order, tag_filter)
- [x] T035 [P] [US1] Add GET conversation by ID endpoint in api/routers/conversations.py
- [x] T036 [P] [US1] Add DELETE conversation endpoint in api/routers/conversations.py
- [x] T037 [P] [US1] Create import router in api/routers/import.py with POST import endpoint
- [x] T038 [US1] Add import progress tracking with in-memory state in api/services/archive_service.py
- [x] T039 [P] [US1] Create SSE progress stream endpoint in api/routers/progress.py (GET /api/import/progress with EventSource support)
- [x] T040 [US1] (depends on T013) Integrate chatgpt_archive.importer.Importer in archive_service.py: instantiate Importer, call import_archive(zip_path, db_path), wire progress callbacks
- [x] T041 [US1] Add file upload handling (multipart/form-data) in import endpoint
- [x] T042 [US1] Add pagination logic to conversation list endpoint (offset, limit parameters)
- [x] T043 [US1] Add sorting to conversation list (by date, title, message_count)
- [x] T044 [US1] Add error handling and validation for all US1 endpoints

#### Frontend UI

- [x] T045 [P] [US1] Create conversation list page in web/src/app/page.tsx (server component)
- [x] T046 [P] [US1] Create ConversationCard component in web/src/components/conversations/ConversationCard.tsx
- [x] T047 [P] [US1] Create Pagination component in web/src/components/common/Pagination.tsx
- [x] T048 [P] [US1] Create conversation detail page in web/src/app/conversation/[id]/page.tsx
- [x] T049 [P] [US1] Create MessageBubble component in web/src/components/conversations/MessageBubble.tsx
- [x] T050 [P] [US1] Create ConversationHeader component in web/src/components/conversations/ConversationHeader.tsx
- [ ] T051 [P] [US1] Create import page in web/src/app/import/page.tsx
- [ ] T052 [US1] Create ImportDialog component in web/src/components/import/ImportDialog.tsx (client component with file upload)
- [ ] T053 [US1] Create ImportProgress component in web/src/components/import/ImportProgress.tsx with progress bar
- [x] T054 [US1] (depends on T039) Implement SSE listener hook in web/src/hooks/useSSE.ts for import progress (EventSource with auto-reconnect on connection drop)
- [x] T055 [US1] Create useConversations hook in web/src/hooks/useConversations.ts with React Query
- [x] T056 [US1] Add API client methods for conversations in web/src/services/api.ts (list, getById, delete)
- [x] T057 [US1] Add API client method for import in web/src/services/api.ts (uploadArchive, getProgress)
- [x] T058 [US1] Add list filtering UI (sort dropdown, order toggle) in conversation list page
- [x] T059 [US1] Add delete confirmation dialog using shadcn/ui AlertDialog
- [x] T060 [US1] Add navigation between list and detail views
- [ ] T061 [US1] Add error states and loading skeletons using shadcn/ui Skeleton

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Run quickstart.md validation for US1 scope.

---

## Phase 4: User Story 2 - Search Conversations (Priority: P2)

**Goal**: Users can quickly find specific conversations or messages by searching through their archive

**Independent Test**: Enter search queries, verify results appear within 500ms, test result navigation

### Implementation for User Story 2

#### Backend API

- [x] T062 [P] [US2] Create search router in api/routers/search.py with POST search endpoint
- [x] T063 [US2] Integrate chatgpt_archive.search module in archive_service.py search method
- [x] T064 [US2] Add search result preview generation (snippet extraction) in search endpoint
- [x] T065 [US2] Add search filtering by date range in search endpoint
- [x] T066 [US2] Add pagination to search results
- [x] T067 [US2] Add error handling and validation for search requests

#### Frontend UI

- [x] T068 [P] [US2] Create search page in web/src/app/search/page.tsx
- [ ] T069 [P] [US2] Create SearchBar component in web/src/components/search/SearchBar.tsx (client component with debounce)
- [ ] T070 [P] [US2] Create SearchFilters component in web/src/components/search/SearchFilters.tsx (date range, search type)
- [ ] T071 [P] [US2] Create SearchResults component in web/src/components/search/SearchResults.tsx
- [ ] T072 [P] [US2] Add shadcn/ui DatePicker component for search filters
- [x] T073 [P] [US2] Add shadcn/ui Select component for search type selector
- [x] T074 [US2] Create useSearch hook in web/src/hooks/useSearch.ts with React Query and debounce
- [x] T075 [US2] Add search API client method in web/src/services/api.ts
- [ ] T076 [US2] Implement 500ms debounce logic in SearchBar input
- [ ] T077 [US2] Add search term highlighting in results
- [x] T078 [US2] Add search result click navigation to conversation detail
- [x] T079 [US2] Add empty state for no results
- [x] T080 [US2] Add global search bar in Header component linking to search page

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Run quickstart.md validation for US1+US2 scope.

---

## Phase 5: User Story 3 - Export Conversations (Priority: P3)

**Goal**: Users can export conversations in various formats for backup, sharing, or analysis

**Independent Test**: Select conversation, choose export format, verify download in correct format

### Implementation for User Story 3

#### Backend API

- [x] T081 [P] [US3] Create export router in api/routers/export.py with GET export endpoint
- [x] T082 [US3] Integrate chatgpt_archive.exporters in archive_service.py export method
- [x] T083 [US3] Add file response handling for each format (md, json, yaml, html, xml, csv, xlsx)
- [x] T084 [US3] Add Content-Disposition headers for download filenames
- [ ] T085 [US3] Add multi-conversation export support (comma-separated IDs)
- [ ] T086 [US3] Add error handling for unsupported formats and missing conversations

#### Frontend UI

- [x] T087 [P] [US3] Create ExportDialog component in web/src/components/export/ExportDialog.tsx
- [x] T088 [P] [US3] Add shadcn/ui DropdownMenu for format selection
- [x] T089 [US3] Add export button to conversation detail header
- [x] T090 [US3] Add export API client method in web/src/services/api.ts
- [x] T091 [US3] Implement file download trigger in ExportDialog
- [ ] T092 [US3] Add multi-select checkbox to conversation list for batch export
- [ ] T093 [US3] Add batch export button to conversation list
- [ ] T094 [US3] Add export success toast notification using shadcn/ui Toast
- [ ] T095 [US3] Add export error handling with user-friendly messages

**Checkpoint**: All three user stories (US1, US2, US3) should now be independently functional. Run quickstart.md validation for US1-US3 scope.

---

## Phase 6: User Story 4 - Manage Tags and Favorites (Priority: P3)

**Goal**: Users can organize conversations with tags and mark favorites for quick re-access

**Independent Test**: Create tags, apply to conversations, mark favorites, filter by tags/favorites

### Implementation for User Story 4

#### Backend API

- [x] T096 [P] [US4] Create tags router in api/routers/tags.py with GET all tags endpoint
- [x] T097 [P] [US4] Add GET tags for conversation endpoint in tags router
- [x] T098 [P] [US4] Add POST add tag endpoint in tags router
- [x] T099 [P] [US4] Add DELETE remove tag endpoint in tags router
- [x] T100 [P] [US4] Create favorites router in api/routers/favorites.py with POST toggle favorite endpoint (uses conversations.is_favorite INTEGER column)
- [x] T101 [P] [US4] Add GET favorites list endpoint in favorites router (WHERE is_favorite = 1)
- [x] T102 [US4] Extend ConversationSummary model with is_favorite: bool field in api/models/responses.py
- [x] T103 [US4] Add favorite status to conversation list query in archive_service.py
- [ ] T104 [US4] Add tag filtering to conversation list endpoint
- [ ] T105 [US4] Add validation for tag names (alphanumeric, hyphens, underscores only)

#### Frontend UI

- [ ] T106 [P] [US4] Create favorites page in web/src/app/favorites/page.tsx
- [ ] T107 [P] [US4] Create FavoriteButton component in web/src/components/favorites/FavoriteButton.tsx (star icon toggle)
- [ ] T108 [P] [US4] Create TagList component in web/src/components/tags/TagList.tsx for sidebar
- [ ] T109 [P] [US4] Create TagEditor component in web/src/components/tags/TagEditor.tsx (add/remove tags)
- [x] T110 [P] [US4] Add shadcn/ui Popover for tag editor
- [x] T111 [P] [US4] Add shadcn/ui Input with autocomplete for tag input
- [x] T112 [US4] Create useTags hook in web/src/hooks/useTags.ts with React Query
- [x] T113 [US4] Create useFavorites hook in web/src/hooks/useFavorites.ts with React Query
- [x] T114 [US4] Add tag API client methods in web/src/services/api.ts (list, add, remove)
- [x] T115 [US4] Add favorites API client methods in web/src/services/api.ts (toggle, list)
- [ ] T116 [US4] Add favorite button to ConversationCard component
- [ ] T117 [US4] Add favorite button to conversation detail header
- [ ] T118 [US4] Add tag badges to ConversationCard component
- [ ] T119 [US4] Add tag editor to conversation detail page
- [ ] T120 [US4] Add tag filter to sidebar (clickable tag list)
- [x] T121 [US4] Add favorites link to sidebar navigation
- [ ] T122 [US4] Implement optimistic updates for favorite toggle
- [ ] T123 [US4] Add tag autocomplete with existing tags

**Checkpoint**: All four user stories (US1-US4) should be independently functional. Run quickstart.md validation for US1-US4 scope.

---

## Phase 7: User Story 5 - Generate Semantic Search Embeddings (Priority: P4)

**Goal**: Users can enable semantic search by generating embeddings for conversations

**Independent Test**: Provide OpenAI API credentials, initiate embedding generation, verify semantic search works

### Implementation for User Story 5

#### Backend API

- [x] T124 [P] [US5] Create embeddings router in api/routers/embeddings.py with POST generate endpoint
- [x] T125 [P] [US5] Add GET estimate endpoint for cost calculation in embeddings router
- [x] T126 [US5] Integrate chatgpt_archive.embeddings module in archive_service.py
- [x] T127 [US5] Add background task support for embedding generation (FastAPI BackgroundTasks — in-memory only, lost on server restart; acceptable for single-user deployment)
- [ ] T128 [US5] Add SSE progress stream for embedding generation
- [ ] T129 [US5] Add semantic search support to search endpoint (search_type parameter)
- [ ] T130 [US5] Add OpenAI API key validation before starting embedding generation (make test API call to verify key validity and sufficient quota)
- [ ] T131 [US5] Add error handling for API quota exceeded, invalid credentials

#### Frontend UI

- [ ] T132 [P] [US5] Create settings page in web/src/app/settings/page.tsx
- [ ] T133 [P] [US5] Create SettingsForm component in web/src/components/settings/SettingsForm.tsx
- [ ] T134 [P] [US5] Create ApiCredentials component in web/src/components/settings/ApiCredentials.tsx
- [x] T135 [P] [US5] Add shadcn/ui Tabs for settings sections
- [x] T136 [US5] Create useSettings hook in web/src/hooks/useSettings.ts with React Query
- [x] T137 [US5] Add settings API client methods in web/src/services/api.ts (get, update)
- [x] T138 [US5] Add embeddings API client methods in web/src/services/api.ts (estimate, generate, progress)
- [ ] T139 [US5] Add embedding generation UI to settings page (start button, progress bar)
- [ ] T140 [US5] Add cost estimate display before generation
- [ ] T141 [US5] Add semantic search type option to SearchFilters component
- [ ] T142 [US5] Add SSE listener for embedding progress in settings page
- [ ] T143 [US5] Add OpenAI API key input with secure storage indication
- [ ] T144 [US5] Persist user settings to backend settings service
- [ ] T145 [US5] Add "Embeddings not generated" info message in semantic search mode

**Checkpoint**: All five user stories should now be independently functional. Run quickstart.md validation for full feature scope.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T146 [P] Update README.md with project overview, features, and deployment instructions
- [ ] T147 [P] Update docs/API.md with complete API documentation (if not using OpenAPI docs)
- [ ] T148 [P] Add environment variable documentation to docker-compose.yml comments
- [ ] T149 [P] Add favicon and app metadata to web/src/app/layout.tsx
- [ ] T150 Optimize Docker images (reduce size, multi-stage builds)
- [x] T151 Add nginx configuration in docker/nginx.conf for production frontend serving
- [ ] T152 [P] Add loading states and skeletons to all data-fetching components
- [ ] T153 [P] Add responsive design breakpoints for mobile/tablet views
- [ ] T154 [P] Add dark mode support using Next.js themes and Tailwind dark mode classes
- [ ] T155 Add keyboard shortcuts for common actions (/, Ctrl+K for search)
- [ ] T156 [P] Add toast notifications for all user actions (import success, tag added, etc.)
- [ ] T157 Optimize conversation list with virtualization for 1000+ conversations (required for SC-009: up to 5000 conversations)
- [ ] T158 Add rate limiting middleware to API to prevent abuse
- [ ] T159 Add request logging middleware to API for debugging
- [ ] T160 [P] Add analytics/telemetry hooks (optional, privacy-respecting)
- [ ] T161 Run full quickstart.md validation on fresh Docker deployment
- [ ] T162 [P] Add code comments and documentation for complex functions
- [ ] T163 [P] Run linting and formatting on all code (ruff, black, eslint, prettier)
- [ ] T164 Verify all shadcn/ui components follow accessibility guidelines (ARIA labels, keyboard nav)
- [ ] T165 Add Content Security Policy headers for security
- [ ] T166 [P] Create deployment guide in docs/DEPLOYMENT.md for production
- [ ] T167 Verify data persistence across Docker container restarts
- [ ] T168 Add health check endpoints to docker-compose.yml
- [ ] T169 [P] Add troubleshooting section to docs/TROUBLESHOOTING.md
- [ ] T170 Final review and cleanup of unused dependencies
- [ ] T174 [P] Create docs/DEPLOYMENT.md with one-command Docker deployment guide and security notices
- [ ] T175 [P] Add Browserslist config in web/ and verify Chrome, Firefox, Safari, Edge (last 2 versions)
- [ ] T176 Write Playwright E2E test suite for US1 (import archive, list conversations, view detail)
- [ ] T177 [P] Write Playwright E2E test suite for US2 (search, debounce, result navigation)
- [ ] T178 [P] Write Playwright E2E test suite for US3-US5 (export, tags/favorites, embeddings)
- [ ] T179 [P] Add structured error logging (JSON to stdout for Docker log aggregation)
- [ ] T180 Conduct 3-user walkthrough test and document pain points for SC-010

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4 → US5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 but benefits from having conversations imported
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent but requires conversations to export
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Independent of US1-3
- **User Story 5 (P4)**: Can start after Foundational (Phase 2) - Enhances US2 (search) but is independent

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

Within each user story, tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1 Backend

```bash
# After Foundational completes, launch all US1 backend tasks together:
Task T034: "Create conversation router in api/routers/conversations.py"
Task T035: "Add GET conversation by ID endpoint"
Task T036: "Add DELETE conversation endpoint"
Task T037: "Create import router in api/routers/import.py"
Task T039: "Create SSE progress stream endpoint"

# All work on different files or independent functions
```

## Parallel Example: User Story 1 Frontend

```bash
# After backend APIs are done, launch frontend components in parallel:
Task T045: "Create conversation list page"
Task T046: "Create ConversationCard component"
Task T047: "Create Pagination component"
Task T048: "Create conversation detail page"
Task T049: "Create MessageBubble component"
Task T050: "Create ConversationHeader component"

# All create different component files
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T033) **← CRITICAL BLOCKER**
3. Complete Phase 3: User Story 1 (T034-T061)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Run quickstart validation (T161)
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

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (36 tasks)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (Import & View) - 28 tasks
   - **Developer B**: User Story 2 (Search) - 19 tasks
   - **Developer C**: User Story 4 (Tags & Favorites) - 28 tasks
   - **Developer D**: Setup Docker + Polish - 32 tasks
3. Integrate and test together
4. Add User Stories 3 and 5 as needed

---

## Task Count Summary

| Phase | Task Count | Parallelizable |
|-------|-----------|----------------|
| Phase 1: Setup | 7 | 5 (71%) |
| Phase 2: Foundational | 29 | 24 (83%) |
| Phase 3: User Story 1 (MVP) | 28 | 21 (75%) |
| Phase 4: User Story 2 | 19 | 13 (68%) |
| Phase 5: User Story 3 | 15 | 8 (53%) |
| Phase 6: User Story 4 | 28 | 15 (54%) |
| Phase 7: User Story 5 | 22 | 10 (45%) |
| Phase 8: Polish | 32 | 22 (69%) |
| **TOTAL** | **180** | **118 (66%)** |

**MVP Tasks** (Phases 1-3): 64 tasks  
**Full Feature Set** (Phases 1-7): 148 tasks  
**Production Ready** (All phases): 180 tasks

---

## Notes

- [P] tasks work on different files or independent functions - safe to parallelize
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No tests included (not explicitly requested in specification)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tasks reference exact file paths from plan.md structure
- All tasks are specific and actionable - ready for LLM execution
