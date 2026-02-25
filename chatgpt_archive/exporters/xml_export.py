"""XML exporter for conversation export."""

from typing import List
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

from .base import BaseExporter


class XMLExporter(BaseExporter):
    """Export conversations to XML format.

    Produces a well-formed XML document with:
    - Conversation metadata as attributes/elements
    - Messages as nested elements
    - ISO 8601 formatted timestamps
    - Proper XML escaping
    """

    format_name = "xml"
    file_extension = ".xml"

    def export(self, conversation: dict, messages: List[dict]) -> str:
        """Export conversation to XML format.

        Args:
            conversation: Conversation metadata dictionary
            messages: List of message dictionaries

        Returns:
            XML formatted string (pretty-printed)
        """
        # Root element
        root = Element("conversation")
        root.set("xmlns", "http://chatgpt-archive.local/schema/v1")

        # Conversation metadata
        conv_id = conversation.get("id") or ""
        if conv_id:
            root.set("id", conv_id)

        # Title
        title_elem = SubElement(root, "title")
        title_elem.text = self.get_display_title(conversation)

        # Metadata
        metadata = SubElement(root, "metadata")

        created_at = SubElement(metadata, "created_at")
        created_at.text = self.format_iso8601(conversation.get("create_time")) or ""

        updated_at = SubElement(metadata, "updated_at")
        updated_at.text = self.format_iso8601(conversation.get("update_time")) or ""

        model = SubElement(metadata, "model")
        model.text = conversation.get("model") or ""

        msg_count = SubElement(metadata, "message_count")
        msg_count.text = str(conversation.get("message_count", len(messages)))

        # Messages
        messages_elem = SubElement(root, "messages")

        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content") or ""

            # Skip empty system messages
            if not content.strip() and role == "system":
                continue

            msg_elem = SubElement(messages_elem, "message")

            msg_id = msg.get("id") or ""
            if msg_id:
                msg_elem.set("id", msg_id)

            msg_elem.set("role", role)

            timestamp = self.format_iso8601(msg.get("create_time"))
            if timestamp:
                msg_elem.set("created_at", timestamp)

            # Content as CDATA-like text
            content_elem = SubElement(msg_elem, "content")
            content_elem.text = content

        # Pretty print
        rough_string = tostring(root, encoding="unicode")
        dom = parseString(rough_string)

        # Get pretty-printed XML with declaration
        pretty_xml = dom.toprettyxml(indent="  ", encoding=None)

        # Clean up extra blank lines that minidom adds
        lines = pretty_xml.split("\n")
        non_empty_lines = [line for line in lines if line.strip()]

        return "\n".join(non_empty_lines)
