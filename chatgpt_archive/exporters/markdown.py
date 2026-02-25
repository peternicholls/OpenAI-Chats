"""Markdown exporter for conversation export."""

from typing import List

from .base import BaseExporter


class MarkdownExporter(BaseExporter):
    """Export conversations to Markdown format.

    Produces a clean, human-readable Markdown document with:
    - Title as H1 header
    - Metadata line with date, model, message count
    - Horizontal rules between messages
    - Role labels in bold with timestamps
    """

    format_name = "markdown"
    file_extension = ".md"

    def export(self, conversation: dict, messages: List[dict]) -> str:
        """Export conversation to Markdown format.

        Args:
            conversation: Conversation metadata dictionary
            messages: List of message dictionaries

        Returns:
            Markdown formatted string
        """
        lines = []

        # Header
        title = self.get_display_title(conversation)
        lines.append(f"# {title}")
        lines.append("")

        # Metadata
        created = self.format_timestamp(conversation.get("create_time"))
        model = conversation.get("model") or "unknown"
        msg_count = conversation.get("message_count", len(messages))

        lines.append(f"**Created**: {created}  ")
        lines.append(f"**Model**: {model}  ")
        lines.append(f"**Messages**: {msg_count}")
        lines.append("")

        # Conversation ID
        conv_id = conversation.get("id", "")
        if conv_id:
            lines.append(f"**ID**: `{conv_id}`")
            lines.append("")

        lines.append("---")
        lines.append("")

        # Messages
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content") or ""
            time_str = self.format_time(msg.get("create_time"))

            # Skip empty system messages
            if not content.strip() and role == "system":
                continue

            # Role header
            role_label = role.capitalize()
            if time_str:
                lines.append(f"### {role_label} ({time_str})")
            else:
                lines.append(f"### {role_label}")
            lines.append("")

            # Content
            lines.append(content)
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)
