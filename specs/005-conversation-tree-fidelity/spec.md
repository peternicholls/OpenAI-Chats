- Q: In fallback mode (missing `current_node`), what ordering should be used for `sequence_order`? → A: Assign `sequence_order` by `create_time` ascending (chronological), with a deterministic tie-breaker for equal or null timestamps. This produces the most meaningful reading order while keeping repeated imports stable.
- Q: Hard rule — should any data from the export be discarded during import? → A: No. Zero discard is a hard requirement for all parsing and importing. Every field at every level must be stored. Conversation-level non-mapping fields go into `conversations.metadata`, the raw `mapping` is preserved separately, and message-level metadata is covered by FR-012b. See FR-015, FR-016, and the Hard Constraints section.
# Feature Specification: Conversation Tree Fidelity

**Feature Branch**: `005-conversation-tree-fidelity`  
**Created**: 2026-04-11  
**Status**: Draft  
**Input**: The ChatGPT export encodes conversations as a branching tree, not a linear list. The current importer ignores this structure, importing every node in the mapping — including abandoned edit-version branches — into the database. This produces incorrect transcripts: multiple consecutive versions of the same user message appear in the rendered conversation view. Fixing this requires changes to the importer, database schema, and the API/rendering pipeline.

---

## Clarifications

### Session 2026-04-11

- Q: What should the fallback behaviour be when `current_node` is missing or not found in the mapping? → A: Import all mapping nodes (current pre-fix behaviour) and log a warning. The conversation degrades gracefully to the same output as the unfixed importer; no content is lost.
- Q: When re-importing, should delete+reinsert happen on every run or only with an explicit flag? → A: N/A — this is a single-developer project with no production concerns. The DB is destroyed and recreated from scratch on each import. No migration compatibility or incremental re-import strategy is needed.
- Q: In fallback mode (missing `current_node`), what ordering should be used for `sequence_order`? → A: Assign `sequence_order` by `create_time` ascending (chronological), with a deterministic tie-breaker for equal or null timestamps. This produces the most meaningful reading order while keeping repeated imports stable.
- Q: Should suppression rules for internal AI processing nodes (`thoughts`, `tool`, `reasoning_recap`) move into the importer or stay at query time in the API layer? → A: Keep at query time in the API layer (sprint 004 definition unchanged). The importer writes all active-path nodes to the DB; visibility filtering is the API's responsibility. This preserves future optionality (e.g. "show thinking activity") without a reimport.
- Q: What data should unit tests for active-path traversal use? → A: Synthetic in-memory `mapping` dicts constructed in the test file. Fast, no I/O, no PII, easy to annotate with explicit branch structure. The real `544a9c4c` conversation is only used in environment-dependent integration smoke tests.

---

## Background & Ground Truth

All data-model facts in this spec are derived from direct inspection of `conversations.json` in the ChatGPT export archive. See [`/Ground-truth-from-ChatGPT-archive.md`](/Ground-truth-from-ChatGPT-archive.md) for the full research notes. The database is **not** authoritative for data-model questions — it reflects whatever the importer produced, which may be incorrect.

### How ChatGPT Stores Conversations

ChatGPT's export format stores each conversation as a **tree**:

- `mapping` — a flat dictionary keyed by node ID, where each node has `parent`, `children[]`, and `message` fields.
- `current_node` — a top-level string on the conversation object identifying the last message of the canonical (active) path.

Every user message edit creates a **new sibling node** alongside the original; the original is never overwritten or deleted. The `children[]` array of the parent node will contain multiple IDs — one per edit version.

The **canonical conversation timeline** is obtained by traversing parent links from `current_node` back to the root, then reversing to get chronological order. Nodes NOT on this path are **abandoned edit branches** and must never appear in the rendered transcript.

### Evidence from Real Data

Tested against conversation `544a9c4c-1b8a-4069-8458-78323ce146ce` ("Legacy PHP code update."):

| Metric | Value |
|---|---|
| Total mapping nodes | 65 |
| Active-path nodes | 34 |
| Inactive branch nodes | 31 |
| Branch points | 4 (user edited their initial message 4 times) |
| `weight` on inactive nodes | `1.0` — identical to active nodes; **weight cannot discriminate branches** |

### Current Defect

`extract_messages_from_mapping()` in `chatgpt_archive/importer.py` iterates `mapping.items()` without path awareness, importing all 65 nodes. `get_conversation_messages()` in `chatgpt_archive/db.py` returns all non-hidden messages ordered by database insertion ID, so the 31 inactive branch nodes surface as consecutive user turns in the rendered transcript.

## Ground Truth Parse and Import Pipeline

The importer is defined against the raw ChatGPT export shape observed in `conversations.json`.

### Source parse model

1. Parse `conversations.json` as a JSON array of conversation objects.
2. For each conversation, read dedicated top-level fields into normalized columns:
    - `id` or `conversation_id`
    - `title`
    - `create_time`
    - `update_time`
    - `default_model_slug`
    - `current_node`
    - `is_archived`
3. Persist all remaining top-level non-mapping fields into `conversations.metadata`.
4. Preserve the full raw `mapping` object separately so inactive branches and unmodeled node fields remain recoverable.

### Mapping parse model

Each `mapping` entry is a node keyed by node ID and containing `message`, `parent`, and `children[]`.

Parsing rules:

1. The mapping key is the node identity.
2. `parent` defines reverse traversal toward the root.
3. `children[]` is source fidelity data, not part of the canonical transcript projection.
4. Nodes whose `message` is `null` are root sentinel nodes and are excluded from canonical message insertion.

### Message parse model

For each imported non-sentinel node:

1. `message.author.role` -> `messages.author_role`
2. `message.author.name` -> `messages.author_name`
3. `message.create_time` -> `messages.create_time`
4. `message.weight` -> `messages.weight`
5. `message.content.content_type` -> `messages.content_type`
6. `message.metadata.model_slug` -> `messages.model_slug`
7. `message.metadata.is_visually_hidden_from_conversation` -> `messages.is_hidden`
8. `message.metadata` -> `messages.metadata`
9. `message.content.parts[]` -> `messages.content` using source-order preservation, verbatim string preservation, and `json.dumps(...)` for non-string parts

### Import projection order

For each conversation, import proceeds in this order:

1. Insert normalized conversation fields into `conversations`.
2. Insert the full raw `mapping` into the raw-source preservation store.
3. Compute the canonical path from `current_node`, or enter fallback mode.
4. Project selected nodes into canonical `messages` rows with `sequence_order`.
5. Insert attachments linked to the imported message rows.

This separation is intentional: the database stores both a canonical transcript projection and a preserved raw source representation.

---

## Scope

This sprint fixes conversation rendering fidelity end-to-end: correct import → correct DB state → correct API output → correct frontend display.

**In scope:**
- Importer path-aware traversal (import only the active path)
- `current_node_id` column on the `conversations` table
- `metadata TEXT` blob on the `conversations` table (all non-mapping fields — FR-015)
- raw `mapping` preservation in `conversation_sources` (FR-016)
- DB schema updates and fresh-import strategy to deliver clean data
- A mapping with a missing or unresolvable `current_node` (fallback behaviour — all nodes imported, ordered by `create_time` plus deterministic tie-breaker)
- `author_name` column on `messages` (from `author.name`)
- `model_slug` column on `messages` (extracted from `metadata.model_slug` — FR-014)
- `metadata` column on `messages` (full metadata dict as JSON blob)
- Correct serialisation of non-string `parts[]` entries (JSON not Python repr)
- Code execution output captured from `metadata.aggregate_result` on `execution_output` nodes
- Inline cite token text stored verbatim; citation resolution data captured in metadata blob
- API and service layer fixes to return only canonical messages
- Frontend rendering validation that branching artefacts are gone
- Tests at every layer

**Out of scope:**
- UI for browsing alternative edit branches ("show previous versions")
- Diff view between message edits
- Per-message model badge UI display (deferred to design — but `model_slug` IS stored per FR-014)
- Rendering of the newly captured metadata fields (`search_queries`, `finished_duration_sec`, `aggregate_result`, etc.) — data is imported and stored; display decisions are deferred to design
- Resolving or replacing inline cite tokens (`\ue200cite\ue202...\ue201`) with markdown links at import time — raw tokens stay in `content`, resolution data (URLs, titles) is available in the `metadata` blob

### Session 2026-04-12

- Q: Should per-message `model_slug` capture require a dedicated column or is the metadata blob sufficient? → A: Dedicated column required. `model_slug` is first-class data; blob-only forces `json_extract()` on every row for common queries. Add `model_slug TEXT` to `messages` as extracting denormalised column (same pattern as `is_hidden`). See FR-014.
- Q: Hard rule — should any data from the export be discarded during import? → A: No. Zero discard is a hard requirement for all parsing and importing. Every field at every level must be stored. Conversation-level non-mapping fields go into `conversations.metadata`, the raw `mapping` is preserved separately, and message-level metadata is covered by FR-012b. See FR-015, FR-016, and the Hard Constraints section.

---

## Functional Requirements

### FR-001 — Active-Path Traversal at Import Time

The importer MUST compute the active message path for each conversation before inserting messages. The active path is defined as the ordered sequence of nodes obtained by walking from `current_node` to the root via `parent` links, then reversing the sequence.

Only nodes on the active path MUST be inserted into the `messages` table. Branch nodes (nodes not on the active path) MUST NOT appear in the canonical transcript projection, but they MUST still be preserved in raw form for future fidelity and branch-history work.

Note: every mapping contains a root **sentinel node** whose `message` field is `null`. It is always the first element of the active path and MUST be skipped during insert (no row is written for it).

See FR-008 for the sole exception: when `current_node` is missing or unresolvable, all mapping nodes are imported instead.

**Acceptance criterion:** After importing a conversation with N branch points, the `messages` table contains exactly the number of nodes on the active path (excluding the null-message sentinel), no message from an inactive branch is present in `messages`, and the full original `mapping` remains recoverable from the database.

---

### FR-002 — `current_node_id` Stored on Conversation

The `conversations` table MUST have a `current_node_id TEXT` column containing the `current_node` value from the raw JSON. This column is used:
1. As the traversal starting point during import
2. For future re-import correctness validation
3. For potential future "navigate to branch" features

**Acceptance criterion:** After import, `SELECT current_node_id FROM conversations WHERE openai_id = ?` returns the string value of `current_node` from the source JSON.

---

### FR-003 — Schema Changes

The new columns `current_node_id TEXT` and `metadata TEXT` on `conversations`, a new `conversation_sources` table for raw tree preservation, and `sequence_order INTEGER NOT NULL`, `author_name TEXT`, `model_slug TEXT`, `metadata TEXT` on `messages` MUST be defined in `chatgpt_archive/db.py` as part of the initial `CREATE TABLE` statements (or `IF NOT EXISTS` logic). Because the database is destroyed and recreated on each import run during development, backward-compatible `ALTER TABLE` migration is not required.

The `Message` dataclass in `chatgpt_archive/models.py` MUST be updated to include four new fields: `author_name: str | None`, `model_slug: str | None`, `sequence_order: int`, and `metadata: str`. These fields are the contract between the importer and the DB insertion layer; without them the importer will fail at runtime.

**Acceptance criterion:** A freshly created database contains all new columns and the `conversation_sources` table. The `Message` dataclass has the four new fields. Running `chatgpt-archive import` against a clean directory produces a DB with the correct schema.

---

### FR-004 — Re-import Strategy

The standard re-import workflow is: delete the database file, then run `chatgpt-archive import` from scratch. This is the only supported recovery path during development. No incremental re-import or branch-node pruning logic is required.

**Acceptance criterion:** After `rm`-ing the DB and re-running import, the resulting database contains only active-path nodes in `messages` for all conversations, while preserving each conversation's full raw `mapping` for recovery and future UX work.

---

### FR-005 — Message Order Reflects Active-Path Sequence

After import, messages returned by `get_conversation_messages()` MUST appear in the order they occur on the active path (root → `current_node`). The current sort by database `id` (insertion order) is unreliable for tree-structured data.

The active-path traversal order MUST be persisted as a `sequence_order INTEGER NOT NULL` column on the `messages` table, set at import time. `get_conversation_messages()` MUST order by `sequence_order ASC`.

**Acceptance criterion:** Messages for conversation `544a9c4c` render in the correct chronological sequence matching the ground truth `current_node → root` walk.

---

### FR-006 — API Returns Only Canonical Messages

The conversation detail endpoint (`GET /conversations/{id}`) MUST return only messages that are on the canonical transcript (active path, non-hidden, passing suppression rules from sprint 004). No branch nodes, no `[No content]` placeholders for abandoned edit versions.

Suppression rules for internal processing nodes (`thoughts`, `tool`, `reasoning_recap`, etc.) remain at query time in the API/service layer — the importer writes all active-path nodes to the DB regardless of content type. Sprint 005 does not move or duplicate the sprint 004 suppression logic.

**Acceptance criterion:** `GET /conversations/544a9c4c-1b8a-4069-8458-78323ce146ce` returns a `messages` array with no duplicate consecutive user turns.

---

### FR-007 — Message Count Accuracy

The `message_count` field on conversation list and detail responses MUST accurately reflect the count of user-visible messages on the active path only (applying the same visibility predicate as sprint 004: user and assistant roles, excluding hidden/suppressed nodes).

**Acceptance criterion:** `message_count` for "Legacy PHP code update." equals the number of `user` and `assistant` messages on the active path, not the total node count.

---

### FR-008 — Importer Handles Missing `current_node` Gracefully

Some older or malformed export conversations may not have a `current_node` field, or `current_node` may reference a node ID not present in the mapping. In either case, the importer MUST fall back to importing **all nodes in the mapping** (equivalent to the pre-fix behaviour) and MUST log a warning identifying the affected conversation. The import MUST NOT abort.

This preserves all content in the degraded case. A follow-up re-import once the data issue is understood can correct the conversation.

**Acceptance criterion:** A conversation with a null, missing, or unresolvable `current_node` is imported without error. All mapping nodes are written to the `messages` table with `sequence_order` assigned by `create_time` ascending and a deterministic tie-breaker for equal/null timestamps. A warning is logged containing the conversation `openai_id` and the nature of the fallback.

---

### FR-009 — Core Library Tests

The `chatgpt_archive` package MUST have unit tests covering:
- Active-path traversal on a mapping with known branch structure
- A mapping with no branching (single linear path)
- A mapping with a missing or unresolvable `current_node` (fallback behaviour — all nodes imported, ordered by `create_time` plus deterministic tie-breaker)
- `sequence_order` is correctly assigned as 1-based ascending integers matching path order
- Sentinel node (null `message`) is excluded from inserted rows
- `author_name` is populated from `author.name` for tool nodes and is `None`/`NULL` for user and assistant nodes
- `metadata` column stores a valid JSON string for every inserted row (round-trippable via `json.loads()`)
- Non-string `parts[]` entries produce valid JSON content strings (not Python repr)
- Cite token text is preserved verbatim: a synthetic message whose `parts[0]` contains `\ue200cite\ue202turn1view0\ue201` stores that exact string in `content` without modification

All test cases MUST use **synthetic in-memory `mapping` dicts** constructed directly in the test file. No fixture files, no live DB access. The real `544a9c4c` conversation may be referenced in a separate integration smoke-test that is skipped unless `~/.chatgpt-archive/chats.db` is present.

**Acceptance criterion:** All tests in `tests/unit/test_importer.py` pass with `pytest tests/unit/ -v` and no external dependencies.

---

### FR-010 — API Tests

`api/tests/` MUST have integration tests covering:
- Conversation detail endpoint returns expected message sequence for a conversation with known branch structure (using a fixture, not the live DB)
- `message_count` matches the active-path count, not the raw node count
- `author_name` is present on tool-role messages in the response
- `metadata` values in the response are valid JSON strings
- A message with cite tokens returns those tokens intact in the `content` field

**Acceptance criterion:** All tests in `api/tests/test_conversations.py` pass.

---

### FR-011 — No Regression on Branch-Free Conversations

Conversations with no editing (single linear path, no branch points) MUST continue to import and render correctly after this change.

**Acceptance criterion:** Existing passing tests in `tests/` continue to pass. A sample of at least 5 branch-free conversations renders without change in the UI.

---

### FR-012 — Complete Node Data Capture

The importer MUST capture all available data from each mapping node. Four specific gaps exist in the current importer:

**FR-012a — `author_name` column**

The `messages` table MUST have an `author_name TEXT` column storing the `author.name` field from each node (e.g. `"canmore"`, `"container.exec"`, `"web.run"`, `"python"`, `"bio"`, `"dalle.text2im"`). This is distinct from `author.role` and is the primary identifier for tool nodes. NULL for user/assistant/system nodes where `author.name` is absent.

**FR-012b — `metadata` JSON blob column**

The `messages` table MUST have a `metadata TEXT` column storing the raw `metadata` dict from each node as a JSON blob (`json.dumps(msg.get('metadata', {}))`). Nodes with no `metadata` key get `'{}'` stored (never NULL).

The existing `is_hidden` column continues to be extracted separately from `metadata['is_visually_hidden_from_conversation']` before the blob is written. The `is_hidden` column is a denormalised copy retained for efficient query filtering; it is not removed even though its source key is present in the blob.

This captures:
- `search_queries`, `reasoning_title`, `searched_display_string` (assistant/code dispatch nodes)
- `finished_duration_sec` (reasoning_recap nodes)
- `aggregate_result`, `ada_visualizations` (execution_output nodes — see FR-012c)
- `citations`, `content_references`, `model_slug` (assistant/text nodes)
- `_cite_metadata`, `display_title`, `display_url` (tether_browsing_display nodes)
- All other tool-specific metadata fields

**FR-012c — Code execution output from `metadata.aggregate_result`**

For `tool/execution_output` nodes, `parts[]` is always empty. The actual code execution output lives in `metadata.aggregate_result`, a structured object containing `code`, `messages` (stdout/stderr), `status`, and `run_id`. This is captured automatically by FR-012b (stored in the `metadata` JSON blob) and MUST NOT be extracted into `content` — `content` remains NULL for these nodes. The rendering layer will read from `metadata` when it needs execution output.

**FR-012d — Fix non-string `parts[]` serialisation**

The current importer calls `str(p)` on non-string parts entries. For `multimodal_text` nodes (user images, DALL-E responses, file search results), parts are dicts:
```json
{"asset_pointer": "file-abc123", "width": 1024, "height": 1024, ...}
```
`str()` produces Python dict repr (`{'asset_pointer': 'file-abc123', ...}`) which is malformed. The importer MUST use `json.dumps(p)` for any part that is not a plain string.

**Acceptance criteria:**
- After import, `SELECT author_name FROM messages WHERE author_role = 'tool' LIMIT 5` returns tool names, not NULL.
- `SELECT metadata FROM messages WHERE content_type = 'reasoning_recap' LIMIT 1` returns a string that is valid JSON (passes `json.loads()`) and contains the key `finished_duration_sec`.
- `SELECT metadata FROM messages WHERE content_type = 'execution_output' LIMIT 1` returns a string that is valid JSON and contains the key `aggregate_result`.
- `SELECT COUNT(*) FROM messages WHERE json_valid(metadata) = 0` returns 0 (all metadata values are valid JSON).
- `SELECT content FROM messages WHERE content_type = 'multimodal_text' LIMIT 1` returns valid JSON (not Python repr); confirmed by `json.loads()` without raising.

---

### FR-013 — Inline Citation Token Preservation

**1,087 `assistant/text` messages** across the archive contain inline citation reference markers embedded in the `parts[]` text string. These use Unicode **Private Use Area** characters:

```
\ue200cite\ue202{ref_id}\ue201
```

Example: `\ue200cite\ue202turn5view0\ue201` or a multi-ref group `\ue200cite\ue202turn2search4\ue202turn2news26\ue201`.

**Import strategy (this sprint):** Store `parts[]` text verbatim — cite markers are preserved as-is in the `content` column. No transformation is applied at import time. The `metadata` blob (FR-012b) already captures `content_references` and `citations`, which contain the full resolution data (URLs, titles, `alt` markdown text, `start_idx`/`end_idx` byte offsets into content).

This is intentionally a two-phase design: import stores everything, rendering resolves cite tokens against metadata when displaying. The rendering resolution is out of scope for this sprint.

**Data available in `metadata.content_references` (web search citations, per cite token):**
- `matched_text` — the raw token (for matching)
- `start_idx` / `end_idx` — byte offsets into the parts text string
- `alt` — pre-formatted markdown replacement (e.g. `([Source Name](https://...))`)
- `items[].title`, `items[].url`, `items[].attribution` — structured citation object
- `safe_urls[]` — resolved URL list

**Data available in `metadata.citations` (file/document citations, per cite token):**
- `start_ix` / `end_ix` — character offsets into the parts text string (not byte offsets — distinct from `content_references`)
- `citation_format_type` — `"berry_file_search"` (uploaded file) or `"tether_v4"` (web page retrieved via code interpreter)
- `metadata.name` — filename (file search) or page title
- `metadata.text` — quoted excerpt
- `metadata.extra.cited_message_id` — links to the tool message that performed the retrieval

#### Rendering Considerations (informs storage decisions)

Although cite rendering is deferred, the intended UX and implementation path must be understood now — **because storage correctness depends on it**.

**Target UX:** ChatGPT's own rendering inlines citations as clickable superscript-style footnote references. The preferred result for this app is the same: `[Source Name](https://...)` links inline in the text, positioned exactly where the cite token appears. The `alt` field in each `content_references` entry already provides this as ready-formatted markdown (e.g. `([Margaret Thatcher Foundation](https://www.margaretthatcher.org/document/107346))`).

**Why store raw, not pre-resolved:** The `start_idx`/`end_idx` offsets are byte positions into the original `parts[]` text. If the importer modifies the text in any way (URL-encoding, normalising whitespace, stripping other markers), those offsets become invalid and the `alt` replacement can no longer be accurately positioned. Storing verbatim preserves the ability to use either offset-based replacement or `matched_text`-based regex replacement in a future rendering pass.

**Recommended rendering approach (future sprint):** The natural integration point is `build_render_segments()` in `api/services/formatting_service.py`. This function already receives `content` and resolves attachment tokens line by line. The cite resolution step would:

1. Receive `metadata` (parsed from the JSON blob) as an additional parameter alongside `content`.
2. After the existing line-by-line segmentation, apply a single-pass regex substitution over any `MarkdownSegment` text: replace each `\ue200cite\ue202...\ue201` token with its `alt` value from `content_references`, matched via `matched_text`.
3. If `content_references` is absent or a token has no matching entry, strip the marker silently (do not leave PUA characters in rendered output).

**Alternative UX — footnote list:** Instead of inline link substitution, citations could be collected and rendered as a numbered footnote list below the message. The `items[]` structure supports this — each item has `title`, `url`, `attribution`. This is a presentation-layer decision and does not change storage or the `alt`-based fallback.

**Storage implication confirmed:** `parts[]` text MUST be stored byte-for-byte as-is. No normalisation, no whitespace trimming, no character substitution. The `\ue200`/`\ue202`/`\ue201` markers must survive the import pipeline intact.

**Acceptance criteria:**
- `SELECT content FROM messages WHERE content LIKE '%` + `\ue200cite%' LIMIT 1` returns a row with the cite marker present and intact (not stripped or garbled).
- The corresponding `metadata` JSON blob for that row contains a `content_references` key.
- No data loss: `json.loads(metadata)['content_references']` is a non-empty list for a message that contained cite tokens.

---

### FR-014 — `model_slug` Dedicated Column on Messages

The `messages` table MUST have a `model_slug TEXT` column containing the value of `metadata.model_slug` for each node where it is present.

**Source**: `msg['metadata'].get('model_slug')` — present on `assistant/text` nodes (26,030 of 31,069 assistant nodes in the reference archive). NULL for:
- User, system, and sentinel nodes (no metadata model slug)
- Assistant subtool nodes of `content_type` `thoughts` or `code` (these are reasoning steps; the model is implied from the parent `text` node)

**Rationale**: `model_slug` is first-class data for every assistant response — it identifies which model produced the text. Storing it as a dedicated column allows efficient queries such as "list all conversations that used o3" without requiring `json_extract()` over the full metadata blob. The value is also present in the metadata blob (FR-012b), so no data is duplicated: the column is a denormalised extract for query performance only.

**Acceptance criteria:**
- `SELECT DISTINCT model_slug FROM messages WHERE author_role = 'assistant' AND model_slug IS NOT NULL` returns a set of recognisable model slug strings (e.g. `gpt-4o`, `o3`, `gpt-5`).
- `SELECT COUNT(*) FROM messages WHERE author_role = 'assistant' AND content_type = 'text' AND model_slug IS NULL` returns a low count consistent with the pre-slug era (older GPT-3.5 exports may lack it).
- `SELECT message_id FROM messages WHERE model_slug = 'o3' LIMIT 1` executes without a full-table scan on `metadata`.

---

### FR-015 — Conversation Metadata Blob

The `conversations` table MUST have a `metadata TEXT` column storing all conversation-level fields from the source JSON that are NOT already stored as dedicated columns, as a JSON blob.

**Source**: The entire top-level conversation object from `conversations.json`, minus the `mapping` key (which is preserved separately in raw form). Implementation: `json.dumps({k: v for k, v in conv_data.items() if k != 'mapping'})`.

**Fields captured** (observed in the reference archive; list is non-exhaustive — all fields pass through regardless of whether they appear below):

| Field | Coverage | Notes |
|---|---|---|
| `memory_scope` | 1778/1778 | `global_enabled` or `project_enabled` |
| `is_do_not_remember` | 585/1778 | Privacy control — whether the conversation was excluded from memory training |
| `safe_urls` | 990/1778 | Resolved URLs from web grounding |
| `gizmo_id` | 65/1778 | Custom GPT / app identifier |
| `gizmo_type` | 65/1778 | GPT type classification |
| `conversation_template_id` | 65/1778 | Template origin |
| `conversation_origin` | 43/1778 | How the conversation was started |
| `plugin_ids` | 27/1778 | Legacy plugin identifiers |
| `async_status` | 27/1778 | Async conversation state |
| `voice` | 5/1778 | Voice interaction settings |
| `disabled_tool_ids` | 1/1778 | Tools disabled for this conversation |
| `is_study_mode` | 1778/1778 | Always `false` in reference archive; stored for completeness |
| `sugar_item_visible` | 1778/1778 | Always `false` in reference archive; stored for completeness |

Dedicated columns (`openai_id`, `title`, `create_time`, `update_time`, `model_slug`, `is_archived`, `is_favorite`, `current_node_id`) continue to exist and are not duplicated in the blob. The blob stores ONLY fields that do not have a dedicated column.

**Acceptance criteria:**
- `SELECT metadata FROM conversations LIMIT 1` returns a valid JSON string (passes `json_valid()`).
- `SELECT COUNT(*) FROM conversations WHERE json_valid(metadata) = 0` returns 0.
- `json_extract(metadata, '$.memory_scope')` returns `'global_enabled'` or `'project_enabled'` for every row where the field was present.
- `json_extract(metadata, '$.gizmo_id')` returns a non-null value for conversations with a custom GPT.
- The `mapping` key is NOT present in the stored blob.
- The full `mapping` object is preserved elsewhere in the database so zero-discard fidelity is maintained.

---

### FR-016 — Raw Mapping Preservation

The database MUST preserve the full raw `mapping` object for every imported conversation in a dedicated raw-source store so that inactive edit branches, `children[]` relationships, and unmodeled node fields remain recoverable without re-import.

The canonical `messages` table remains the app-facing transcript projection. Raw-tree preservation is a separate responsibility and MUST NOT be approximated solely by the canonical rows.

**Acceptance criteria:**
- Every imported conversation has exactly one raw-source record containing the original `mapping` JSON.
- `json_valid()` succeeds for every stored raw `mapping` value.
- An inactive branch node excluded from `messages` can still be recovered from the raw-source record for that conversation.

---

### FR-017 — Ground Truth Parsing and Projection Semantics

The importer MUST parse the export according to the observed ground-truth structure in `conversations.json` and project it into the database in a deterministic order.

Required semantics:

1. Parse the archive as an array of conversation objects.
2. Split each conversation into:
    - normalized conversation columns
    - conversation-level metadata blob
    - raw `mapping` preservation record
3. Parse mapping nodes using the mapping key as node identity.
4. Exclude null-message sentinel nodes from canonical `messages` insertion.
5. Parse `message.content.parts[]` preserving source order, verbatim string content, and JSON serialization for non-string parts.
6. Project selected nodes into canonical `messages` rows only after raw source preservation has succeeded.

**Acceptance criteria:**
- A synthetic conversation object can be traced from raw JSON shape to `conversations`, raw-source storage, `messages`, and `attachments` without losing any source field.
- Non-string `parts[]` content is stored as valid JSON text, not Python repr text.
- Tool execution nodes with empty `parts[]` still preserve their execution payload in stored metadata.

---

## Data Model Changes

### `conversations` table

Add the following columns to the `CREATE TABLE conversations` definition in `chatgpt_archive/db.py`:

```sql
current_node_id  TEXT,   -- current_node value from source JSON (traversal + future nav)
metadata         TEXT    -- all non-mapping conversation-level fields as JSON blob
```

### `conversation_sources` table

Add a dedicated raw-source preservation table:

```sql
conversation_id  INTEGER PRIMARY KEY,  -- 1:1 with conversations.id
mapping_json     TEXT NOT NULL         -- full raw mapping object as JSON
```

This table preserves the full tree, including inactive edit branches, `children[]` relationships, and raw node payloads that are not part of the canonical `messages` projection.

### `messages` table

Add the following columns to the `CREATE TABLE messages` definition:

```sql
author_name     TEXT,               -- author.name (tool identity, e.g. "canmore", "web.run")
model_slug      TEXT,               -- metadata.model_slug (assistant/text nodes; NULL elsewhere)
sequence_order  INTEGER NOT NULL,   -- 1-based active-path position, set at import time
metadata        TEXT                -- full metadata dict as JSON blob
```

`sequence_order` is 1-based, assigned at import time from the active-path traversal index. All rows are inserted fresh so NULL is not needed for `sequence_order`.

`model_slug` is extracted from `msg['metadata'].get('model_slug')` and is NULL for non-assistant nodes and for assistant subtool nodes that do not carry a slug.

`metadata` stores `json.dumps(msg.get('metadata', {}))` for every node. NULL is not used; empty dict `'{}'` is the minimum.

---

## Key Entities & Invariants

**Active path** — the unique ordered path from the root sentinel node to `current_node`. It is determined entirely from the `mapping` + `current_node` fields in the raw JSON at import time and projected into the canonical `messages` table.

**Branch node** — any mapping node that is NOT on the active path. Not stored in the canonical `messages` table after this sprint, but preserved in the raw-source mapping store for future recovery and branch-history features.

**`current_node`** — required field on each conversation in `conversations.json`. During the archive export from ChatGPT (January 2026), all conversations observed had this field populated.

---

## Hard Constraints

**No data shall be discarded during import.** Every field present in a `conversations.json` export node — whether currently rendered by the UI or not — MUST be stored in the database. Data that is not yet displayed is stored intact so that future features (rendering, search, analytics) can access it without requiring a reimport.

This rule applies at both levels:
- **Message nodes**: the full raw node remains recoverable through preserved raw mapping data (FR-016), while every key in `message.metadata` is additionally stored in the `messages.metadata` blob (FR-012b). Individual high-value fields may additionally be extracted as dedicated columns (e.g. `is_hidden`, `model_slug`) for query efficiency.
- **Conversation records**: every key at the conversation level except `mapping` is stored in the conversation `metadata` blob (FR-015). The `mapping` key itself is preserved separately in raw form (FR-016). Individual high-value fields may additionally be extracted as dedicated columns for query efficiency.

A re-import is expensive (requires deleting the DB and re-running import against the full archive). Storing everything now eliminates the need for a re-import solely to recover discarded fields.

---

## Assumptions

1. The `current_node` value in the export always points to the most recent message in the canonical thread — the "final" state of the conversation as of the export date. This is consistent with ChatGPT's own rendering.
2. Conversations exported in 2023 (GPT-3.5/4 era) use the same tree structure with `current_node` as later exports. (Confirmed: the "Legacy PHP code update." conversation was created 2023-03-24.)
3. The archive `.json` file remains available for full rebuilds, but recovery of inactive branch content should not require a re-import after this sprint.
4. Branch nodes remain part of the preserved source data even though they are excluded from the canonical transcript projection.

---

## Success Criteria

1. No conversation in the UI shows consecutive turns by the same role that are duplicate or near-duplicate edit versions of each other.
2. All conversations with branching history (tested against the real archive) render the same transcript as ChatGPT's own export `chat.html` (the authoritative ground truth for display order).
3. Message counts in the conversation list and header match user-visible turn counts (no inflation from branch nodes or suppressed internal turns).
4. Re-import of the full archive completes without error and produces a consistent DB state on repeated runs.
5. All existing tests continue to pass. New tests added for active-path traversal, fallback behaviour, and API message sequence.

---

## Dependencies

- Sprint 004 must be merged first — the visibility predicate (suppression rules for `thoughts`, `tool`, etc.) is defined there and referenced by FR-006 and FR-007.
- No new external dependencies are expected. The fix is pure Python traversal logic.

---

## Implementation Notes (non-prescriptive)

The core algorithmic change is small:

```python
def active_path(mapping: dict, current_node_id: str) -> list[str]:
    """Return node IDs from root to current_node (chronological order).
    The root sentinel node (null message) is included here; callers must
    skip it when inserting — check node['message'] is not None before insert.
    """
    path = []
    node_id = current_node_id
    while node_id and node_id in mapping:
        path.append(node_id)
        node_id = mapping[node_id].get("parent")
    path.reverse()
    return path
```

Everything else follows from this: preserve the raw `mapping` first, restrict the canonical insert loop to `active_path(mapping, current_node)` unless fallback mode is triggered, assign `sequence_order` from that deterministic order, and project the parsed nodes into the refined schema.

Because this feature uses rebuild-from-scratch imports during development, the implementation can assume clean table creation rather than incremental reconciliation of existing rows.
