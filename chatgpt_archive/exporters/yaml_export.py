"""YAML exporter for conversation export."""

from typing import List

import yaml  # type: ignore[import-untyped]

from .base import BaseExporter


class YAMLExporter(BaseExporter):
    """Export conversations to YAML format.

    Produces a clean YAML document with:
    - Conversation metadata
    - Array of messages with full details
    - ISO 8601 formatted timestamps
    - Human-readable multi-line content blocks
    """

    format_name = "yaml"
    file_extension = ".yaml"

    def export(self, conversation: dict, messages: List[dict]) -> str:
        """Export conversation to YAML format.

        Args:
            conversation: Conversation metadata dictionary
            messages: List of message dictionaries

        Returns:
            YAML formatted string
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
            ],
        }

        # Use default_flow_style=False for readable multi-line output
        # allow_unicode=True for proper character handling
        return yaml.dump(
            output,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )
