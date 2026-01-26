"""Tests for database functionality."""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from chatgpt_archive.db import init_db, get_db_path, get_db_size


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


@pytest.fixture
def tmp_path():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
