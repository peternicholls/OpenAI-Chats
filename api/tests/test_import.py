"""Tests for the import endpoint."""

import io

import pytest


class TestImport:
    """Tests for POST /api/import endpoint."""

    @pytest.mark.asyncio
    async def test_import_accepts_zip_file(self, client, sample_archive_zip):
        """Test that import endpoint accepts ZIP files."""
        with open(sample_archive_zip, "rb") as f:
            files = {"file": ("archive.zip", f, "application/zip")}
            response = await client.post("/api/import", files=files)

        assert response.status_code == 202

    @pytest.mark.asyncio
    async def test_import_returns_progress_info(self, client, sample_archive_zip):
        """Test that import returns progress information."""
        with open(sample_archive_zip, "rb") as f:
            files = {"file": ("archive.zip", f, "application/zip")}
            response = await client.post("/api/import", files=files)

        data = response.json()
        # Should have status field
        assert "status" in data or "message" in data

    @pytest.mark.asyncio
    async def test_import_invalid_file_type_rejected(self, client):
        """Test that non-ZIP files are rejected."""
        content = b"This is not a zip file"
        files = {"file": ("notzip.txt", io.BytesIO(content), "text/plain")}
        response = await client.post("/api/import", files=files)

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_import_corrupt_zip_handled(self, client):
        """Corrupt ZIP files are rejected early."""
        content = b"PK\x03\x04corrupted data"
        files = {"file": ("corrupt.zip", io.BytesIO(content), "application/zip")}
        response = await client.post("/api/import", files=files)

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_import_empty_zip_handled(self, client, tmp_path):
        """Test that empty ZIP files are handled."""
        import zipfile

        empty_zip = tmp_path / "empty.zip"
        with zipfile.ZipFile(empty_zip, "w") as zf:
            pass  # Create empty zip

        with open(empty_zip, "rb") as f:
            files = {"file": ("empty.zip", f, "application/zip")}
            response = await client.post("/api/import", files=files)

        # Valid ZIP upload should be queued; processing may still error later.
        assert response.status_code == 202

    @pytest.mark.asyncio
    async def test_import_oversize_upload_rejected(self, client, monkeypatch):
        """Uploads exceeding MAX_FILE_SIZE_BYTES return 413."""
        monkeypatch.setattr("api.routers.import_.MAX_FILE_SIZE_BYTES", 10)

        files = {"file": ("archive.zip", io.BytesIO(b"01234567890"), "application/zip")}
        response = await client.post("/api/import", files=files)

        assert response.status_code == 413


class TestImportProgress:
    """Tests for GET /api/import/progress endpoint."""

    @pytest.mark.asyncio
    async def test_get_progress_returns_200(self, client):
        """Test that progress endpoint returns 200."""
        response = await client.get("/api/import/progress")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_progress_structure(self, client):
        """Test progress response structure."""
        response = await client.get("/api/import/progress")

        data = response.json()
        assert "status" in data
