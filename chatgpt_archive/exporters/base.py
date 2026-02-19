"""Base exporter abstract class for conversation export."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List


class BaseExporter(ABC):
    """Abstract base class for conversation exporters.
    
    All export format implementations must inherit from this class
    and implement the export() method.
    
    Attributes:
        format_name: Human-readable format name
        file_extension: Default file extension for this format
    """
    
    format_name: str = "base"
    file_extension: str = ".txt"
    
    @abstractmethod
    def export(self, conversation: dict, messages: List[dict]) -> str:
        """Export a conversation to the target format.
        
        Args:
            conversation: Dictionary with conversation metadata:
                - id: OpenAI conversation ID
                - title: Conversation title
                - create_time: Unix timestamp
                - update_time: Unix timestamp  
                - model: Model slug
                - message_count: Number of messages
            messages: List of message dictionaries:
                - id: OpenAI message ID
                - role: Author role (user, assistant, system, tool)
                - content: Message text content
                - create_time: Unix timestamp
                
        Returns:
            Formatted string representation of the conversation
        """
        pass
    
    @staticmethod
    def format_timestamp(ts: float | None, include_time: bool = True) -> str:
        """Format a unix timestamp for display.
        
        Args:
            ts: Unix timestamp or None
            include_time: Whether to include time component
            
        Returns:
            Formatted datetime string or empty string
        """
        if ts is None:
            return ""
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        if include_time:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d")
    
    @staticmethod
    def format_date(ts: float | None) -> str:
        """Format a unix timestamp as date only.
        
        Args:
            ts: Unix timestamp or None
            
        Returns:
            Formatted date string (YYYY-MM-DD) or empty string
        """
        return BaseExporter.format_timestamp(ts, include_time=False)
    
    @staticmethod
    def format_time(ts: float | None) -> str:
        """Format a unix timestamp as time only.
        
        Args:
            ts: Unix timestamp or None
            
        Returns:
            Formatted time string (HH:MM:SS) or empty string
        """
        if ts is None:
            return ""
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.strftime("%H:%M:%S")
    
    @staticmethod
    def format_iso8601(ts: float | None) -> str | None:
        """Format a unix timestamp as ISO 8601.
        
        Args:
            ts: Unix timestamp or None
            
        Returns:
            ISO 8601 formatted string or None
        """
        if ts is None:
            return None
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.isoformat()
    
    @staticmethod
    def get_display_title(conversation: dict) -> str:
        """Get conversation title with fallback.
        
        Args:
            conversation: Conversation dictionary
            
        Returns:
            Title or "[Untitled]" if not set
        """
        return conversation.get("title") or "[Untitled]"
