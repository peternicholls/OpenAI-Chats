# Tasks: ChatGPT Archive Search & Export

**Input**: Design documents from `/specs/001-archive-search-export/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/cli.md ✓

**Tests**: Not requested in spec - test tasks omitted

**Organization**: Tasks grouped by user story for independent implementation

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1-US5) - Setup/Foundational phases have no story label
- Exact file paths included in descriptions

---

## Phase 1: Setup

**Purpose**: Project initialization and package structure

- [X] T001 Create project structure with chatgpt_archive/ package directory
- [X] T002 Create pyproject.toml with click and pyyaml dependencies
- [X] T003 [P] Create chatgpt_archive/__init__.py with version number
- [X] T004 [P] Create chatgpt_archive/__main__.py entry point
- [X] T005 [P] Create README.md with installation and usage instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database schema and core models that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Implement database connection and schema setup in chatgpt_archive/db.py
- [X] T007 [P] Create Conversation dataclass in chatgpt_archive/models.py
- [X] T008 [P] Create Message dataclass in chatgpt_archive/models.py
- [X] T009 [P] Create Attachment dataclass in chatgpt_archive/models.py
- [X] T010 Create Click command group skeleton in chatgpt_archive/cli.py

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Import Archive (Priority: P1) 🎯 MVP

**Goal**: Import ChatGPT export archive into searchable SQLite database with FTS5

**Independent Test**: Run `chatgpt-archive import ./archive/` and verify conversations accessible via `sqlite3 ~/.chatgpt-archive/chats.db "SELECT COUNT(*) FROM conversations"`

### Implementation for User Story 1

- [ ] T011 [US1] Implement JSON parsing for conversations.json in chatgpt_archive/importer.py
- [ ] T012 [US1] Implement message tree traversal to extract messages in chatgpt_archive/importer.py
- [ ] T013 [US1] Implement conversation insertion with idempotent upsert logic and fallback title (first user message or "[Untitled]") in chatgpt_archive/importer.py
- [ ] T014 [US1] Implement message batch insertion with FTS5 triggers in chatgpt_archive/importer.py
- [ ] T015 [US1] Implement attachment detection and storage in chatgpt_archive/importer.py
- [ ] T016 [US1] Add import command to CLI with progress output in chatgpt_archive/cli.py
- [ ] T017 [US1] Add --json flag support for machine-readable import output in chatgpt_archive/cli.py
- [ ] T018 [US1] Add error handling for invalid JSON and missing files in chatgpt_archive/importer.py

**Checkpoint**: User Story 1 complete - can import archive and query database directly

---

## Phase 4: User Story 2 - Search Conversations (Priority: P2)

**Goal**: Full-text search across all messages with relevance ranking and previews

**Independent Test**: Run `chatgpt-archive search "keyword"` and verify results show title, date, and context snippets

### Implementation for User Story 2

- [ ] T019 [US2] Implement FTS5 query builder with term sanitization in chatgpt_archive/search.py
- [ ] T020 [US2] Implement search result formatting with snippet generation and match count per FR-008 in chatgpt_archive/search.py
- [ ] T021 [US2] Implement date range filtering for search in chatgpt_archive/search.py
- [ ] T022 [US2] Add search command to CLI with --from/--to/--limit options in chatgpt_archive/cli.py
- [ ] T023 [US2] Add --json flag for search results output in chatgpt_archive/cli.py
- [ ] T024 [US2] Handle "no results" case with user-friendly message in chatgpt_archive/search.py

**Checkpoint**: User Stories 1-2 complete - can import AND search archive

---

## Phase 5: User Story 3 - View Conversation (Priority: P3)

**Goal**: Display full conversation with all messages in chronological order

**Independent Test**: Run `chatgpt-archive view <id>` and verify all messages display with role labels and timestamps

### Implementation for User Story 3

- [ ] T025 [US3] Implement conversation retrieval by ID in chatgpt_archive/db.py
- [ ] T026 [US3] Implement message ordering (handle tree structure) in chatgpt_archive/db.py
- [ ] T027 [US3] Implement human-readable conversation formatting with pagination for long conversations (1000+ messages) in chatgpt_archive/cli.py
- [ ] T028 [US3] Add view command to CLI in chatgpt_archive/cli.py
- [ ] T029 [US3] Add --json flag for view output in chatgpt_archive/cli.py
- [ ] T030 [US3] Handle "conversation not found" error case in chatgpt_archive/cli.py

**Checkpoint**: User Stories 1-3 complete - can import, search, and view conversations

---

## Phase 6: User Story 4 - Export Conversation (Priority: P4)

**Goal**: Export conversations to MD, JSON, YAML, HTML, XML formats

**Independent Test**: Run `chatgpt-archive export <id> -f md -o test.md` and verify output contains complete conversation

### Implementation for User Story 4

- [ ] T031 [P] [US4] Create base exporter abstract class in chatgpt_archive/exporters/base.py
- [ ] T032 [P] [US4] Implement Markdown exporter in chatgpt_archive/exporters/markdown.py
- [ ] T033 [P] [US4] Implement JSON exporter in chatgpt_archive/exporters/json_export.py
- [ ] T034 [P] [US4] Implement YAML exporter in chatgpt_archive/exporters/yaml_export.py
- [ ] T035 [P] [US4] Implement HTML exporter with CSS styling in chatgpt_archive/exporters/html.py
- [ ] T036 [P] [US4] Implement XML exporter in chatgpt_archive/exporters/xml_export.py
- [ ] T037 [US4] Create exporter registry in chatgpt_archive/exporters/__init__.py
- [ ] T038 [US4] Add export command to CLI with --format and --output options in chatgpt_archive/cli.py
- [ ] T039 [US4] Handle stdout output when no --output specified in chatgpt_archive/cli.py
- [ ] T040 [US4] Add file write error handling in chatgpt_archive/cli.py

**Checkpoint**: User Stories 1-4 complete - full import/search/view/export workflow

---

## Phase 7: User Story 5 - List Conversations (Priority: P5)

**Goal**: Browse all imported conversations with metadata and pagination

**Independent Test**: Run `chatgpt-archive list --limit 10` and verify 10 conversations shown with titles, dates, message counts

### Implementation for User Story 5

- [ ] T041 [US5] Implement conversation listing query with message counts in chatgpt_archive/db.py
- [ ] T042 [US5] Implement sorting (by date, title, message count) in chatgpt_archive/db.py
- [ ] T043 [US5] Implement pagination with offset/limit in chatgpt_archive/db.py
- [ ] T044 [US5] Add list command to CLI with --sort/--order/--limit/--offset options in chatgpt_archive/cli.py
- [ ] T045 [US5] Add --json flag for list output in chatgpt_archive/cli.py
- [ ] T046 [US5] Format human-readable list output with summary counts in chatgpt_archive/cli.py

**Checkpoint**: All user stories complete - full feature set implemented

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

- [ ] T047 [P] Add environment variable CHATGPT_ARCHIVE_DB support in chatgpt_archive/cli.py
- [ ] T048 [P] Add --version flag to CLI in chatgpt_archive/cli.py
- [ ] T049 [P] Ensure all errors output to stderr in chatgpt_archive/cli.py
- [ ] T050 Add database path expansion (~/ handling) throughout chatgpt_archive/db.py
- [ ] T051 Run quickstart.md validation - verify all documented commands work
- [ ] T052 Performance validation - ensure <60s import, <500ms search, <2s export
- [ ] T053 Database size validation - ensure DB file is <2x original JSON size per SC-007

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKING
    ↓
┌───┴───────────────────────────────┐
↓       ↓       ↓       ↓           ↓
US1 →  US2  →  US3  →  US4  →     US5    (Sequential by priority)
(P1)   (P2)    (P3)    (P4)       (P5)
    ↓
Phase 8 (Polish)
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (Import) | Foundational | Phase 2 complete |
| US2 (Search) | US1 | Phase 3 complete (needs data to search) |
| US3 (View) | US1 | Phase 3 complete (needs data to view) |
| US4 (Export) | US3 | Phase 5 complete (needs view logic) |
| US5 (List) | US1 | Phase 3 complete (needs data to list) |

### Parallel Opportunities

**Within Phase 1 (Setup)**:
```
T001 → T002 → [T003, T004, T005] in parallel
```

**Within Phase 2 (Foundational)**:
```
T006 → [T007, T008, T009] in parallel → T010
```

**Within Phase 6 (User Story 4 - Export)**:
```
T031 → [T032, T033, T034, T035, T036] all in parallel → T037 → T038...
```

**Within Phase 8 (Polish)**:
```
[T047, T048, T049] all in parallel → T050 → T051 → T052
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. ✅ Complete Phase 1: Setup
2. ✅ Complete Phase 2: Foundational
3. ✅ Complete Phase 3: User Story 1 (Import)
4. **STOP**: Test import with real archive, verify data in database
5. **Value delivered**: 1,778 conversations now queryable via direct SQL

### Incremental Delivery

| After Phase | Capability Unlocked |
|-------------|---------------------|
| 3 (US1) | Import and direct SQL queries |
| 4 (US2) | Full-text search via CLI |
| 5 (US3) | View conversations in terminal |
| 6 (US4) | Export to any format |
| 7 (US5) | Browse/list all conversations |
| 8 (Polish) | Production-ready tool |

### Recommended Approach

**Single developer**: Sequential P1→P2→P3→P4→P5
- Each phase delivers testable value
- Can ship after any phase

**Two developers**:
1. Dev A: US1, US2, US3
2. Dev B: (wait for US1) then US4, US5 in parallel once US3 done

---

## Notes

- All paths are relative to repository root
- Database schema from data-model.md includes FTS5 triggers (auto-index on insert)
- CLI contract from contracts/cli.md defines all options and exit codes
- No tests explicitly requested - add tests/ directory if needed later
- Commit after each task or logical group
- Run `pip install -e .` after T002 to test CLI during development
