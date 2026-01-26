# Data Model: ChatGPT Archive Search & Export

**Feature**: 001-archive-search-export | **Date**: 2026-01-26

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      conversations                           │
├─────────────────────────────────────────────────────────────┤
│ id            INTEGER PRIMARY KEY AUTOINCREMENT             │
│ openai_id     TEXT UNIQUE NOT NULL                          │
│ title         TEXT                                          │
│ create_time   REAL                                          │
│ update_time   REAL                                          │
│ model_slug    TEXT                                          │
│ is_archived   INTEGER DEFAULT 0                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        messages                              │
├─────────────────────────────────────────────────────────────┤
│ id              INTEGER PRIMARY KEY AUTOINCREMENT           │
│ conversation_id INTEGER NOT NULL REFERENCES conversations   │
│ openai_id       TEXT NOT NULL                               │
│ parent_id       TEXT                                        │
│ author_role     TEXT NOT NULL                               │
│ content         TEXT                                        │
│ content_type    TEXT DEFAULT 'text'                         │
│ create_time     REAL                                        │
│ weight          REAL DEFAULT 1.0                            │
│ is_hidden       INTEGER DEFAULT 0                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      attachments                             │
├─────────────────────────────────────────────────────────────┤
│ id              INTEGER PRIMARY KEY AUTOINCREMENT           │
│ message_id      INTEGER NOT NULL REFERENCES messages        │
│ file_path       TEXT NOT NULL                               │
│ file_type       TEXT                                        │
│ original_name   TEXT                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    messages_fts (FTS5)                       │
├─────────────────────────────────────────────────────────────┤
│ rowid           → messages.id                               │
│ content         TEXT (full-text indexed)                    │
└─────────────────────────────────────────────────────────────┘
```

## Schema DDL

```sql
-- Core tables
CREATE TABLE IF NOT EXISTS conversations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    openai_id     TEXT UNIQUE NOT NULL,
    title         TEXT,
    create_time   REAL,
    update_time   REAL,
    model_slug    TEXT,
    is_archived   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    openai_id       TEXT NOT NULL,
    parent_id       TEXT,
    author_role     TEXT NOT NULL CHECK (author_role IN ('user', 'assistant', 'system', 'tool')),
    content         TEXT,
    content_type    TEXT DEFAULT 'text',
    create_time     REAL,
    weight          REAL DEFAULT 1.0,
    is_hidden       INTEGER DEFAULT 0,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attachments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id      INTEGER NOT NULL,
    file_path       TEXT NOT NULL,
    file_type       TEXT,
    original_name   TEXT,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
);

-- Full-text search index
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    content,
    tokenize='porter unicode61',
    content='messages',
    content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
END;

CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, content) VALUES('delete', old.id, old.content);
END;

CREATE TRIGGER IF NOT EXISTS messages_au AFTER UPDATE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, content) VALUES('delete', old.id, old.content);
    INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
END;

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_parent ON messages(parent_id);
CREATE INDEX IF NOT EXISTS idx_conversations_create_time ON conversations(create_time);
CREATE INDEX IF NOT EXISTS idx_conversations_title ON conversations(title);
```

## Field Mappings

### conversations table

| DB Field | OpenAI Export Field | Type | Notes |
|----------|---------------------|------|-------|
| openai_id | `conversation_id` or `id` | TEXT | Primary identifier from export |
| title | `title` | TEXT | May be null, use fallback |
| create_time | `create_time` | REAL | Unix timestamp |
| update_time | `update_time` | REAL | Unix timestamp |
| model_slug | `default_model_slug` | TEXT | e.g., "gpt-4", "gpt-3.5-turbo" |
| is_archived | `is_archived` | INTEGER | Boolean as 0/1 |

### messages table

| DB Field | OpenAI Export Field | Type | Notes |
|----------|---------------------|------|-------|
| openai_id | `mapping[node_id].id` | TEXT | Node ID in message tree |
| parent_id | `mapping[node_id].parent` | TEXT | Parent node ID |
| author_role | `message.author.role` | TEXT | user/assistant/system/tool |
| content | `message.content.parts[0]` | TEXT | Joined if multiple parts |
| content_type | `message.content.content_type` | TEXT | text, image, etc. |
| create_time | `message.create_time` | REAL | May be null |
| weight | `message.weight` | REAL | Tree weighting |
| is_hidden | `message.metadata.is_visually_hidden_from_conversation` | INTEGER | Hidden system messages |

## Validation Rules

1. **conversation.openai_id**: Must be unique, used for idempotent imports
2. **message.author_role**: Must be one of: user, assistant, system, tool
3. **message.conversation_id**: Must reference existing conversation
4. **Foreign keys**: Enforced via `PRAGMA foreign_keys = ON`

## State Transitions

No complex state machines. Conversations and messages are immutable after import.

## Example Queries

```sql
-- Search for keyword with relevance ranking
SELECT c.id, c.title, c.create_time,
       snippet(messages_fts, 0, '**', '**', '...', 50) as preview,
       bm25(messages_fts) as score
FROM messages_fts
JOIN messages m ON messages_fts.rowid = m.id
JOIN conversations c ON m.conversation_id = c.id
WHERE messages_fts MATCH 'machine learning'
GROUP BY c.id
ORDER BY score
LIMIT 20;

-- Get conversation with all messages in order
SELECT m.author_role, m.content, m.create_time
FROM messages m
WHERE m.conversation_id = ?
  AND m.is_hidden = 0
ORDER BY m.id;

-- List conversations by date
SELECT id, openai_id, title, 
       datetime(create_time, 'unixepoch') as created,
       (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as msg_count
FROM conversations c
ORDER BY create_time DESC;
```
