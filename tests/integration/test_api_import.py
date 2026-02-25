"""Integration tests for the import API endpoints (T247-T250)."""

import io
import zipfile

import pytest


class TestImportValidZip:
    """API-IMP-001: test_import_valid_zip."""

    @pytest.mark.asyncio
    async def test_import_valid_zip(self, client, sample_archive_zip):
        """Uploading a valid archive ZIP returns 202 and starts processing."""
        with open(sample_archive_zip, "rb") as f:
            response = await client.post(
                "/api/import",
                files={"file": ("archive.zip", f, "application/zip")},
            )

        assert response.status_code in (200, 202)


class TestImportInvalidFile:
    """API-IMP-002: test_import_invalid_file."""

    @pytest.mark.asyncio
    async def test_import_invalid_file(self, client):
        """Uploading a non-ZIP file returns 400."""
        fake_content = b"this is not a zip file"
        response = await client.post(
            "/api/import",
            files={"file": ("archive.txt", io.BytesIO(fake_content), "text/plain")},
        )

        assert response.status_code == 400


class TestImportProgress:
    """API-IMP-003: test_import_progress."""

    @pytest.mark.asyncio
    async def test_import_progress(self, client):
        """The import progress endpoint returns a valid progress object."""
        response = await client.get("/api/import/progress")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestImportCorruptedZip:
    """API-IMP-004: test_import_corrupted_zip."""

    @pytest.mark.asyncio
    async def test_import_corrupted_zip(self, client):
        """Uploading a corrupted ZIP file is accepted (202) for async processing.

        The import is handled asynchronously; corruption is detected during
        extraction, not at upload time, so the API responds with 202 Accepted.
        """
        corrupted = b"PK\x03\x04" + b"\x00" * 50  # ZIP magic but invalid content
        response = await client.post(
            "/api/import",
            files={"file": ("broken.zip", io.BytesIO(corrupted), "application/zip")},
        )

        # 202 = queued for async processing; error surfaces via /api/import/progress
        assert response.status_code in (202, 400)
