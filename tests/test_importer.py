"""Tests for importer functionality."""

import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from chatgpt_archive import importer
from chatgpt_archive.db import init_db


class TestImporterValidation:
    """Tests for import validation logic."""
    
    def test_find_conversations_file_valid(self, tmp_path):
        """Test finding conversations.json in valid archive."""
        # Create mock archive structure
        conversations_file = tmp_path / "conversations.json"
        conversations_file.write_text("[]")
        
        result = importer.find_conversations_file(tmp_path)
        assert result == conversations_file
    
    def test_find_conversations_file_missing(self, tmp_path):
        """Test error when conversations.json is missing."""
        with pytest.raises(importer.InvalidArchiveError, match="conversations.json not found"):
            importer.find_conversations_file(tmp_path)
    
    def test_load_conversations_valid_json(self, tmp_path):
        """Test loading valid conversations JSON."""
        conversations_file = tmp_path / "conversations.json"
        test_data = [
            {
                "id": "conv-1",
                "title": "Test Conversation",
                "create_time": 1710000000,
                "mapping": {}
            }
        ]
        conversations_file.write_text(json.dumps(test_data))
        
        result = importer.load_conversations_json(conversations_file)
        assert len(result) == 1
        assert result[0]["id"] == "conv-1"
    
    def test_load_conversations_invalid_json(self, tmp_path):
        """Test error on invalid JSON."""
        conversations_file = tmp_path / "conversations.json"
        conversations_file.write_text("not valid json {")
        
        with pytest.raises(importer.InvalidJSONError):
            importer.load_conversations_json(conversations_file)
    
    def test_load_conversations_not_array(self, tmp_path):
        """Test error when JSON is not an array."""
        conversations_file = tmp_path / "conversations.json"
        conversations_file.write_text('{"id": "test"}')
        
        with pytest.raises(importer.InvalidJSONError, match="Expected JSON array"):
            importer.load_conversations_json(conversations_file)


class TestMessageExtraction:
    """Tests for message tree traversal."""
    
    def test_extract_messages_simple(self):
        """Test extracting messages from simple mapping."""
        mapping = {
            "msg-1": {
                "id": "msg-1",
                "message": {
                    "id": "msg-1",
                    "author": {"role": "user"},
                    "content": {"parts": ["Hello"]},
                    "create_time": 1710000000
                },
                "parent": None,
                "children": ["msg-2"]
            },
            "msg-2": {
                "id": "msg-2",
                "message": {
                    "id": "msg-2",
                    "author": {"role": "assistant"},
                    "content": {"parts": ["Hi there!"]},
                    "create_time": 1710000001
                },
                "parent": "msg-1",
                "children": []
            }
        }
        
        messages = importer.extract_messages_from_mapping(mapping, conversation_db_id=1)
        assert len(messages) == 2
        assert messages[0].content == "Hello"
        assert messages[1].content == "Hi there!"
    
    def test_extract_messages_no_message_field(self):
        """Test handling of mapping entries without message field."""
        mapping = {
            "msg-1": {
                "id": "msg-1",
                "parent": None,
                "children": []
            }
        }
        
        messages = importer.extract_messages_from_mapping(mapping, conversation_db_id=1)
        assert len(messages) == 0
    
    def test_extract_messages_multipart(self):
        """Test extracting multi-part message content."""
        mapping = {
            "msg-1": {
                "id": "msg-1",
                "message": {
                    "id": "msg-1",
                    "author": {"role": "user"},
                    "content": {"parts": ["First part", "Second part"]},
                    "create_time": 1710000000
                },
                "parent": None,
                "children": []
            }
        }
        
        messages = importer.extract_messages_from_mapping(mapping, conversation_db_id=1)
        assert len(messages) == 1
        assert messages[0].content == "First part\nSecond part"


class TestConversationImport:
    """Tests for full conversation import."""
    
    def test_import_simple_conversation(self, tmp_path):
        """Test importing a simple conversation."""
        # Setup database
        db_path = tmp_path / "test.db"
        init_db(db_path)
        
        # Create test data
        conversation = {
            "id": "conv-test",
            "title": "Test Conversation",
            "create_time": 1710000000.0,
            "mapping": {
                "msg-1": {
                    "id": "msg-1",
                    "message": {
                        "id": "msg-1",
                        "author": {"role": "user"},
                        "content": {"parts": ["Hello, world!"]},
                        "create_time": 1710000000.0
                    },
                    "parent": None,
                    "children": []
                }
            }
        }
        
        # Import
        conn = sqlite3.connect(db_path)
        conv_db_id, msg_count = importer.insert_conversation(conn, conversation)
        conn.commit()
        
        # Verify
        cursor = conn.cursor()
        cursor.execute("SELECT openai_id, title FROM conversations WHERE openai_id = ?", ("conv-test",))
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == "conv-test"
        assert result[1] == "Test Conversation"
        
        cursor.execute("SELECT COUNT(*) FROM messages WHERE conversation_id = ?", (conv_db_id,))
        count = cursor.fetchone()[0]
        assert count == 1
        
        conn.close()
    
    def test_import_idempotent(self, tmp_path):
        """Test that importing same conversation twice is idempotent."""
        db_path = tmp_path / "test.db"
        init_db(db_path)
        
        conversation = {
            "id": "conv-test",
            "title": "Test",
            "create_time": 1710000000.0,
            "mapping": {
                "msg-1": {
                    "id": "msg-1",
                    "message": {
                        "id": "msg-1",
                        "author": {"role": "user"},
                        "content": {"parts": ["Test"]},
                        "create_time": 1710000000.0
                    },
                    "parent": None,
                    "children": []
                }
            }
        }
        
        # Import twice
        conn = sqlite3.connect(db_path)
        importer.insert_conversation(conn, conversation)
        conn.commit()
        importer.insert_conversation(conn, conversation)
        conn.commit()
        
        # Verify no duplicates
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conv_count = cursor.fetchone()[0]
        assert conv_count == 1
        
        cursor.execute("SELECT COUNT(*) FROM messages")
        msg_count = cursor.fetchone()[0]
        assert msg_count == 1
        
        conn.close()


class TestFullArchiveImport:
    """Tests for full archive import workflow."""
    
    def test_import_archive_simple(self, tmp_path):
        """Test importing a complete archive."""
        # Create archive structure
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        
        conversations_data = [
            {
                "id": "conv-1",
                "title": "First Chat",
                "create_time": 1710000000.0,
                "mapping": {
                    "msg-1": {
                        "id": "msg-1",
                        "message": {
                            "id": "msg-1",
                            "author": {"role": "user"},
                            "content": {"parts": ["Question"]},
                            "create_time": 1710000000.0
                        },
                        "parent": None,
                        "children": []
                    }
                }
            },
            {
                "id": "conv-2",
                "title": "Second Chat",
                "create_time": 1710000100.0,
                "mapping": {
                    "msg-2": {
                        "id": "msg-2",
                        "message": {
                            "id": "msg-2",
                            "author": {"role": "assistant"},
                            "content": {"parts": ["Answer"]},
                            "create_time": 1710000100.0
                        },
                        "parent": None,
                        "children": []
                    }
                }
            }
        ]
        
        conversations_file = archive_dir / "conversations.json"
        conversations_file.write_text(json.dumps(conversations_data))
        
        # Create database
        db_path = tmp_path / "test.db"
        
        # Import
        conv_count, msg_count = importer.import_archive(
            archive_dir,
            db_path
        )
        
        assert conv_count == 2
        assert msg_count == 2
        
        # Verify database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        assert cursor.fetchone()[0] == 2
        
        cursor.execute("SELECT COUNT(*) FROM messages")
        assert cursor.fetchone()[0] == 2
        
        conn.close()
    
    def test_import_archive_with_progress(self, tmp_path):
        """Test import with progress callback."""
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        
        conversations_data = [
            {
                "id": f"conv-{i}",
                "title": f"Chat {i}",
                "create_time": 1710000000.0 + i,
                "mapping": {}
            }
            for i in range(5)
        ]
        
        (archive_dir / "conversations.json").write_text(json.dumps(conversations_data))
        
        db_path = tmp_path / "test.db"
        
        # Track progress
        progress_calls = []
        def progress_callback(current: int, total: int):
            progress_calls.append((current, total))
        
        importer.import_archive(archive_dir, db_path, progress_callback)
        
        # Verify progress was reported
        assert len(progress_calls) > 0
        assert progress_calls[-1] == (5, 5)  # Final call should show 5/5


@pytest.fixture
def tmp_path():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
