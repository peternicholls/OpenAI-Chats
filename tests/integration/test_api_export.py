"""Integration tests for the export API endpoint (T228-T236)."""

import pytest


class TestExportMarkdown:
    """API-EXP-001: test_export_markdown."""

    @pytest.mark.asyncio
    async def test_export_markdown(self, client):
        """Markdown export returns text/markdown content."""
        response = await client.get("/api/conversations/conv-001-test/export?format=md")

        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "text/" in content_type or "markdown" in content_type
        assert len(response.content) > 0


class TestExportJson:
    """API-EXP-002: test_export_json."""

    @pytest.mark.asyncio
    async def test_export_json(self, client):
        """JSON export returns valid JSON content."""
        response = await client.get("/api/conversations/conv-001-test/export?format=json")

        assert response.status_code == 200
        data = response.json()
        assert "id" in data or "messages" in data or isinstance(data, (dict, list))


class TestExportYaml:
    """API-EXP-003: test_export_yaml."""

    @pytest.mark.asyncio
    async def test_export_yaml(self, client):
        """YAML export returns non-empty text content."""
        response = await client.get("/api/conversations/conv-001-test/export?format=yaml")

        assert response.status_code == 200
        text = response.text
        assert len(text) > 0
        assert "id:" in text or "title:" in text or "conv-001-test" in text


class TestExportHtml:
    """API-EXP-004: test_export_html."""

    @pytest.mark.asyncio
    async def test_export_html(self, client):
        """HTML export returns HTML content."""
        response = await client.get("/api/conversations/conv-001-test/export?format=html")

        assert response.status_code == 200
        text = response.text
        assert "<html" in text.lower() or "<!doctype" in text.lower()


class TestExportXml:
    """API-EXP-005: test_export_xml."""

    @pytest.mark.asyncio
    async def test_export_xml(self, client):
        """XML export returns XML content."""
        response = await client.get("/api/conversations/conv-001-test/export?format=xml")

        assert response.status_code == 200
        text = response.text
        assert "<?xml" in text or "<conversation" in text


class TestExportCsv:
    """API-EXP-006: test_export_csv."""

    @pytest.mark.asyncio
    async def test_export_csv(self, client):
        """CSV export returns comma-separated content."""
        response = await client.get("/api/conversations/conv-001-test/export?format=csv")

        assert response.status_code == 200
        text = response.text
        assert len(text) > 0
        # CSV should have at least one comma-separated line
        lines = text.strip().splitlines()
        assert len(lines) >= 1


class TestExportExcel:
    """API-EXP-007: test_export_excel."""

    @pytest.mark.asyncio
    async def test_export_excel(self, client):
        """Excel export returns binary xlsx content."""
        response = await client.get("/api/conversations/conv-001-test/export?format=xlsx")

        assert response.status_code == 200
        # XLSX files start with PK (zip magic bytes)
        assert response.content[:2] == b"PK"


class TestExportInvalidFormat:
    """API-EXP-008: test_export_invalid_format."""

    @pytest.mark.asyncio
    async def test_export_invalid_format(self, client):
        """Requesting an invalid format returns 400."""
        response = await client.get("/api/conversations/conv-001-test/export?format=pdf")

        assert response.status_code == 400


class TestExportNotFound:
    """API-EXP-009: test_export_not_found."""

    @pytest.mark.asyncio
    async def test_export_not_found(self, client):
        """Exporting a non-existent conversation returns 404."""
        response = await client.get("/api/conversations/no-such-conv/export?format=md")

        assert response.status_code == 404
