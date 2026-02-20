"""CSV exporter for conversation export."""

import csv
import io
from typing import List

from .base import BaseExporter


class CSVExporter(BaseExporter):
    """Export conversations to CSV format.
    
    Produces a CSV file with columns:
    - message_id: OpenAI message ID
    - role: Author role (user, assistant, system, tool)
    - content: Message text content
    - timestamp: ISO 8601 formatted timestamp
    
    Conversation metadata is included as a header comment block.
    """
    
    format_name = "csv"
    file_extension = ".csv"
    
    def export(self, conversation: dict, messages: List[dict]) -> str:
        """Export conversation to CSV format.
        
        Args:
            conversation: Conversation metadata dictionary
            messages: List of message dictionaries
            
        Returns:
            CSV formatted string with header row and message data
        """
        output = io.StringIO()
        
        # Write metadata as comment lines
        title = self.sanitize_spreadsheet_cell(self.get_display_title(conversation))
        created = self.format_timestamp(conversation.get("create_time"))
        model = self.sanitize_spreadsheet_cell(conversation.get("model") or "unknown")
        conv_id = self.sanitize_spreadsheet_cell(conversation.get("id", ""))
        
        output.write(f"# Conversation: {title}\n")
        output.write(f"# ID: {conv_id}\n")
        output.write(f"# Created: {created}\n")
        output.write(f"# Model: {model}\n")
        output.write(f"# Messages: {conversation.get('message_count', len(messages))}\n")
        
        # Write CSV data
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["message_id", "role", "content", "timestamp"])
        
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content") or ""
            
            # Skip empty system messages
            if not content.strip() and role == "system":
                continue
            
            timestamp = self.format_iso8601(msg.get("create_time")) or ""
            msg_id = msg.get("id", "")

            writer.writerow(
                [
                    self.sanitize_spreadsheet_cell(msg_id),
                    self.sanitize_spreadsheet_cell(role),
                    self.sanitize_spreadsheet_cell(content),
                    self.sanitize_spreadsheet_cell(timestamp),
                ]
            )
        
        return output.getvalue()
