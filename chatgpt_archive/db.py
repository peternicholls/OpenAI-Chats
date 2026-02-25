"""Database connection and schema management for ChatGPT archive."""

import os
import sqlite3
import struct
from pathlib import Path

# Default database location
DEFAULT_DB_DIR = Path.home() / ".chatgpt-archive"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "chats.db"

# SQL schema from data-model.md
SCHEMA_SQL = """
-- Core tables
CREATE TABLE IF NOT EXISTS conversations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    openai_id     TEXT UNIQUE NOT NULL,
    title         TEXT,
    create_time   REAL,
    update_time   REAL,
    model_slug    TEXT,
    is_archived   INTEGER DEFAULT 0,
    is_favorite   INTEGER NOT NULL DEFAULT 0
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

-- Tags system
CREATE TABLE IF NOT EXISTS tags (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT UNIQUE NOT NULL COLLATE NOCASE
);

CREATE TABLE IF NOT EXISTS conversation_tags (
    conversation_id INTEGER NOT NULL,
    tag_id          INTEGER NOT NULL,
    PRIMARY KEY (conversation_id, tag_id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_conversation_tags_tag ON conversation_tags(tag_id);
"""

# Embeddings schema (separate so it can be applied when semantic feature is enabled)
EMBEDDINGS_SCHEMA_SQL = """
-- Vector embeddings table for semantic search
CREATE TABLE IF NOT EXISTS message_embeddings (
    message_id      INTEGER PRIMARY KEY,
    embedding       BLOB NOT NULL,
    model           TEXT DEFAULT 'text-embedding-3-small',
    created_at      REAL DEFAULT (unixepoch()),
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
);

-- Index for faster embedding lookups
CREATE INDEX IF NOT EXISTS idx_embeddings_created ON message_embeddings(created_at);
"""

# Embedding dimensions for supported models
EMBEDDING_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}

# Versioned, idempotent DDL patches applied by run_migrations()
_MIGRATIONS = [
    # Migration 1: add is_favorite column to conversations
    (
        1,
        "ALTER TABLE conversations ADD COLUMN is_favorite INTEGER NOT NULL DEFAULT 0",
    ),
]


def run_migrations(conn: sqlite3.Connection) -> None:
    """Apply versioned schema migrations idempotently.

    Creates a schema_migrations table to track which patches have been
    applied, then runs any patches not yet recorded.

    Args:
        conn: Database connection
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at REAL DEFAULT (unixepoch())
        )
    """
    )
    conn.commit()

    applied = {
        row[0]
        for row in conn.execute("SELECT version FROM schema_migrations").fetchall()
    }

    for version, ddl in _MIGRATIONS:
        if version in applied:
            continue
        try:
            conn.execute(ddl)
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (?)", (version,)
            )
            conn.commit()
        except sqlite3.OperationalError:
            # Column/object already exists — mark as applied and continue
            conn.execute(
                "INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)",
                (version,),
            )
            conn.commit()


def get_db_path() -> Path:
    """Get database path from environment or use default.

    Checks CHATGPT_ARCHIVE_DB environment variable first,
    falls back to ~/.chatgpt-archive/chats.db

    Returns:
        Path to the database file
    """
    env_path = os.environ.get("CHATGPT_ARCHIVE_DB")
    if env_path:
        return Path(env_path).expanduser()
    return DEFAULT_DB_PATH


def ensure_db_dir(db_path: Path) -> None:
    """Ensure the database directory exists.

    Args:
        db_path: Path to the database file
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Get a database connection with proper settings.

    Args:
        db_path: Optional path to database file. If None, uses default.

    Returns:
        SQLite connection with foreign keys enabled and WAL mode
    """
    if db_path is None:
        db_path = get_db_path()
    else:
        db_path = Path(db_path).expanduser()

    ensure_db_dir(db_path)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows

    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")

    # Use WAL mode for better concurrent read performance
    conn.execute("PRAGMA journal_mode = WAL")

    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Initialize database schema.

    Creates all tables, indexes, triggers, and FTS5 virtual table
    if they don't exist.

    Args:
        conn: Database connection
    """
    conn.executescript(SCHEMA_SQL)
    conn.commit()


def init_db(db_path: Path | None = None) -> sqlite3.Connection:
    """Initialize database with schema.

    Convenience function that gets connection and initializes schema,
    then applies any pending migrations.

    Args:
        db_path: Optional path to database file

    Returns:
        Initialized database connection
    """
    conn = get_connection(db_path)
    init_schema(conn)
    run_migrations(conn)
    return conn


def get_db_size(db_path: Path | None = None) -> int:
    """Get database file size in bytes.

    Args:
        db_path: Optional path to database file

    Returns:
        File size in bytes, or 0 if file doesn't exist
    """
    if db_path is None:
        db_path = get_db_path()
    else:
        db_path = Path(db_path).expanduser()

    if db_path.exists():
        return db_path.stat().st_size
    return 0


def is_sqlite_vec_available() -> bool:
    """Check if the sqlite-vec extension is available.

    Returns:
        True if sqlite-vec can be loaded
    """
    try:
        import sqlite_vec  # type: ignore[import-untyped]  # noqa: F401

        return True
    except ImportError:
        return False


def load_sqlite_vec(conn: sqlite3.Connection) -> bool:
    """Load the sqlite-vec extension into a connection.

    Args:
        conn: Database connection to load the extension into

    Returns:
        True if extension was loaded successfully, False otherwise
    """
    try:
        import sqlite_vec  # type: ignore[import-untyped]

        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        return True
    except (ImportError, Exception):
        return False


def init_embeddings_schema(conn: sqlite3.Connection) -> None:
    """Initialize the embeddings table schema.

    Creates the message_embeddings table if it doesn't exist.

    Args:
        conn: Database connection
    """
    conn.executescript(EMBEDDINGS_SCHEMA_SQL)
    conn.commit()


def init_vec_table(conn: sqlite3.Connection, dimensions: int = 1536) -> bool:
    """Initialize the sqlite-vec virtual table for similarity search.

    Creates a virtual table that allows efficient nearest-neighbor
    vector search using the sqlite-vec extension.

    Args:
        conn: Database connection (must have sqlite-vec loaded)
        dimensions: Embedding vector dimensions (default: 1536 for text-embedding-3-small)

    Returns:
        True if virtual table was created successfully
    """
    try:
        conn.execute(
            f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS vec_messages 
            USING vec0(
                message_id INTEGER PRIMARY KEY,
                embedding float[{dimensions}]
            )
        """
        )
        conn.commit()
        return True
    except Exception:
        return False


def serialize_embedding(embedding: list) -> bytes:
    """Serialize a float list to a binary blob for storage.

    Args:
        embedding: List of float values

    Returns:
        Binary blob of packed float32 values
    """
    return struct.pack(f"{len(embedding)}f", *embedding)


def deserialize_embedding(blob: bytes) -> list:
    """Deserialize a binary blob back to a float list.

    Args:
        blob: Binary blob of packed float32 values

    Returns:
        List of float values
    """
    n = len(blob) // 4  # 4 bytes per float32
    return list(struct.unpack(f"{n}f", blob))


def get_conversation_by_id(
    conn: sqlite3.Connection, openai_id: str
) -> sqlite3.Row | None:
    """Retrieve a conversation by its OpenAI ID.

    Args:
        conn: Database connection
        openai_id: The OpenAI conversation ID (UUID string)

    Returns:
        Row with conversation data, or None if not found
    """
    row = conn.execute(
        """
        SELECT c.id, c.openai_id, c.title, c.create_time, c.update_time,
               c.model_slug, c.is_archived,
               (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count
        FROM conversations c
        WHERE c.openai_id = ?
        """,
        (openai_id,),
    ).fetchone()
    return row


def get_conversation_messages(
    conn: sqlite3.Connection, conversation_db_id: int, include_hidden: bool = False
) -> list:
    """Retrieve all messages for a conversation in chronological order.

    Messages are ordered by their database insertion order (id), which
    corresponds to the tree traversal order from import. Hidden system
    messages are excluded by default.

    Args:
        conn: Database connection
        conversation_db_id: The internal database ID of the conversation
        include_hidden: Whether to include hidden system messages

    Returns:
        List of Row objects with message data
    """
    if include_hidden:
        rows = conn.execute(
            """
            SELECT id, openai_id, parent_id, author_role, content,
                   content_type, create_time, weight, is_hidden
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id
            """,
            (conversation_db_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT id, openai_id, parent_id, author_role, content,
                   content_type, create_time, weight, is_hidden
            FROM messages
            WHERE conversation_id = ? AND is_hidden = 0
            ORDER BY id
            """,
            (conversation_db_id,),
        ).fetchall()
    return rows


def get_embedding_stats(conn: sqlite3.Connection) -> dict:
    """Get statistics about stored embeddings.

    Args:
        conn: Database connection

    Returns:
        Dictionary with embedding statistics
    """
    try:
        total_messages = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE content IS NOT NULL AND content != ''"
        ).fetchone()[0]

        embedded_count = conn.execute(
            "SELECT COUNT(*) FROM message_embeddings"
        ).fetchone()[0]

        model = None
        if embedded_count > 0:
            row = conn.execute(
                "SELECT model FROM message_embeddings LIMIT 1"
            ).fetchone()
            model = row[0] if row else None

        return {
            "total_messages": total_messages,
            "embedded_count": embedded_count,
            "remaining": total_messages - embedded_count,
            "model": model,
            "percent_complete": round(
                (embedded_count / total_messages * 100) if total_messages > 0 else 0, 1
            ),
        }
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        return {
            "total_messages": 0,
            "embedded_count": 0,
            "remaining": 0,
            "model": None,
            "percent_complete": 0,
        }


def list_conversations(
    conn: sqlite3.Connection,
    sort_by: str = "date",
    order: str = "desc",
    limit: int = 50,
    offset: int = 0,
) -> tuple:
    """List conversations with message counts and pagination.

    Args:
        conn: Database connection
        sort_by: Field to sort by: 'date', 'title', 'messages'
        order: Sort order: 'asc' or 'desc'
        limit: Maximum number of results
        offset: Number of results to skip (pagination)

    Returns:
        Tuple of (conversations list, total count)
    """
    # Map sort_by to actual SQL columns
    sort_map = {
        "date": "c.create_time",
        "title": "c.title",
        "messages": "message_count",
    }
    sort_column = sort_map.get(sort_by, "c.create_time")

    # Validate order
    order_clause = "DESC" if order.lower() == "desc" else "ASC"

    # Handle NULL values in sorting (put NULLs at end for DESC, beginning for ASC)
    null_handling = "NULLS LAST" if order_clause == "DESC" else "NULLS FIRST"

    # Get total count
    total = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]

    # Query conversations with message counts
    query = f"""
        SELECT c.id, c.openai_id, c.title, c.create_time, c.update_time,
               c.model_slug, c.is_archived, c.is_favorite,
               (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count
        FROM conversations c
        ORDER BY {sort_column} {order_clause} {null_handling}
        LIMIT ? OFFSET ?
    """

    rows = conn.execute(query, (limit, offset)).fetchall()

    return list(rows), total


def get_conversation_count(conn: sqlite3.Connection) -> int:
    """Get total number of conversations.

    Args:
        conn: Database connection

    Returns:
        Total conversation count
    """
    return conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]


def get_total_message_count(conn: sqlite3.Connection) -> int:
    """Get total number of messages across all conversations.

    Args:
        conn: Database connection

    Returns:
        Total message count
    """
    return conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]


def delete_conversation(conn: sqlite3.Connection, openai_id: str) -> bool:
    """Delete a conversation and all its messages by OpenAI ID.

    Cascading deletes will remove associated messages, attachments,
    and embeddings due to ON DELETE CASCADE foreign key constraints.

    Args:
        conn: Database connection
        openai_id: The OpenAI conversation ID (UUID string)

    Returns:
        True if the conversation was found and deleted, False if not found
    """
    cursor = conn.execute(
        "SELECT id FROM conversations WHERE openai_id = ?", (openai_id,)
    )
    row = cursor.fetchone()
    if row is None:
        return False

    db_id = row[0]

    # Collect message IDs before deletion (for targeted embedding cleanup)
    msg_rows = conn.execute(
        "SELECT id FROM messages WHERE conversation_id = ?", (db_id,)
    ).fetchall()
    message_ids = [r[0] for r in msg_rows]

    # Delete messages first (triggers FTS cleanup via triggers)
    conn.execute("DELETE FROM messages WHERE conversation_id = ?", (db_id,))

    # Delete embeddings for only the removed messages (not a full-table scan)
    if message_ids:
        placeholders = ",".join("?" * len(message_ids))
        try:
            conn.execute(
                f"DELETE FROM message_embeddings WHERE message_id IN ({placeholders})",
                message_ids,
            )
        except sqlite3.OperationalError:
            pass  # Embeddings table may not exist

    # Delete the conversation
    conn.execute("DELETE FROM conversations WHERE id = ?", (db_id,))
    conn.commit()

    return True


def add_tag(conn: sqlite3.Connection, openai_id: str, tag_name: str) -> bool:
    """Add a tag to a conversation.

    Creates the tag if it doesn't exist, then associates it with the conversation.
    Tag names are case-insensitive (stored as-is but compared case-insensitively).

    Args:
        conn: Database connection
        openai_id: The OpenAI conversation ID
        tag_name: Tag name to add

    Returns:
        True if tag was added, False if conversation not found

    Raises:
        ValueError: If tag_name is empty
    """
    tag_name = tag_name.strip()
    if not tag_name:
        raise ValueError("Tag name cannot be empty")

    # Get conversation DB id
    row = conn.execute(
        "SELECT id FROM conversations WHERE openai_id = ?", (openai_id,)
    ).fetchone()
    if row is None:
        return False
    conv_db_id = row[0]

    # Create or get tag
    conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
    tag_row = conn.execute(
        "SELECT id FROM tags WHERE name = ? COLLATE NOCASE", (tag_name,)
    ).fetchone()
    tag_id = tag_row[0]

    # Associate tag with conversation (ignore if already exists)
    conn.execute(
        "INSERT OR IGNORE INTO conversation_tags (conversation_id, tag_id) VALUES (?, ?)",
        (conv_db_id, tag_id),
    )
    conn.commit()
    return True


def remove_tag(conn: sqlite3.Connection, openai_id: str, tag_name: str) -> bool:
    """Remove a tag from a conversation.

    Args:
        conn: Database connection
        openai_id: The OpenAI conversation ID
        tag_name: Tag name to remove

    Returns:
        True if the tag was removed, False if conversation or tag not found
    """
    row = conn.execute(
        "SELECT id FROM conversations WHERE openai_id = ?", (openai_id,)
    ).fetchone()
    if row is None:
        return False
    conv_db_id = row[0]

    tag_row = conn.execute(
        "SELECT id FROM tags WHERE name = ? COLLATE NOCASE", (tag_name.strip(),)
    ).fetchone()
    if tag_row is None:
        return False
    tag_id = tag_row[0]

    cursor = conn.execute(
        "DELETE FROM conversation_tags WHERE conversation_id = ? AND tag_id = ?",
        (conv_db_id, tag_id),
    )
    conn.commit()

    # Clean up orphan tags (no conversations using them)
    conn.execute(
        "DELETE FROM tags WHERE id NOT IN (SELECT DISTINCT tag_id FROM conversation_tags)"
    )
    conn.commit()

    return cursor.rowcount > 0


def get_conversation_tags(conn: sqlite3.Connection, openai_id: str) -> list:
    """Get all tags for a conversation.

    Args:
        conn: Database connection
        openai_id: The OpenAI conversation ID

    Returns:
        List of tag name strings
    """
    rows = conn.execute(
        """
        SELECT t.name
        FROM tags t
        JOIN conversation_tags ct ON t.id = ct.tag_id
        JOIN conversations c ON ct.conversation_id = c.id
        WHERE c.openai_id = ?
        ORDER BY t.name
        """,
        (openai_id,),
    ).fetchall()
    return [row[0] for row in rows]


def list_all_tags(conn: sqlite3.Connection) -> list:
    """List all tags with usage counts.

    Args:
        conn: Database connection

    Returns:
        List of dicts with 'name' and 'count' keys
    """
    rows = conn.execute(
        """
        SELECT t.name, COUNT(ct.conversation_id) as count
        FROM tags t
        LEFT JOIN conversation_tags ct ON t.id = ct.tag_id
        GROUP BY t.id
        ORDER BY t.name
        """
    ).fetchall()
    return [{"name": row[0], "count": row[1]} for row in rows]


def rename_tag(conn: sqlite3.Connection, old_name: str, new_name: str) -> bool:
    """Rename a tag across all conversations.

    Args:
        conn: Database connection
        old_name: Existing tag name
        new_name: New tag name

    Returns:
        True if the tag was found and renamed, False if not found.

    Raises:
        ValueError: If new_name is empty.
    """
    new_name = new_name.strip()
    if not new_name:
        raise ValueError("New tag name cannot be empty")

    tag_row = conn.execute(
        "SELECT id FROM tags WHERE name = ? COLLATE NOCASE",
        (old_name.strip(),),
    ).fetchone()
    if tag_row is None:
        return False

    conn.execute("UPDATE tags SET name = ? WHERE id = ?", (new_name, tag_row[0]))
    conn.commit()
    return True


def list_conversations_by_tag(
    conn: sqlite3.Connection,
    tag_name: str,
    sort_by: str = "date",
    order: str = "desc",
    limit: int = 50,
    offset: int = 0,
) -> tuple:
    """List conversations that have a specific tag.

    Args:
        conn: Database connection
        tag_name: Tag name to filter by
        sort_by: Sort field: 'date', 'title', 'messages'
        order: Sort order: 'asc' or 'desc'
        limit: Maximum results
        offset: Pagination offset

    Returns:
        Tuple of (conversations list, total count)
    """
    sort_map = {
        "date": "c.create_time",
        "title": "c.title",
        "messages": "message_count",
    }
    sort_column = sort_map.get(sort_by, "c.create_time")
    order_clause = "DESC" if order.lower() == "desc" else "ASC"
    null_handling = "NULLS LAST" if order_clause == "DESC" else "NULLS FIRST"

    # Get total count for this tag
    total = conn.execute(
        """
        SELECT COUNT(DISTINCT ct.conversation_id)
        FROM conversation_tags ct
        JOIN tags t ON ct.tag_id = t.id
        WHERE t.name = ? COLLATE NOCASE
        """,
        (tag_name.strip(),),
    ).fetchone()[0]

    query = f"""
        SELECT c.id, c.openai_id, c.title, c.create_time, c.update_time,
               c.model_slug, c.is_archived, c.is_favorite,
               (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count
        FROM conversations c
        JOIN conversation_tags ct ON c.id = ct.conversation_id
        JOIN tags t ON ct.tag_id = t.id
        WHERE t.name = ? COLLATE NOCASE
        ORDER BY {sort_column} {order_clause} {null_handling}
        LIMIT ? OFFSET ?
    """

    rows = conn.execute(query, (tag_name.strip(), limit, offset)).fetchall()
    return list(rows), total
