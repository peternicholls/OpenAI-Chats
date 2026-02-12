"""JSON exporter for conversation export."""

import json
from typing import List

from .base import BaseExporter


class JSONExporter(BaseExporter):
    """Export conversations to JSON format.
    
    Produces a structured JSON document with:
    - Conversation metadata
    - Array of messages with full details
    - ISO 8601 formatted timestamps
    """
    
    format_name = "json"
    file_extension = ".json"
    
    def export(self, conversation: dict, messages: List[dict]) -> str:
        """Export conversation to JSON format.
        
        Args:
            conversation: Conversation metadata dictionary
            messages: List of message dictionaries
            
        Returns:
            JSON formatted string (pretty-printed)
        """
        output = {
            "id": conversation.get("id"),
            "title": conversation.get("title"),
            "created_at": self.format_iso8601(conversation.get("create_time")),
            "updated_at": self.format_iso8601(conversation.get("update_time")),
            "model": conversation.get("model"),
            "message_count": conversation.get("message_count", len(messages)),
            "messages": [
                {
                    "id": msg.get("id"),
                    "role": msg.get("role"),
                    "content": msg.get("content"),
                    "created_at": self.format_iso8601(msg.get("create_time")),
                }
                for msg in messages
            ]
        }
        
        return json.dumps(output, indent=2, ensure_ascii=False)
