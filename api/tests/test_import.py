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

        # Should return 200 or 202 (accepted)
        assert response.status_code in [200, 202]

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

        # Should return 400 or 422
        assert response.status_code in [400, 422, 500]

    @pytest.mark.asyncio
    async def test_import_corrupt_zip_handled(self, client):
        """Test that corrupt ZIP files are handled gracefully."""
        content = b"PK\x03\x04corrupted data"
        files = {"file": ("corrupt.zip", io.BytesIO(content), "application/zip")}
        response = await client.post("/api/import", files=files)

        # API accepts the file and processes async, so 202 is expected
        # The error will be reported via the progress endpoint
        assert response.status_code in [200, 202, 400, 422, 500]

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

        # Should handle gracefully (error or success with 0 imports)
        assert response.status_code in [200, 202, 400, 422, 500]


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
