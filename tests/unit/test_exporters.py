"""Unit tests for conversation exporters (EXP-001 through EXP-014).

Tests each supported export format for structure, content, and edge cases.
"""

import json

import pytest

from chatgpt_archive.exporters import (
    CSVExporter,
    HTMLExporter,
    JSONExporter,
    MarkdownExporter,
    XMLExporter,
    YAMLExporter,
    get_exporter,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

SAMPLE_CONVERSATION = {
    "id": "test-conv-001",
    "title": "Test Conversation",
    "create_time": 1700000000.0,
    "update_time": 1700001000.0,
    "model": "gpt-4",
    "message_count": 2,
}

SAMPLE_MESSAGES = [
    {
        "id": "msg-001",
        "role": "user",
        "content": "Hello, how are you?",
        "create_time": 1700000000.0,
    },
    {
        "id": "msg-002",
        "role": "assistant",
        "content": "I'm doing well, thank you for asking!",
        "create_time": 1700000100.0,
    },
]

MULTIPART_MESSAGES = [
    {
        "id": "msg-code",
        "role": "user",
        "content": "Here is some code:\n```python\nprint('hello')\n```",
        "create_time": 1700000000.0,
    },
    {
        "id": "msg-response",
        "role": "assistant",
        "content": "Your code prints 'hello' to stdout.",
        "create_time": 1700000100.0,
    },
]

SPECIAL_CHARS_MESSAGES = [
    {
        "id": "msg-special",
        "role": "user",
        "content": 'Text with "quotes", <tags>, & ampersands, and émojis 🎉',
        "create_time": 1700000000.0,
    },
    {
        "id": "msg-resp",
        "role": "assistant",
        "content": "Received your message with special characters.",
        "create_time": 1700000100.0,
    },
]


# ---------------------------------------------------------------------------
# EXP-001: Markdown export — single conversation
# ---------------------------------------------------------------------------


class TestMarkdownExport:
    """Tests for Markdown exporter (EXP-001, EXP-002)."""

    def test_markdown_export_single_conversation(self):
        """EXP-001: Export a single conversation as Markdown."""
        exporter = MarkdownExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SAMPLE_MESSAGES)

        assert isinstance(result, str)
        assert "Test Conversation" in result
        assert "# Test Conversation" in result

    def test_markdown_export_contains_messages(self):
        """EXP-001: Markdown output includes message content."""
        exporter = MarkdownExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SAMPLE_MESSAGES)

        assert "Hello, how are you?" in result
        assert "I'm doing well" in result

    def test_markdown_export_has_role_labels(self):
        """EXP-001: Markdown export labels user and assistant messages."""
        exporter = MarkdownExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SAMPLE_MESSAGES)

        # Roles should appear in some form
        assert "user" in result.lower() or "**user**" in result.lower()

    def test_markdown_export_multipart_content(self):
        """EXP-002: Markdown handles code blocks and multipart content."""
        exporter = MarkdownExporter()
        result = exporter.export(SAMPLE_CONVERSATION, MULTIPART_MESSAGES)

        assert "```python" in result or "print" in result
        assert "Your code prints" in result

    def test_markdown_export_metadata(self):
        """EXP-001: Markdown output contains conversation metadata."""
        exporter = MarkdownExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SAMPLE_MESSAGES)

        # Should include creation date or model info
        assert "gpt-4" in result or "2023" in result


# ---------------------------------------------------------------------------
# EXP-003 & EXP-004: JSON export
# ---------------------------------------------------------------------------


class TestJSONExport:
    """Tests for JSON exporter (EXP-003, EXP-004)."""

    def test_json_export_structure(self):
        """EXP-003: JSON export has the expected structure."""
        exporter = JSONExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SAMPLE_MESSAGES)

        data = json.loads(result)
        assert "id" in data
        assert "title" in data
        assert "messages" in data
        assert isinstance(data["messages"], list)
        assert len(data["messages"]) == 2

    def test_json_export_message_fields(self):
        """EXP-003: Each message has required fields."""
        exporter = JSONExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SAMPLE_MESSAGES)

        data = json.loads(result)
        for msg in data["messages"]:
            assert "role" in msg
            assert "content" in msg

    def test_json_export_special_chars(self):
        """EXP-004: JSON handles special characters correctly."""
        exporter = JSONExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SPECIAL_CHARS_MESSAGES)

        data = json.loads(result)
        assert len(data["messages"]) == 2
        # Content with special chars should survive round-trip
        content = data["messages"][0]["content"]
        assert "quotes" in content or '"' in content

    def test_json_export_is_valid_json(self):
        """EXP-003: JSON export always produces valid JSON."""
        exporter = JSONExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SAMPLE_MESSAGES)

        # Should not raise
        parsed = json.loads(result)
        assert parsed is not None


# ---------------------------------------------------------------------------
# EXP-005: YAML export
# ---------------------------------------------------------------------------


class TestYAMLExport:
    """Tests for YAML exporter (EXP-005)."""

    def test_yaml_export_structure(self):
        """EXP-005: YAML export has valid structure."""
        import yaml

        exporter = YAMLExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SAMPLE_MESSAGES)

        data = yaml.safe_load(result)
        assert "id" in data or "title" in data
        assert isinstance(result, str)

    def test_yaml_export_contains_content(self):
        """EXP-005: YAML output contains message content."""
        exporter = YAMLExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SAMPLE_MESSAGES)

        assert "Hello, how are you?" in result
        assert "I'm doing well" in result


# ---------------------------------------------------------------------------
# EXP-006 & EXP-007: HTML export
# ---------------------------------------------------------------------------


class TestHTMLExport:
    """Tests for HTML exporter (EXP-006, EXP-007)."""

    def test_html_export_structure(self):
        """EXP-006: HTML export has valid HTML structure."""
        exporter = HTMLExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SAMPLE_MESSAGES)

        assert "<html" in result or "<!DOCTYPE" in result
        assert "</html>" in result
        assert "<body" in result

    def test_html_export_contains_title(self):
        """EXP-006: HTML output contains conversation title."""
        exporter = HTMLExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SAMPLE_MESSAGES)

        assert "Test Conversation" in result

    def test_html_export_contains_messages(self):
        """EXP-006: HTML output contains message content."""
        exporter = HTMLExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SAMPLE_MESSAGES)

        assert "Hello, how are you?" in result
        # Apostrophes may be HTML-escaped as &#x27; or &#39;
        assert "I&#x27;m doing well" in result or "I&#39;m doing well" in result or "I'm doing well" in result

    def test_html_export_xss_prevention(self):
        """EXP-007: HTML export escapes dangerous content to prevent XSS."""
        xss_messages = [
            {
                "id": "msg-xss",
                "role": "user",
                "content": "<script>alert('xss')</script>",
                "create_time": 1700000000.0,
            }
        ]

        exporter = HTMLExporter()
        result = exporter.export(SAMPLE_CONVERSATION, xss_messages)

        # Raw <script> tag must not appear; it should be escaped
        assert "<script>alert" not in result
        assert "&lt;script&gt;" in result or "alert" not in result


# ---------------------------------------------------------------------------
# EXP-008 & EXP-009: XML export
# ---------------------------------------------------------------------------


class TestXMLExport:
    """Tests for XML exporter (EXP-008, EXP-009)."""

    def test_xml_export_structure(self):
        """EXP-008: XML export produces well-formed XML."""
        import xml.etree.ElementTree as ET

        exporter = XMLExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SAMPLE_MESSAGES)

        # Should parse without error
        root = ET.fromstring(result)
        assert root is not None

    def test_xml_export_special_chars(self):
        """EXP-009: XML handles special characters correctly."""
        import xml.etree.ElementTree as ET

        exporter = XMLExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SPECIAL_CHARS_MESSAGES)

        # Can still parse (escaped properly)
        root = ET.fromstring(result)
        assert root is not None


# ---------------------------------------------------------------------------
# EXP-010 & EXP-011: CSV export
# ---------------------------------------------------------------------------


class TestCSVExport:
    """Tests for CSV exporter (EXP-010, EXP-011)."""

    def test_csv_export_structure(self):
        """EXP-010: CSV export has valid CSV structure with message data."""
        exporter = CSVExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SAMPLE_MESSAGES)

        assert isinstance(result, str)
        # Result should contain message content
        assert "Hello, how are you?" in result
        assert "I\'m doing well" in result or "I'm doing well" in result
        # Should have role indicators
        assert "user" in result
        assert "assistant" in result

    def test_csv_export_commas_in_content(self):
        """EXP-011: CSV properly handles content containing commas."""
        comma_messages = [
            {
                "id": "msg-comma",
                "role": "user",
                "content": "Hello, world, this has commas",
                "create_time": 1700000000.0,
            }
        ]

        exporter = CSVExporter()
        result = exporter.export(SAMPLE_CONVERSATION, comma_messages)

        # Content should survive in the CSV output
        assert "Hello" in result
        assert "commas" in result


# ---------------------------------------------------------------------------
# EXP-012 & EXP-013: Excel export
# ---------------------------------------------------------------------------


class TestExcelExport:
    """Tests for Excel exporter (EXP-012, EXP-013)."""

    @pytest.mark.skipif(
        not __import__("importlib").util.find_spec("openpyxl"),
        reason="openpyxl not installed",
    )
    def test_excel_export_structure(self):
        """EXP-012: Excel export produces valid XLSX file."""
        import io

        import openpyxl
        from chatgpt_archive.exporters.excel_export import ExcelExporter

        exporter = ExcelExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SAMPLE_MESSAGES)

        # Excel exporter returns bytes
        assert isinstance(result, (bytes, str))
        if isinstance(result, bytes):
            wb = openpyxl.load_workbook(io.BytesIO(result))
            assert len(wb.sheetnames) >= 1

    @pytest.mark.skipif(
        not __import__("importlib").util.find_spec("openpyxl"),
        reason="openpyxl not installed",
    )
    def test_excel_export_binary(self):
        """EXP-013: Excel export returns binary data."""
        from chatgpt_archive.exporters.excel_export import ExcelExporter

        exporter = ExcelExporter()
        result = exporter.export(SAMPLE_CONVERSATION, SAMPLE_MESSAGES)

        assert result is not None
        assert len(result) > 0


# ---------------------------------------------------------------------------
# EXP-014: Empty conversation
# ---------------------------------------------------------------------------


class TestEmptyConversationExport:
    """Tests for exporting empty conversations (EXP-014)."""

    def test_markdown_export_empty_conversation(self):
        """EXP-014: Markdown handles conversations with no messages."""
        exporter = MarkdownExporter()
        result = exporter.export(SAMPLE_CONVERSATION, [])

        assert isinstance(result, str)
        assert len(result) > 0  # Should still produce output

    def test_json_export_empty_conversation(self):
        """EXP-014: JSON handles empty conversation."""
        exporter = JSONExporter()
        result = exporter.export(SAMPLE_CONVERSATION, [])

        data = json.loads(result)
        assert data["messages"] == []

    def test_csv_export_empty_conversation(self):
        """EXP-014: CSV handles empty conversation."""
        exporter = CSVExporter()
        result = exporter.export(SAMPLE_CONVERSATION, [])

        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Exporter registry
# ---------------------------------------------------------------------------


class TestExporterRegistry:
    """Tests for the exporter factory/registry."""

    def test_get_exporter_returns_markdown(self):
        """Factory returns MarkdownExporter for 'md'."""
        exporter = get_exporter("md")
        assert isinstance(exporter, MarkdownExporter)

    def test_get_exporter_returns_json(self):
        """Factory returns JSONExporter for 'json'."""
        exporter = get_exporter("json")
        assert isinstance(exporter, JSONExporter)

    def test_get_exporter_unknown_format(self):
        """Factory returns None for unknown formats."""
        exporter = get_exporter("unknown_format")
        assert exporter is None
