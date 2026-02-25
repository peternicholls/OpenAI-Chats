# Tasks: Web UI — Code Review Fixes

**Input**: [`specs/002-web-ui/code_reviews/end-spec002-code-review.md`](end-spec002-code-review.md)  
**Branch**: `002-web-ui` | **Date**: 2026-02-20

## Format: `[ID] [P?] Description — file(s)`

- **[P]**: Parallelisable — no incomplete dependencies, touches different files
- Dependencies called out explicitly within each phase

---

## Phase 1: Foundational (Complete First — Unblocks Quality Phase)

**Purpose**: Two infrastructure changes other tasks depend on. T001 must precede T022 and T023 (schema/env validation moved to startup). T002 must precede T020 (is_favorite migration).

- [ ] T001 Migrate `@app.on_event("startup")` to `lifespan` async context manager; move startup logic into the `lifespan` function body, shutdown logic after `yield` — `api/main.py` *(unblocks T022, T023)*
- [ ] T002 [P] Add `schema_migrations` table and `run_migrations(conn)` function containing a versioned list of idempotent DDL patches; call once at startup — `chatgpt_archive/db.py` *(unblocks T020)*

**Checkpoint**: Foundation ready. All remaining phases can proceed.

---

## Phase 2: Security

### P1 — Critical

- [ ] T003 Fix ZIP path traversal in `import_archive_from_zip`: resolve each member path against `tmpdir_path.resolve()` before extraction; raise `HTTP 400` for any entry that escapes the temp directory — `api/services/archive_service.py`

  ```python
  for member in zf.namelist():
      member_path = (tmpdir_path / member).resolve()
      if not member_path.is_relative_to(tmpdir_path.resolve()):
          raise HTTPException(status_code=400, detail="Invalid archive: path traversal detected")
  zf.extractall(tmpdir_path)
  ```

### P2 — High (all parallelisable — different files)

- [ ] T004 [P] Replace `assert conv_db_id_temp is not None` with `if conv_db_id_temp is None: raise RuntimeError("Failed to get conversation ID after insert")` — `chatgpt_archive/importer.py`
- [ ] T005 [P] Mirror proxy-aware IP logic from `rate_limit.py` into `_get_client_ip`: only trust `X-Forwarded-For` when the direct connecting IP is in `trusted_proxy_ips` — `api/middleware/logging.py`

### P3 — Medium (all parallelisable — different files)

- [ ] T006 [P] Replace `filename="…"` header value with `filename*=UTF-8''<percent-encoded>` using `urllib.parse.quote(filename, safe='')` to prevent header injection from titles containing `"` or non-ASCII characters — `api/routers/export.py`
- [ ] T007 [P] Cap `/api/export/batch` ID list at 500 entries; return `HTTP 422` if exceeded — `api/routers/export.py`
- [ ] T008 [P] Document S-02 known risk: add note explaining that `GET /api/settings` returns the decrypted API key (acceptable for single-user trusted environment per FR-019); consider masking to last 4 chars in the response — `api/routers/settings.py`, `docs/DEPLOYMENT.md`

---

## Phase 3: Bugs

### P1 — Critical

- [ ] T009 Add `"cancelled"` to the terminal status set in **both** `stream_import_progress` and `stream_embedding_progress` — `api/routers/progress.py`

  ```python
  # Before:
  if progress.get("status") in ("complete", "error", "idle"):
  # After:
  if progress.get("status") in ("complete", "error", "idle", "cancelled"):
  ```

### P3 — Medium (independent fixes — parallelisable)

- [ ] T010 [P] Fix `EmbeddingEstimate` TypeScript interface: remove `total_messages` (never returned by API); add `messages_to_embed`, `total_characters`, `price_per_million_tokens`, `estimated_cost_display` — `web/src/types/index.ts`
- [ ] T011 [P] Fix `delete_conversation` orphan scan: collect deleted message IDs before deletion, then `DELETE FROM message_embeddings WHERE message_id IN (…)` rather than a full-table `NOT IN` scan — `chatgpt_archive/db.py`

### P3 — Medium (Tag Rename — FR-008/US4-AC3 — sequential chain)

- [ ] T012 Add `rename_tag(conn, old_name: str, new_name: str)` DB function: `UPDATE conversation_tags SET tag = ? WHERE tag = ?` — `chatgpt_archive/db.py`
- [ ] T013 Add `rename_tag` service adapter that calls the DB function — `api/services/archive_service.py` *(depends T012)*
- [ ] T014 Add `PUT /api/tags/{tag_name}` endpoint with request body `{new_name: str}`; validate new name; return 404 if tag not found, 422 on invalid name — `api/routers/tags.py` *(depends T013)*
- [ ] T015 Add rename affordance to tag list UI (inline edit or rename button); update `useTags` hook to call the new endpoint — `web/src/components/tags/` *(depends T014)*

### P3 — Medium (items_per_page — FR-022 — partially parallelisable)

- [ ] T016 Add `items_per_page: int = 50` to `DEFAULT_SETTINGS` dict — `api/services/settings_service.py`
- [ ] T017 [P] Add `items_per_page: int` field to `UserSettings` Pydantic model — `api/models/responses.py`
- [ ] T018 [P] Add `items_per_page: number` to TypeScript `UserSettings` type — `web/src/types/index.ts`
- [ ] T019 Wire `items_per_page` into conversation list pagination: read from settings and apply as page size — `web/src/` (conversation list hook/page), `api/routers/conversations.py` *(depends T016, T017, T018)*

---

## Phase 4: Code Quality

**Internal dependencies**:
- T022 and T023 depend on T001 (lifespan must exist first)
- T020 depends on T002 (migration system must exist first)
- T021 depends on T020 (`is_favorite` must be in schema first)

### P2 — High (sequential chain)

- [ ] T020 Add `is_favorite INTEGER NOT NULL DEFAULT 0` to `SCHEMA_SQL`; add migration step to `run_migrations()` for existing databases; remove `_ensure_favorite_column()` and all call sites — `chatgpt_archive/db.py`, `api/services/archive_service.py` *(depends T002)*
- [ ] T021 Fix N+1 in `list_conversations` (currently 101 queries/page of 50): batch-fetch all tags with one `GROUP_CONCAT` query; include `is_favorite` in the main conversation SELECT — `api/services/archive_service.py` *(depends T020)*

  ```sql
  SELECT conversation_id, GROUP_CONCAT(tag) FROM conversation_tags
  WHERE conversation_id IN (…) GROUP BY conversation_id
  ```

- [ ] T022 Move `validate_schema_compatibility()` call from `get_connection()` into the `lifespan` startup block so it runs once at startup, not once per API request — `api/services/archive_service.py` *(depends T001)*
- [ ] T023 Move `validate_environment()` into `lifespan` startup; replace `sys.exit(1)` with `raise RuntimeError(…)` so the module is importable in tests — `api/main.py` *(depends T001)*

### P2 — High (parallelisable)

- [ ] T024 [P] Refactor `export_multiple_conversations`: open one DB connection and fetch all requested conversations with `WHERE openai_id IN (?)` rather than one connection per conversation — `api/services/archive_service.py`

### P4 — Low (all parallelisable — different files)

- [ ] T025 [P] Replace `_embedding_cancelled: bool` global with `threading.Event()`; update all `.set()`, `.clear()`, and `.is_set()` call sites — `api/services/archive_service.py`
- [ ] T026 [P] Remove `init_embeddings_schema(conn)` call from `estimate_cost`; callers already initialise the schema at startup — `chatgpt_archive/embeddings.py`
- [ ] T027 [P] Extract `truncate_title(title: str, max_len: int = 50) -> str` shared helper; replace the duplicated 50-char truncation logic in both `Conversation.display_title` and `get_fallback_title()` — `chatgpt_archive/models.py`, `chatgpt_archive/importer.py`
- [ ] T028 [P] Change `datetime.fromtimestamp(ts)` → `datetime.fromtimestamp(ts, tz=timezone.utc)` in `format_results_human` to match CLI UTC output — `chatgpt_archive/search.py`
- [ ] T029 [P] Bump `requires-python = ">=3.10"` (code already uses `X | Y` union syntax throughout, which requires 3.10+) — `pyproject.toml`, `api/pyproject.toml`
- [ ] T030 [P] Remove custom `tmp_path` fixture definitions in both test files; pytest's built-in `tmp_path` provides identical behaviour — `tests/test_db.py`, `tests/test_importer.py`

---

## Phase 5: Test Coverage *(all parallelisable — all different files)*

- [ ] T031 [P] Add unit tests for all tag DB functions: `add_tag`, `remove_tag`, `get_conversation_tags`, `list_all_tags`, `list_conversations_by_tag`, and new `rename_tag` — `tests/test_db.py`
- [ ] T032 [P] Add API-level embedding workflow tests covering: start generation, poll progress, cancel (verify `"cancelled"` status in SSE), and completion — `api/tests/test_embeddings.py` *(new file)*
- [ ] T033 [P] Add settings encryption tests: save API key → retrieve decrypts correctly; corrupt/delete key file → graceful degradation (returns `""`, does not crash); key rotation — `api/tests/test_settings.py` *(new file)*
- [ ] T034 [P] Add middleware unit tests: rate limiter burst limit, window reset, proxy IP trust; validation middleware XSS detection, UUID validation, SQL injection pattern; CORS allowed and rejected origins — `api/tests/test_middleware.py` *(new file)*
- [ ] T035 [P] Add SSE stream termination tests: verify stream closes for each of `"complete"`, `"error"`, `"idle"`, and `"cancelled"` statuses — `api/tests/test_progress.py` *(new file)*
- [ ] T036 [P] Add tag rename API tests: happy path `PUT /api/tags/{name}`; 404 when tag doesn't exist; 422 on invalid new name — `api/tests/test_tags.py`
- [ ] T037 Add end-to-end integration test: import archive → search → export → verify output bytes — `tests/integration/`

---

## Phase 6: Architecture & Polish

- [ ] T038 [P] Persist import/embedding progress state to a SQLite table or JSON file in `~/.chatgpt-archive/` so a server restart does not show false `"idle"` to the browser *(low priority)* — `api/services/archive_service.py`
- [ ] T039 [P] Document `~/.chatgpt-archive/encryption.key`: add backup procedure, consequences of key loss, and log a warning when decryption fails rather than silently returning `""` — `docs/DEPLOYMENT.md`, `api/services/settings_service.py`
- [ ] T040 Add `nginx:alpine` service to `docker-compose.yml` using the existing bind-mounted `docker/nginx.conf`; remove direct port 3000/8000 exposure from `web` and `api` services; update `README.md` — `docker-compose.yml`, `docker/nginx.conf`, `README.md`

---

## Dependency Graph

```
T001 (lifespan)          ──► T022 (schema validation at startup)
                         └──► T023 (validate_environment → RuntimeError)

T002 (migration system)  ──► T020 (is_favorite in SCHEMA_SQL)
                                  └──► T021 (N+1 fix)

T012 (rename_tag DB)     ──► T013 (service adapter)
                                  └──► T014 (PUT /api/tags/{name})
                                            └──► T015 (UI rename affordance)

T016 (DEFAULT_SETTINGS) ─┐
T017 (Pydantic model)   ─┼──► T019 (wire into pagination)
T018 (TS types)         ─┘
```

All other tasks are independent and can run in any order or in parallel.

---

## Parallel Execution Examples

```bash
# Phase 1 (T001 + T002 simultaneously — different files):
"T001: Migrate lifespan in api/main.py"
"T002: Add migration system in chatgpt_archive/db.py"

# Phase 2 P2/P3 security group (all different files):
"T004: Replace assert in chatgpt_archive/importer.py"
"T005: Fix IP trust in api/middleware/logging.py"
"T006: RFC 5987 Content-Disposition in api/routers/export.py"
"T007: Cap batch IDs in api/routers/export.py"

# Phase 4 P4 quality group (all parallel, all different files):
"T025: threading.Event in archive_service.py"
"T026: Remove side effect in embeddings.py"
"T027: Extract truncate_title in models.py"
"T028: Fix UTC in search.py"
"T029: Bump Python in pyproject.toml"
"T030: Remove tmp_path fixtures"

# Phase 5 (all parallel, all new/different files):
"T031: Tag DB tests"
"T032: Embedding tests"
"T033: Settings tests"
"T034: Middleware tests"
"T035: SSE tests"
"T036: Tag rename tests"
```

---

## Verification Checklist

- [ ] `pytest tests/ api/tests/ -v` — all tests pass
- [ ] `pytest tests/ api/tests/ --cov` — coverage >80% on `archive_service.py`, `db.py`, middleware
- [ ] ZIP Slip: craft a path-traversal ZIP (entry: `../../etc/evil`) → confirm `HTTP 400` (T003)
- [ ] SSE cancellation: cancel embedding job → confirm stream closes (T009)
- [ ] N+1 fix: enable SQLite query logging → confirm ≤3 queries for a 50-conversation page load (T021)
- [ ] Content-Disposition: export conversation with `"` / non-ASCII in title → verify header is valid (T006)
- [ ] `cd web && npm run build` — zero TypeScript errors (validates T010 EmbeddingEstimate fix)
- [ ] `docker-compose up` — nginx proxies web (port 80) and API correctly (T040)
- [ ] Manual smoke: import → search → tag → rename tag → favorite → export → settings API key round-trip

---

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Python version | `>=3.10` | Code already uses `X \| Y` union syntax throughout |
| Migration system | Hand-rolled `schema_migrations` table | Minimal complexity; not Alembic |
| Nginx | Wire into `docker-compose.yml` | Config already complete and correct |
| Tag rename | Backend + frontend (T012–T015) | Spec requirement FR-008 / US4-AC3 |
| `is_favorite` schema | Add to `SCHEMA_SQL` via migration (T020) | Removes the lazy `ALTER TABLE` anti-pattern |
