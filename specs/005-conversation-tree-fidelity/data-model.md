# Data Model: Conversation Tree Fidelity

**Feature**: 005-conversation-tree-fidelity | **Date**: 2026-04-12

This feature changes the persisted archive schema. The new design has two goals:

1. Preserve the canonical conversation path instead of importing abandoned edit branches.
2. Preserve all source data that is not rendered yet, so future UX work does not require a destructive re-import.

The database remains SQLite. The import workflow is still rebuild-from-scratch during development.

To satisfy both goals at once, the schema separates:
- the canonical transcript projection used by the app (`messages`)
- the raw export tree preserved for fidelity and future features (`conversation_sources`)

## Entity Relationship Diagram

```text
┌───────────────────────────────────────────────────────────────────────────────┐
│                              conversations                                    │
├───────────────────────────────────────────────────────────────────────────────┤
│ id               INTEGER PRIMARY KEY AUTOINCREMENT                            │
│ openai_id        TEXT UNIQUE NOT NULL                                         │
│ title            TEXT                                                         │
│ create_time      REAL                                                         │
│ update_time      REAL                                                         │
│ model_slug       TEXT                                                         │
│ current_node_id  TEXT                                                         │
│ metadata         TEXT                                                         │
│ is_archived      INTEGER DEFAULT 0                                            │
│ is_favorite      INTEGER NOT NULL DEFAULT 0                                   │
└───────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ 1:1
                                  ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                           conversation_sources                                │
├───────────────────────────────────────────────────────────────────────────────┤
│ conversation_id  INTEGER PRIMARY KEY REFERENCES conversations(id)             │
│ mapping_json     TEXT NOT NULL                                                │
└───────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ preserves full raw tree
                                  │ including inactive branches,
                                  │ children[], and full message payloads
                                  │
                                  │
                                  │ 1:N
                                  ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                                messages                                       │
├───────────────────────────────────────────────────────────────────────────────┤
│ id               INTEGER PRIMARY KEY AUTOINCREMENT                            │
│ conversation_id  INTEGER NOT NULL REFERENCES conversations(id)                │
│ openai_id        TEXT NOT NULL                                                │
│ parent_id        TEXT                                                         │
│ author_role      TEXT NOT NULL                                                │
│ author_name      TEXT                                                         │
│ model_slug       TEXT                                                         │
│ content          TEXT                                                         │
│ content_type     TEXT DEFAULT 'text'                                          │
│ create_time      REAL                                                         │
│ sequence_order   INTEGER NOT NULL                                             │
│ weight           REAL DEFAULT 1.0                                             │
│ is_hidden        INTEGER DEFAULT 0                                            │
│ metadata         TEXT                                                         │
└───────────────────────────────────────────────────────────────────────────────┘
          ▲                              │
          │ self-reference via           │ 1:N
          │ parent_id -> openai_id       ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                              attachments                                      │
├───────────────────────────────────────────────────────────────────────────────┤
│ id               INTEGER PRIMARY KEY AUTOINCREMENT                            │
│ message_id       INTEGER NOT NULL REFERENCES messages(id)                     │
│ file_path        TEXT NOT NULL                                                │
│ file_type        TEXT                                                         │
│ original_name    TEXT                                                         │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                            messages_fts (FTS5)                                │
├───────────────────────────────────────────────────────────────────────────────┤
│ rowid            → messages.id                                                │
│ content          TEXT (full-text indexed)                                     │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                        message_embeddings (Optional)                          │
├───────────────────────────────────────────────────────────────────────────────┤
│ message_id       INTEGER PRIMARY KEY → messages.id                            │
│ embedding        BLOB                                                         │
│ model            TEXT                                                         │
│ created_at       REAL                                                         │
└───────────────────────────────────────────────────────────────────────────────┘
```

## Schema DDL

```sql
CREATE TABLE IF NOT EXISTS conversations (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    openai_id        TEXT UNIQUE NOT NULL,
    title            TEXT,
    create_time      REAL,
    update_time      REAL,
    model_slug       TEXT,
    current_node_id  TEXT,
    metadata         TEXT NOT NULL DEFAULT '{}' CHECK (json_valid(metadata)),
        is_archived      INTEGER NOT NULL DEFAULT 0 CHECK (is_archived IN (0, 1)),
        is_favorite      INTEGER NOT NULL DEFAULT 0 CHECK (is_favorite IN (0, 1))
);
| selected transcript node identity and ordering | normalized transcript rows | `messages` |

CREATE TABLE IF NOT EXISTS conversation_sources (
    conversation_id  INTEGER PRIMARY KEY,
    mapping_json     TEXT NOT NULL CHECK (json_valid(mapping_json)),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS messages (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id  INTEGER NOT NULL,
    openai_id        TEXT NOT NULL,
    parent_id        TEXT,
    author_role      TEXT NOT NULL CHECK (author_role IN ('user', 'assistant', 'system', 'tool')),
    author_name      TEXT,
    model_slug       TEXT,
    content          TEXT,
    content_type     TEXT NOT NULL DEFAULT 'text',
    create_time      REAL,
    sequence_order   INTEGER NOT NULL,
    weight           REAL NOT NULL DEFAULT 1.0,
    is_hidden        INTEGER NOT NULL DEFAULT 0 CHECK (is_hidden IN (0, 1)),
    metadata         TEXT NOT NULL DEFAULT '{}' CHECK (json_valid(metadata)),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    UNIQUE (conversation_id, openai_id),
    UNIQUE (conversation_id, sequence_order)
);

CREATE TABLE IF NOT EXISTS attachments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id      INTEGER NOT NULL,
    file_path       TEXT NOT NULL,
    file_type       TEXT,
    original_name   TEXT,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
);

CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    content,
    tokenize='porter unicode61',
    content='messages',
    content_rowid='id'
);

CREATE TABLE IF NOT EXISTS message_embeddings (
    message_id      INTEGER PRIMARY KEY,
    embedding       BLOB NOT NULL,
    model           TEXT DEFAULT 'text-embedding-3-small',
    created_at      REAL DEFAULT (unixepoch()),
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_sequence
    ON messages(conversation_id, sequence_order);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_parent
    ON messages(conversation_id, parent_id);

CREATE INDEX IF NOT EXISTS idx_messages_model_slug
    ON messages(model_slug)
    WHERE model_slug IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_messages_author_name
    ON messages(author_name)
    WHERE author_name IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_attachments_message_id
    ON attachments(message_id);

CREATE INDEX IF NOT EXISTS idx_conversations_create_time
    ON conversations(create_time);

CREATE INDEX IF NOT EXISTS idx_conversations_model_slug
    ON conversations(model_slug)
    WHERE model_slug IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_conversations_title
    ON conversations(title);
```

## Field Mappings

### conversations table

| DB Field | OpenAI Export Field | Type | Notes |
|----------|---------------------|------|-------|
| `openai_id` | `id` or `conversation_id` | TEXT | Primary archive identifier |
| `title` | `title` | TEXT | Nullable |
| `create_time` | `create_time` | REAL | Unix timestamp |
| `update_time` | `update_time` | REAL | Unix timestamp |
| `model_slug` | `default_model_slug` | TEXT | Conversation default model |
| `current_node_id` | `current_node` | TEXT | Traversal anchor for active path |
| `metadata` | all top-level conversation keys except `mapping` and dedicated columns | TEXT | JSON blob preserving non-normalized conversation state |
| `is_archived` | `is_archived` | INTEGER | Boolean as 0/1 |
| `is_favorite` | local app state | INTEGER | Not from export |

### conversation_sources table

| DB Field | OpenAI Export Field | Type | Notes |
|----------|---------------------|------|-------|
| `conversation_id` | derived FK to `conversations.id` | INTEGER | 1:1 raw payload preservation row |
| `mapping_json` | `mapping` | TEXT | Full raw mapping object preserved exactly once, including inactive edit branches, `children[]`, and full node payloads |

### messages table

| DB Field | OpenAI Export Field | Type | Notes |
|----------|---------------------|------|-------|
| `openai_id` | mapping key / node id | TEXT | Message tree node id |
| `parent_id` | `mapping[node].parent` | TEXT | Parent node id in source tree; not enforced as an FK because the root sentinel node is not inserted into `messages` |
| `author_role` | `message.author.role` | TEXT | `user` / `assistant` / `system` / `tool` |
| `author_name` | `message.author.name` | TEXT | Tool identity, e.g. `web.run`, `canmore`, `python` |
| `model_slug` | `message.metadata.model_slug` | TEXT | Per-response model; NULL for nodes that do not carry it |
| `content` | derived from `message.content.parts[]` | TEXT | Joined string parts in source order; non-string parts JSON-serialized; cite tokens preserved verbatim |
| `content_type` | `message.content.content_type` | TEXT | `text`, `multimodal_text`, `thoughts`, `execution_output`, etc. |
| `create_time` | `message.create_time` | REAL | Unix timestamp, nullable |
| `sequence_order` | derived active-path index | INTEGER | 1-based canonical display order |
| `weight` | `message.weight` | REAL | Retained raw source value even though not useful for branch discrimination |
| `is_hidden` | `message.metadata.is_visually_hidden_from_conversation` | INTEGER | Denormalized copy for query efficiency |
| `metadata` | `message.metadata` | TEXT | Full raw metadata dict as JSON blob |

### attachments table

Unchanged from earlier features. Attachments remain normalized and associated with the imported `messages.id` row.

## Ground Truth Parsing Model

The source of truth is the ChatGPT export `conversations.json`, not the SQLite database. Import begins by parsing that file as a JSON array of conversation objects.

### Conversation-level parse

For each conversation object:

1. Read the archive identifier from `id` or `conversation_id`.
2. Read dedicated conversation fields into normalized columns:
    - `title`
    - `create_time`
    - `update_time`
    - `default_model_slug` -> `conversations.model_slug`
    - `current_node` -> `conversations.current_node_id`
    - `is_archived`
3. Persist all remaining top-level non-mapping fields into `conversations.metadata`.
4. Persist the full raw `mapping` object into `conversation_sources.mapping_json`.

### Mapping-node parse

Each `mapping` entry is keyed by a node ID and contains:
- `message`
- `parent`
- `children[]`

Parsing rules:

1. The mapping key is the canonical node identity and becomes `messages.openai_id` when the node is projected into the canonical transcript.
2. `parent` becomes `messages.parent_id`.
3. `children[]` is not normalized into `messages`; it is preserved in `conversation_sources.mapping_json`.
4. Nodes whose `message` is `null` are root sentinel nodes and are never inserted into `messages`.

### Message-object parse

For each imported node with a non-null `message`:

1. Read `message.author.role` -> `messages.author_role`.
2. Read `message.author.name` -> `messages.author_name`.
3. Read `message.create_time` -> `messages.create_time`.
4. Read `message.weight` -> `messages.weight`.
5. Read `message.content.content_type` -> `messages.content_type`.
6. Read `message.metadata.model_slug` -> `messages.model_slug`.
7. Read `message.metadata.is_visually_hidden_from_conversation` -> `messages.is_hidden`.
8. Persist the full `message.metadata` dict into `messages.metadata`.

### Content parse

`messages.content` is a display-oriented projection of `message.content.parts[]`, preserving source order.

Rules:

1. If `parts[]` is empty, `messages.content` is `NULL`.
2. String parts are preserved byte-for-byte, including inline cite tokens such as `\ue200cite\ue202...\ue201`.
3. Non-string parts are serialized with `json.dumps(...)`, never `str(...)`.
4. Multiple parts are joined with newline separators in source order.
5. `tool/execution_output` content remains `NULL`; execution payloads live in `messages.metadata.aggregate_result`.

## Import Semantics

### Canonical path selection

Before projecting canonical rows into `messages`, persist the full raw tree into `conversation_sources.mapping_json`.

1. Read `conversation.current_node`.
2. Walk `mapping[node].parent` until the root sentinel node.
3. Reverse the collected path to obtain chronological order.
4. Skip the root sentinel node because its `message` field is null.
5. Insert only nodes on the active path, except FR-008 fallback mode.

### Import projection flow

For each parsed conversation, import proceeds in this order:

1. Insert the normalized conversation row into `conversations`.
2. Insert the full raw `mapping` into `conversation_sources` for that conversation.
3. Compute the canonical path from `current_node`, or enter fallback mode if it is missing/unresolvable.
4. Parse each selected node into a canonical `messages` row.
5. Assign `sequence_order` from the canonical path position, or from fallback ordering rules.
6. Insert normalized attachments for each imported message after the message row exists.

This makes `conversation_sources` the preserved raw tree store and `messages` the app-facing transcript projection.

### Fallback mode when `current_node` is missing

- Import all mapping nodes.
- Assign `sequence_order` by `create_time` ascending, with `openai_id` ascending as a deterministic tie-breaker when timestamps are equal or null.
- Log a warning with `conversation.openai_id`.
- Preserve all data; do not fail the import.

### No-discard rule

- No field present in the export may be dropped during import.
- The canonical `messages` table is a projection, not the only preserved source of truth.
- Full-tree fidelity is preserved in `conversation_sources.mapping_json`.
- Dedicated columns exist only for data that is either queried often or needed for integrity / ordering.

### Parse-to-storage summary

| Source location | Parse result | Storage target |
|----------------|--------------|----------------|
| conversation top-level dedicated fields | normalized scalar values | `conversations` |
| conversation top-level non-dedicated fields | JSON blob | `conversations.metadata` |
| conversation `mapping` | raw JSON blob | `conversation_sources.mapping_json` |
| active-path node identity and ordering | normalized transcript rows | `messages` |
| message metadata dict | JSON blob | `messages.metadata` |
| message attachments | normalized attachment rows | `attachments` |

## JSON Storage Rules

### messages.metadata

Stores `json.dumps(message.metadata)` exactly once for every imported node.

High-value fields retained inside the blob include:
- `search_queries`
- `reasoning_title`
- `finished_duration_sec`
- `aggregate_result`
- `citations`
- `content_references`
- `model_slug`
- `display_title`
- `display_url`

### conversation_sources.mapping_json

Stores `json.dumps(conversation['mapping'])` exactly once for every imported conversation.

This preserves raw source fields that are intentionally not normalized into dedicated columns, including:
- inactive edit branches excluded from the canonical transcript
- node `children[]` arrays
- raw `message.status`, `message.end_turn`, `message.recipient`, `message.channel`, and any future unmodeled keys
- the original message content object shape, beyond the display-oriented `content` projection stored in `messages`

### conversations.metadata

Stores all conversation-level keys except:
- `mapping` (preserved in `conversation_sources.mapping_json`)
- `id` / `conversation_id` / `title` / `create_time` / `update_time` / `default_model_slug` / `current_node` / `is_archived`

Observed high-value fields that would otherwise be lost:
- `memory_scope`
- `is_do_not_remember`
- `safe_urls`
- `gizmo_id`
- `gizmo_type`
- `conversation_template_id`
- `conversation_origin`
- `plugin_ids`
- `async_status`
- `voice`
- `disabled_tool_ids`

## Validation Rules

1. **Conversation identity**: `conversations.openai_id` must be unique.
2. **Canonical ordering**: `messages.sequence_order` must be unique within a conversation.
3. **Role constraint**: `messages.author_role` must be one of `user`, `assistant`, `system`, `tool`.
4. **JSON validity**: every non-null `messages.metadata` and `conversations.metadata` value must pass `json_valid()`.
5. **Raw tree preservation**: every imported conversation must have exactly one `conversation_sources` row whose `mapping_json` passes `json_valid()`.
6. **Cite preservation**: if source `parts[]` contains `\ue200cite\ue202...\ue201`, `messages.content` must preserve that token byte-for-byte.
7. **Execution output retention**: `tool/execution_output` rows may have null `content`, but their `metadata` must contain `aggregate_result` when present in the source.
8. **Sentinel exclusion**: no row may be created for a mapping node whose `message` is null.
9. **Message identity**: `messages.openai_id` must be unique within a conversation.
10. **Deterministic fallback ordering**: when fallback mode is used, repeated imports of the same source data must produce the same `sequence_order` values.

## Query Guidance

### Prefer dedicated columns for common filters

Use dedicated columns for:
- conversation lists by `conversations.model_slug`
- conversation lists by `conversations.title`
- per-response model analysis by `messages.model_slug`
- tool-type filtering by `messages.author_name`
- canonical display order by `messages.sequence_order`

Use `conversation_sources.mapping_json` for:
- future branch-history UX without re-import
- debugging tree anomalies
- recovery of raw node fields that were intentionally not normalized into `messages`

### Use JSON blobs for long-tail fields

Use `json_extract()` on blobs for fields that are preserved for fidelity but not common filters, e.g.:

```sql
SELECT openai_id,
       json_extract(metadata, '$.memory_scope') AS memory_scope,
       json_extract(metadata, '$.gizmo_id') AS gizmo_id
FROM conversations;

SELECT openai_id,
       json_extract(metadata, '$.finished_duration_sec') AS duration,
       json_extract(metadata, '$.aggregate_result.status') AS exec_status
FROM messages
WHERE content_type IN ('reasoning_recap', 'execution_output');
```

## Notes for Rendering

- Cite rendering must operate against raw `content` plus `metadata.content_references` / `metadata.citations`.
- `content` is intentionally raw-source-oriented, not display-normalized.
- Display transformations belong in the formatting layer, not the importer.
