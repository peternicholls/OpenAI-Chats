"""Unit tests for data models."""

import pytest
from chatgpt_archive.models import Message, Conversation, Attachment


class TestMessage:
    """Tests for Message dataclass."""
    
    def test_valid_message_user(self):
        """Test creating a valid user message."""
        msg = Message(
            openai_id="msg-123",
            author_role="user",
            content="Hello, world!",
            conversation_id=1,
            create_time=1710000000
        )
        assert msg.openai_id == "msg-123"
        assert msg.author_role == "user"
        assert msg.content == "Hello, world!"
    
    def test_valid_message_assistant(self):
        """Test creating a valid assistant message."""
        msg = Message(
            openai_id="msg-123",
            author_role="assistant",
            content="Hello!",
            create_time=1710000000
        )
        assert msg.author_role == "assistant"
    
    def test_valid_message_system(self):
        """Test creating a valid system message."""
        msg = Message(
            openai_id="msg-123",
            author_role="system",
            content="System message",
            create_time=1710000000
        )
        assert msg.author_role == "system"
    
    def test_valid_message_tool(self):
        """Test creating a valid tool message."""
        msg = Message(
            openai_id="msg-123",
            author_role="tool",
            content="Tool output",
            create_time=1710000000
        )
        assert msg.author_role == "tool"
    
    def test_invalid_author_role(self):
        """Test that invalid author_role raises ValueError."""
        with pytest.raises(ValueError, match="author_role must be one of"):
            Message(
                openai_id="msg-123",
                author_role="invalid",
                content="Test",
                create_time=1710000000
            )
    
    def test_optional_fields(self):
        """Test message with optional fields."""
        msg = Message(
            openai_id="msg-123",
            author_role="user",
            content="Test",
            create_time=1710000000,
            parent_id="msg-parent",
            content_type="text",
            weight=0.8
        )
        assert msg.parent_id == "msg-parent"
        assert msg.content_type == "text"
        assert msg.weight == 0.8


class TestConversation:
    """Tests for Conversation dataclass."""
    
    def test_conversation_with_title(self):
        """Test conversation with explicit title."""
        conv = Conversation(
            openai_id="conv-123",
            title="My Conversation",
            create_time=1710000000
        )
        assert conv.openai_id == "conv-123"
        assert conv.title == "My Conversation"
        assert conv.display_title == "My Conversation"
    
    def test_conversation_without_title(self):
        """Test conversation without title falls back to [Untitled]."""
        conv = Conversation(
            openai_id="conv-123",
            title=None,
            create_time=1710000000
        )
        assert conv.title is None
        assert conv.display_title == "[Untitled]"
    
    def test_conversation_with_user_message_fallback(self):
        """Test conversation fallback to first user message."""
        conv = Conversation(
            openai_id="conv-123",
            title=None,
            create_time=1710000000
        )
        # Add a user message
        msg = Message(
            openai_id="msg-1",
            author_role="user",
            content="This is a test message that is longer than 50 characters for testing truncation",
            create_time=1710000000
        )
        conv.messages.append(msg)
        
        # Should use truncated message content as title
        assert "This is a test message" in conv.display_title
        assert conv.display_title.endswith("...")
    
    def test_conversation_optional_fields(self):
        """Test conversation with all optional fields."""
        conv = Conversation(
            openai_id="conv-123",
            title="Test",
            create_time=1710000000,
            update_time=1710000100,
            model_slug="gpt-4",
            is_archived=True
        )
        assert conv.update_time == 1710000100
        assert conv.model_slug == "gpt-4"
        assert conv.is_archived is True


class TestAttachment:
    """Tests for Attachment dataclass."""
    
    def test_attachment_creation(self):
        """Test creating an attachment."""
        att = Attachment(
            file_path="6a46cf21/image/image.png",
            file_type="image/png",
            original_name="image.png"
        )
        assert att.file_path == "6a46cf21/image/image.png"
        assert att.file_type == "image/png"
        assert att.original_name == "image.png"
    
    def test_attachment_optional_fields(self):
        """Test attachment with minimal fields."""
        att = Attachment(
            file_path="doc.pdf"
        )
        assert att.file_path == "doc.pdf"
        assert att.file_type is None
        assert att.original_name is None
        assert att.id is None
        assert att.message_id is None
