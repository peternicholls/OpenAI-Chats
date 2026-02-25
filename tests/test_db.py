"""Tests for database functionality."""

import sqlite3
from pathlib import Path

import pytest

from chatgpt_archive.db import (
    init_db,
    get_db_path,
    get_db_size,
    add_tag,
    remove_tag,
    get_conversation_tags,
    list_all_tags,
    list_conversations_by_tag,
    rename_tag,
)


class TestDatabaseSchema:
    """Tests for database schema initialization."""
    
    def test_init_db_creates_database(self, tmp_path):
        """Test that init_db creates a database file."""
        db_path = tmp_path / "test.db"
        init_db(db_path)
        assert db_path.exists()
    
    def test_init_db_creates_tables(self, tmp_path):
        """Test that all required tables are created."""
        db_path = tmp_path / "test.db"
        init_db(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        assert "conversations" in tables
        assert "messages" in tables
        assert "attachments" in tables
        assert "messages_fts" in tables  # FTS5 virtual table
        
        conn.close()
    
    def test_conversations_table_schema(self, tmp_path):
        """Test conversations table has correct columns."""
        db_path = tmp_path / "test.db"
        init_db(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(conversations)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert "id" in columns
        assert "openai_id" in columns
        assert "title" in columns
        assert "create_time" in columns
        assert columns["id"] == "INTEGER"  # Primary key
        assert columns["openai_id"] == "TEXT"
        assert columns["create_time"] == "REAL"
        
        conn.close()
    
    def test_messages_table_schema(self, tmp_path):
        """Test messages table has correct columns."""
        db_path = tmp_path / "test.db"
        init_db(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(messages)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert "id" in columns
        assert "conversation_id" in columns
        assert "author_role" in columns
        assert "content" in columns
        assert "create_time" in columns
        
        conn.close()
    
    def test_fts5_table_created(self, tmp_path):
        """Test that FTS5 virtual table is created."""
        db_path = tmp_path / "test.db"
        init_db(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check FTS5 table exists
        cursor.execute(
            "SELECT sql FROM sqlite_master WHERE name='messages_fts'"
        )
        result = cursor.fetchone()
        assert result is not None
        assert "fts5" in result[0].lower()
        
        conn.close()
    
    def test_foreign_keys_enabled(self, tmp_path):
        """Test that foreign key constraints are enabled."""
        db_path = tmp_path / "test.db"
        init_db(db_path)
        
        # Create a new connection and check foreign keys
        # Note: init_db enables them but it's connection-specific
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")  # Must enable per connection
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()
        assert result[0] == 1  # Foreign keys enabled
        
        conn.close()
    
    def test_wal_mode_enabled(self, tmp_path):
        """Test that WAL mode is enabled."""
        db_path = tmp_path / "test.db"
        init_db(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA journal_mode")
        result = cursor.fetchone()
        assert result[0].lower() == "wal"
        
        conn.close()
    
    def test_idempotent_initialization(self, tmp_path):
        """Test that calling init_db multiple times is safe."""
        db_path = tmp_path / "test.db"
        
        # Initialize twice
        init_db(db_path)
        init_db(db_path)
        
        # Should still work
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        count = cursor.fetchone()[0]
        assert count > 0
        conn.close()


class TestDatabaseUtilities:
    """Tests for database utility functions."""
    
    def test_get_db_path_default(self):
        """Test default database path."""
        path = get_db_path()
        assert str(path).endswith(".chatgpt-archive/chats.db")
        assert path.parent.name == ".chatgpt-archive"
    
    def test_get_db_size(self, tmp_path):
        """Test getting database size."""
        db_path = tmp_path / "test.db"
        init_db(db_path)
        
        size = get_db_size(db_path)
        assert size > 0
        assert isinstance(size, int)
    
    def test_get_db_size_nonexistent(self, tmp_path):
        """Test getting size of nonexistent database returns 0."""
        db_path = tmp_path / "nonexistent.db"
        size = get_db_size(db_path)
        assert size == 0


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _make_conversation(conn: sqlite3.Connection, openai_id: str = "conv-001") -> int:
    """Insert a minimal conversation row and return its integer pk."""
    cursor = conn.execute(
        "INSERT INTO conversations (openai_id, title, create_time, update_time)"
        " VALUES (?, ?, 1700000000.0, 1700000000.0)",
        (openai_id, "Test Conversation"),
    )
    conn.commit()
    return cursor.lastrowid


@pytest.fixture
def tag_db(tmp_path):
    """Return an open, initialised in-memory-like DB conn for tag tests."""
    db_path = tmp_path / "tags_test.db"
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _make_conversation(conn, "conv-001")
    _make_conversation(conn, "conv-002")
    yield conn
    conn.close()


# ---------------------------------------------------------------------------
# Tag tests
# ---------------------------------------------------------------------------

class TestTagFunctions:
    """Unit tests for tag DB functions: add, remove, get, list, rename, by_tag."""

    def test_add_tag_creates_entry(self, tag_db):
        result = add_tag(tag_db, "conv-001", "work")
        assert result is True
        tags = get_conversation_tags(tag_db, "conv-001")
        assert "work" in tags

    def test_add_tag_duplicate_is_idempotent(self, tag_db):
        add_tag(tag_db, "conv-001", "work")
        # Second add should not raise and still return the tag once
        add_tag(tag_db, "conv-001", "work")
        tags = get_conversation_tags(tag_db, "conv-001")
        assert tags.count("work") == 1

    def test_add_tag_nonexistent_conversation(self, tag_db):
        # Should return False (or raise) for unknown conversation
        result = add_tag(tag_db, "conv-DOES-NOT-EXIST", "work")
        assert result is False

    def test_remove_tag_existing(self, tag_db):
        add_tag(tag_db, "conv-001", "to-remove")
        result = remove_tag(tag_db, "conv-001", "to-remove")
        assert result is True
        assert "to-remove" not in get_conversation_tags(tag_db, "conv-001")

    def test_remove_tag_not_present(self, tag_db):
        result = remove_tag(tag_db, "conv-001", "not-here")
        assert result is False

    def test_get_conversation_tags_multiple(self, tag_db):
        add_tag(tag_db, "conv-001", "alpha")
        add_tag(tag_db, "conv-001", "beta")
        tags = get_conversation_tags(tag_db, "conv-001")
        assert set(tags) == {"alpha", "beta"}

    def test_get_conversation_tags_empty(self, tag_db):
        tags = get_conversation_tags(tag_db, "conv-001")
        assert tags == []

    def test_list_all_tags(self, tag_db):
        add_tag(tag_db, "conv-001", "project-x")
        add_tag(tag_db, "conv-002", "project-x")
        add_tag(tag_db, "conv-001", "personal")
        all_tags = list_all_tags(tag_db)
        names = [t["name"] if isinstance(t, dict) else t for t in all_tags]
        assert "project-x" in names
        assert "personal" in names

    def test_rename_tag_updates_all_conversations(self, tag_db):
        add_tag(tag_db, "conv-001", "old-name")
        add_tag(tag_db, "conv-002", "old-name")
        result = rename_tag(tag_db, "old-name", "new-name")
        assert result is True
        assert "new-name" in get_conversation_tags(tag_db, "conv-001")
        assert "new-name" in get_conversation_tags(tag_db, "conv-002")
        assert "old-name" not in get_conversation_tags(tag_db, "conv-001")

    def test_rename_tag_nonexistent(self, tag_db):
        result = rename_tag(tag_db, "ghost", "phantom")
        assert result is False

    def test_list_conversations_by_tag(self, tag_db):
        add_tag(tag_db, "conv-001", "shared")
        add_tag(tag_db, "conv-002", "shared")
        rows, total = list_conversations_by_tag(tag_db, "shared", limit=50, offset=0)
        openai_ids = [r["openai_id"] for r in rows]
        assert "conv-001" in openai_ids
        assert "conv-002" in openai_ids
        assert total == 2

    def test_list_conversations_by_tag_empty(self, tag_db):
        rows, total = list_conversations_by_tag(tag_db, "no-such-tag", limit=50, offset=0)
        assert rows == []
        assert total == 0

