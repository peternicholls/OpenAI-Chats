# Post Phase 4 Testing Plan

**Created**: 2026-02-15  
**Status**: ✅ Complete (2026-02-16)  
**Scope**: Backend API + Frontend Web UI (002-web-ui feature)

---

## Implementation Summary

### Test Counts

| Layer | Tests | Status |
|-------|-------|--------|
| **API Integration Tests** | 62 | ✅ Passing |
| **Frontend Unit Tests** | 55 | ✅ Passing |
| **E2E Tests (Playwright)** | 27 | ✅ Created |

### Coverage

| Layer | Coverage |
|-------|----------|
| API Backend | 82% |
| Frontend | 16% (core paths well covered) |

### Test Files Created

**API Tests** (`api/tests/`):
- `conftest.py` - Shared fixtures (async client, temp DB, sample archive)
- `test_health.py` - 2 tests
- `test_conversations.py` - 13 tests
- `test_search.py` - 10 tests
- `test_export.py` - 12 tests
- `test_import.py` - 7 tests
- `test_tags.py` - 10 tests
- `test_favorites.py` - 8 tests

**Frontend Tests** (`web/__tests__/`):
- `mocks/handlers.ts` - MSW request handlers
- `mocks/server.ts` - MSW server setup
- `utils/test-utils.tsx` - React Query wrapper
- `services/api.test.ts` - 14 tests
- `hooks/useDebounce.test.ts` - 5 tests
- `hooks/useSearch.test.ts` - 4 tests
- `components/ConversationCard.test.tsx` - 9 tests
- `components/MessageBubble.test.tsx` - 11 tests
- `components/SearchBar.test.tsx` - 12 tests

**E2E Tests** (`web/__tests__/e2e/`):
- `home.spec.ts` - 5 tests
- `conversation.spec.ts` - 5 tests
- `search.spec.ts` - 7 tests
- `import.spec.ts` - 5 tests
- `export.spec.ts` - 5 tests

### Run Commands

```bash
# API tests
source .venv/bin/activate
pytest api/tests/ -v

# Frontend unit tests
cd web && npm test

# Frontend with coverage
cd web && npm test -- --coverage

# E2E tests (uses port 3030)
cd web && npm run test:e2e
```

---

## Current Implementation Status

### What's Built

| Layer | Status | Components |
|-------|--------|------------|
| **Backend API** | ✅ Complete | FastAPI with 11 routers: conversations, embeddings, export, favorites, health, import, progress, search, settings, tags |
| **Frontend** | ✅ Complete | Next.js 16 with pages: home, conversation/[id], favorites, import, search, settings |
| **Docker** | ✅ Complete | docker-compose.yml, api.Dockerfile, web.Dockerfile, nginx.conf |
| **Core Library** | ✅ Pre-existing | chatgpt_archive (importer, exporters, search, embeddings, db) |

### Tasks Completed (from tasks.md)

- **Phase 1**: Setup - 100% (T001-T007)
- **Phase 2**: Foundational - 100% (T008-T036)
- **Phase 3**: User Story 1 (Import/View) - 100% (T037-T067)
- **Phase 4**: User Story 2 (Search) - 100% (T068-T086)
- **Phase 5**: User Story 3 (Export) - ~60% (single export works, multi-export pending)
- **Phase 6**: User Story 4 (Tags/Favorites) - ~40% (API complete, UI partially complete)
- **Phase 7**: User Story 5 (Embeddings) - ~30% (API started, UI pending)

---

## Testing Strategy

### Test Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    E2E Tests (Playwright)                   │  ← User flows
├─────────────────────────────────────────────────────────────┤
│                 Frontend Component Tests                     │  ← React components
├─────────────────────────────────────────────────────────────┤
│               Frontend Hook/Service Tests                    │  ← API clients, hooks
├─────────────────────────────────────────────────────────────┤
│                API Integration Tests                         │  ← HTTP endpoint tests
├─────────────────────────────────────────────────────────────┤
│                Python Unit Tests                             │  ← Library functions
└─────────────────────────────────────────────────────────────┘
```

### Automation Approach

#### Phase A: Infrastructure Setup (30 mins)

1. **Backend test dependencies**
   - Add pytest-asyncio, pytest-mock, httpx to api/pyproject.toml
   - Create tests/api/ directory for API-specific tests
   - Create api/tests/conftest.py with fixtures (test client, temp database)

2. **Frontend test dependencies**
   - Add to web/package.json: vitest, @testing-library/react, @testing-library/jest-dom, jsdom, msw
   - Create web/vitest.config.ts
   - Create web/__tests__/mocks/handlers.ts

3. **E2E test dependencies**
   - Add @playwright/test to web/package.json
   - Create web/playwright.config.ts
   - Create web/__tests__/e2e/ directory

#### Phase B: Priority Test Implementation (Ordered by Risk)

**Priority 1 - Critical Path (Must Pass)**
| Test | Type | Purpose |
|------|------|---------|
| API health check | Integration | Verify API starts and responds |
| Conversation list | Integration | Verify core data retrieval |
| Import archive | Integration | Verify core import flow |
| Search functionality | Integration | Verify search returns results |
| Export single | Integration | Verify export produces valid files |

**Priority 2 - Core Functionality**
| Test | Type | Purpose |
|------|------|---------|
| Frontend renders | E2E | Page loads without errors |
| Navigation works | E2E | Routes function correctly |
| Import flow E2E | E2E | Upload → Progress → Completion |
| Search flow E2E | E2E | Type → Debounce → Results |

**Priority 3 - Edge Cases**
| Test | Type | Purpose |
|------|------|---------|
| Invalid ZIP upload | Integration | Error handling |
| Empty search results | Integration | UI state handling |
| 404 conversation | Integration | Not found handling |

---

## Success Criteria

### Quantitative Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| API tests pass | 100% | pytest exit code 0 |
| Frontend tests pass | 100% | vitest exit code 0 |
| E2E tests pass | 100% | playwright exit code 0 |
| API response time | < 500ms | Health check latency |
| Page load time | < 3s | Lighthouse/manual |
| Zero critical errors | 0 bugs | Console errors, 500 responses |

### Qualitative Criteria

| Criteria | How to Verify |
|----------|---------------|
| Import completes successfully | Upload real ChatGPT ZIP, see conversations |
| Search returns relevant results | Search for known term, verify matches |
| Export produces valid files | Download each format, open/validate |
| Error messages are helpful | Trigger errors, check messages follow pattern |
| SSE progress updates work | Watch import progress bar update in real-time |

### Critical User Journeys to Validate

1. **Import Journey**: Upload ZIP → See progress → Browse results
2. **Search Journey**: Type query → See results → Click to view conversation
3. **Export Journey**: View conversation → Click export → Select format → Download file
4. **Browse Journey**: View list → Paginate → Sort → View detail → Navigate back

---

## Challenge Response Protocol

### Challenge Category: Test Infrastructure

| Issue | Response |
|-------|----------|
| Test deps won't install | Check Node/Python versions, clear cache, try specific versions |
| vitest config errors | Reference working vitest configs, check Next.js compatibility |
| Playwright browser download fails | Use npx playwright install, try single browser first |

### Challenge Category: API Tests

| Issue | Response |
|-------|----------|
| Database state conflicts | Use fresh temp database per test, add proper fixtures |
| Import tests slow | Mock file system operations, use smaller test archives |
| Async test timeouts | Increase timeout, add proper async handling |

### Challenge Category: Frontend Tests

| Issue | Response |
|-------|----------|
| Component import errors | Check alias paths, mock troublesome dependencies |
| React Query issues | Wrap in QueryClientProvider, mock api calls properly |
| Next.js App Router issues | Use appropriate testing patterns for server/client components |

### Challenge Category: E2E Tests

| Issue | Response |
|-------|----------|
| Services won't start | Test manually first, check ports, verify Docker works |
| Flaky tests | Add proper waits, increase timeouts, retry mechanism |
| State pollution | Reset database between tests, use isolated test data |

### Challenge Category: Discovered Bugs

| Severity | Response |
|----------|----------|
| **Critical** (app crashes, data loss) | Stop testing, document, fix immediately |
| **High** (feature broken) | Document with reproduction steps, add to fix list, continue |
| **Medium** (UX issue) | Document, add to polish backlog, continue |
| **Low** (cosmetic) | Note for later, continue testing |

---

## Test Execution Order

### Stage 1: Manual Smoke Test (15 mins)

Before automation, verify the app works at all:

```bash
# 1. Start services
docker-compose up -d

# 2. Verify API responds
curl http://localhost:8000/api/health

# 3. Verify frontend loads
open http://localhost:3000

# 4. Manual test: Upload a real ChatGPT export ZIP
# 5. Manual test: Search for a term
# 6. Manual test: Export a conversation
```

**Pass criteria**: All 4 manual tests complete without errors

### Stage 2: API Integration Tests (30 mins)

```bash
# Run from repo root
cd api
pip install -e ".[dev]"
pytest tests/ -v --tb=short
```

**Tests to implement/run:**
1. `test_health_endpoint` - GET /api/health returns 200
2. `test_list_conversations` - GET /api/conversations returns paginated list
3. `test_get_conversation` - GET /api/conversations/{id} returns detail
4. `test_search` - POST /api/search returns results
5. `test_export_formats` - GET /api/export/{id} for each format
6. `test_import_archive` - POST /api/import with valid ZIP

### Stage 3: Frontend Unit Tests (30 mins)

```bash
cd web
npm install
npm test
```

**Tests to implement/run:**
1. `api.test.ts` - API client methods make correct fetch calls
2. `useConversations.test.ts` - Hook manages state correctly
3. `useSearch.test.ts` - Debounce behavior works
4. `ConversationCard.test.tsx` - Renders conversation data
5. `SearchBar.test.tsx` - Input and debounce work

### Stage 4: E2E Tests (30 mins)

```bash
cd web
npx playwright test
```

**Tests to implement/run:**
1. `home.spec.ts` - Home page loads, shows conversations
2. `import.spec.ts` - Import flow completes
3. `search.spec.ts` - Search finds results
4. `export.spec.ts` - Export downloads file

---

## Test Data Requirements

### Minimal Test Archive

Create `tests/fixtures/test_archive.zip` containing:
- `conversations.json` with 3 conversations (5, 10, 20 messages each)
- `user.json` with minimal user profile

### Test Database

- Fresh SQLite database for each test run
- Pre-populated database fixture with 10 conversations for read tests

### Mock Responses

- MSW handlers for all API endpoints
- Realistic response shapes matching actual API

---

## Issue Tracking

Issues discovered during testing will be logged in this format:

```markdown
### [ISSUE-001] Brief title

**Severity**: Critical/High/Medium/Low
**Found in**: Stage X, test Y
**Reproduction**:
1. Step 1
2. Step 2
3. Expected vs Actual

**Root cause**: (if known)
**Fix**: (PR reference or inline)
**Status**: Open/Fixed/Deferred
```

---

## Execution Checklist

Pre-Test Setup:
- [ ] Verify Docker is running
- [ ] Verify ports 3000, 8000 are free
- [ ] Have a real ChatGPT export ZIP ready for manual testing

Stage 1 - Manual Smoke Test:
- [ ] API health check passes
- [ ] Frontend loads without console errors
- [ ] Can upload and import a ZIP file
- [ ] Can search and see results
- [ ] Can export a conversation

Stage 2 - API Tests:
- [ ] Test dependencies installed
- [ ] conftest.py with fixtures created
- [ ] All API tests passing

Stage 3 - Frontend Tests:
- [ ] Test dependencies installed
- [ ] vitest configured
- [ ] MSW handlers created
- [ ] All frontend tests passing

Stage 4 - E2E Tests:
- [ ] Playwright configured
- [ ] All E2E tests passing

Post-Test:
- [ ] All issues documented
- [ ] Critical issues fixed
- [ ] Test coverage report generated

---

## Expected Outcomes

### Best Case
- All manual tests pass
- 100% automated test pass rate
- No critical or high severity issues found
- Coverage > 70%

### Likely Case
- Manual tests pass with minor issues
- 90%+ automated tests pass initially
- 2-5 medium severity issues found
- Some tests need iteration to stabilize

### Worst Case
- Manual tests reveal blocking issues
- Cannot proceed to automated tests
- Must fix critical issues first
- Re-plan after fixes

---

## Resource Links

- [tasks.md](tasks.md) - Full task list with Phase 9 test tasks
- [spec.md](spec.md) - Feature requirements and acceptance criteria
- [contracts/](contracts/) - API contracts for test assertions
- [quickstart.md](quickstart.md) - Validation steps per user story

---

## Task Breakdown

### Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel with other [P] tasks

---

### Stage 0: Pre-Test Setup

- [ ] TS001 Verify Docker daemon is running
- [ ] TS002 Verify ports 3000 and 8000 are free (lsof -i :3000 -i :8000)
- [ ] TS003 Locate or create test ChatGPT export ZIP file for manual testing

---

### Stage 1: Manual Smoke Test

**Purpose**: Verify app works before investing in automation

- [ ] TS004 Start services with docker-compose up -d (or local dev servers)
- [ ] TS005 Test API health: curl http://localhost:8000/api/health returns 200
- [ ] TS006 Test frontend loads: http://localhost:3000 renders without console errors
- [ ] TS007 Test import flow: Upload ZIP, watch progress, verify conversations appear
- [ ] TS008 Test search flow: Enter query, verify debounce, check results display
- [ ] TS009 Test export flow: Open conversation, export as Markdown, verify download
- [ ] TS010 Document any issues found in Stage 1

**Gate**: If TS005-TS009 fail, stop and fix before proceeding

---

### Stage 2: API Test Infrastructure

**Purpose**: Set up backend testing framework

- [ ] TS011 Add test dependencies to api/pyproject.toml (pytest-asyncio>=0.23, pytest-mock>=3.12, httpx>=0.27)
- [ ] TS012 [P] Create api/tests/ directory structure
- [ ] TS013 [P] Create api/tests/conftest.py with fixtures (test_client, temp_db, sample_conversation)
- [ ] TS014 [P] Create api/tests/fixtures/sample_archive/ with minimal conversations.json
- [ ] TS015 Create api/tests/fixtures/test_archive.zip from sample_archive/
- [ ] TS016 Verify pytest runs with: cd api && pytest --collect-only

---

### Stage 2B: API Integration Tests

**Purpose**: Test all API endpoints

- [ ] TS017 [P] Write test_health.py: test_health_endpoint returns 200 with status
- [ ] TS018 [P] Write test_conversations.py: test_list_empty returns empty array
- [ ] TS019 [P] Write test_conversations.py: test_list_paginated returns limit/offset
- [ ] TS020 [P] Write test_conversations.py: test_get_by_id returns conversation detail
- [ ] TS021 [P] Write test_conversations.py: test_get_not_found returns 404
- [ ] TS022 [P] Write test_search.py: test_search_basic returns matching results
- [ ] TS023 [P] Write test_search.py: test_search_empty_query returns error or empty
- [ ] TS024 [P] Write test_export.py: test_export_markdown returns valid markdown
- [ ] TS025 [P] Write test_export.py: test_export_json returns valid JSON
- [ ] TS026 [P] Write test_export.py: test_export_invalid_format returns 400
- [ ] TS027 [P] Write test_import.py: test_import_valid_zip creates conversations
- [ ] TS028 [P] Write test_import.py: test_import_invalid_file returns error
- [ ] TS029 [P] Write test_tags.py: test_list_tags returns tag array
- [ ] TS030 [P] Write test_favorites.py: test_toggle_favorite updates status
- [ ] TS031 Run full API test suite: pytest api/tests/ -v
- [ ] TS032 Document any API issues found

**Gate**: All API tests must pass before Stage 3

---

### Stage 3: Frontend Test Infrastructure

**Purpose**: Set up frontend testing framework

- [ ] TS033 Add test deps to web/package.json: vitest, @testing-library/react, @testing-library/jest-dom, @testing-library/user-event, jsdom, msw
- [ ] TS034 [P] Create web/vitest.config.ts with jsdom environment
- [ ] TS035 [P] Create web/vitest.setup.ts with jest-dom matchers
- [ ] TS036 [P] Create web/__tests__/ directory structure
- [ ] TS037 Create web/__tests__/mocks/handlers.ts with MSW handlers for API
- [ ] TS038 [P] Create web/__tests__/mocks/server.ts with MSW server setup
- [ ] TS039 Add "test" script to web/package.json: "vitest run"
- [ ] TS040 Verify vitest runs with: cd web && npm test -- --passWithNoTests

---

### Stage 3B: Frontend Unit Tests

**Purpose**: Test API client and React hooks

- [ ] TS041 [P] Write api.test.ts: test_listConversations makes correct fetch
- [ ] TS042 [P] Write api.test.ts: test_getConversation fetches by ID
- [ ] TS043 [P] Write api.test.ts: test_search sends POST with query
- [ ] TS044 [P] Write api.test.ts: test_exportConversation returns blob
- [ ] TS045 [P] Write useConversations.test.ts: test_loading_state shows loading
- [ ] TS046 [P] Write useConversations.test.ts: test_success_state returns data
- [ ] TS047 [P] Write useSearch.test.ts: test_debounce waits 500ms
- [ ] TS048 [P] Write useSearch.test.ts: test_results updates on response
- [ ] TS049 Run frontend unit tests: npm test
- [ ] TS050 Document any frontend issues found

---

### Stage 3C: Frontend Component Tests

**Purpose**: Test React components render correctly

- [ ] TS051 [P] Write ConversationCard.test.tsx: renders title and date
- [ ] TS052 [P] Write ConversationCard.test.tsx: renders message count
- [ ] TS053 [P] Write MessageBubble.test.tsx: renders user message style
- [ ] TS054 [P] Write MessageBubble.test.tsx: renders assistant message style
- [ ] TS055 [P] Write SearchBar.test.tsx: renders input field
- [ ] TS056 [P] Write SearchBar.test.tsx: calls onChange on type
- [ ] TS057 [P] Write Pagination.test.tsx: renders page numbers
- [ ] TS058 Run component tests: npm test
- [ ] TS059 Document any component issues found

**Gate**: All frontend tests must pass before Stage 4

---

### Stage 4: E2E Test Infrastructure

**Purpose**: Set up Playwright for end-to-end testing

- [ ] TS060 Add @playwright/test to web/package.json devDependencies
- [ ] TS061 Run npx playwright install chromium (single browser for speed)
- [ ] TS062 Create web/playwright.config.ts with base URL http://localhost:3000
- [ ] TS063 [P] Create web/__tests__/e2e/ directory
- [ ] TS064 Add "test:e2e" script to web/package.json: "playwright test"
- [ ] TS065 Verify playwright runs: npm run test:e2e -- --list

---

### Stage 4B: E2E Tests

**Purpose**: Test complete user journeys

- [ ] TS066 Write home.spec.ts: page loads and shows header
- [ ] TS067 [P] Write home.spec.ts: conversation list displays items
- [ ] TS068 [P] Write conversation.spec.ts: click opens detail view
- [ ] TS069 [P] Write conversation.spec.ts: messages render correctly
- [ ] TS070 [P] Write search.spec.ts: typing shows results after debounce
- [ ] TS071 [P] Write search.spec.ts: clicking result navigates to conversation
- [ ] TS072 [P] Write import.spec.ts: upload triggers progress display
- [ ] TS073 [P] Write export.spec.ts: export button downloads file
- [ ] TS074 Start services for E2E: docker-compose up -d (or dev servers)
- [ ] TS075 Run E2E tests: npm run test:e2e
- [ ] TS076 Document any E2E issues found

---

### Stage 5: Issue Resolution

**Purpose**: Fix discovered bugs by severity

- [ ] TS077 Triage all documented issues by severity (Critical/High/Medium/Low)
- [ ] TS078 Fix all Critical issues (app crashes, data loss)
- [ ] TS079 Fix all High issues (feature broken)
- [ ] TS080 Re-run failed tests after fixes
- [ ] TS081 [P] Document Medium issues as tech debt for Phase 8
- [ ] TS082 [P] Document Low issues as backlog items

---

### Stage 6: Test Coverage & Reporting

**Purpose**: Generate coverage reports and summary

- [ ] TS083 Run API tests with coverage: pytest --cov=api --cov-report=html
- [ ] TS084 [P] Run frontend tests with coverage: npm test -- --coverage
- [ ] TS085 [P] Generate test summary report in specs/002-web-ui/test-results.md
- [ ] TS086 Update testing-plan.md execution checklist with results

---

## Task Summary

| Stage | Tasks | Parallelizable | Est. Time |
|-------|-------|----------------|-----------|
| Stage 0: Pre-Test Setup | 3 | 0 | 5 min |
| Stage 1: Manual Smoke | 7 | 0 | 15 min |
| Stage 2: API Infrastructure | 6 | 3 | 15 min |
| Stage 2B: API Tests | 16 | 14 | 30 min |
| Stage 3: Frontend Infrastructure | 8 | 4 | 15 min |
| Stage 3B: Frontend Unit Tests | 10 | 8 | 20 min |
| Stage 3C: Component Tests | 9 | 7 | 15 min |
| Stage 4: E2E Infrastructure | 6 | 1 | 10 min |
| Stage 4B: E2E Tests | 11 | 7 | 30 min |
| Stage 5: Issue Resolution | 6 | 2 | Variable |
| Stage 6: Coverage | 4 | 2 | 10 min |
| **TOTAL** | **86** | **48 (56%)** | **~2.5 hrs** |

---

## Execution Gates

```
Stage 0 ──► Stage 1 ──► [GATE: Smoke passes?]
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
              Stage 2/3             Fix issues
              (parallel)                │
                    │                   │
                    ▼                   │
            [GATE: Unit tests pass?] ◄──┘
                    │
                    ▼
              Stage 4 E2E
                    │
                    ▼
            [GATE: E2E passes?]
                    │
                    ▼
              Stage 5 Fixes
                    │
                    ▼
              Stage 6 Report
```

---

## Next Steps After Plan Approval

1. Execute Stage 0 (Pre-Test Setup)
2. Execute Stage 1 (Manual Smoke Test)
3. Based on results, proceed to Stage 2/3 or fix blocking issues
4. Progress through gates sequentially
5. Report final findings and coverage
