"""Database connection and schema management for ChatGPT archive."""

import os
import sqlite3
from pathlib import Path
from typing import Optional

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
"""


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


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
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


def init_db(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Initialize database with schema.
    
    Convenience function that gets connection and initializes schema.
    
    Args:
        db_path: Optional path to database file
        
    Returns:
        Initialized database connection
    """
    conn = get_connection(db_path)
    init_schema(conn)
    return conn


def get_db_size(db_path: Optional[Path] = None) -> int:
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
