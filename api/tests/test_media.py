"""Tests for media parsing and media-serving endpoints."""

from pathlib import Path

import pytest

from api.services import media_service
from api.tests.conftest import (
    MEDIA_AUDIO_FILE_ID,
    MEDIA_CONVERSATION_ID,
    MEDIA_IMAGE_FILE_ID,
    MEDIA_ROOT_FILE_ID,
)


class TestMediaEndpoints:
    @pytest.mark.asyncio
    async def test_get_conversation_image(self, media_client):
        response = await media_client.get(
            f"/api/media/{MEDIA_CONVERSATION_ID}/{MEDIA_IMAGE_FILE_ID}"
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/jpeg")
        assert response.headers["cache-control"] == "public, max-age=86400, immutable"

    @pytest.mark.asyncio
    async def test_get_conversation_audio(self, media_client):
        response = await media_client.get(
            f"/api/media/{MEDIA_CONVERSATION_ID}/{MEDIA_AUDIO_FILE_ID}"
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("audio/x-wav")

    @pytest.mark.asyncio
    async def test_get_root_file(self, media_client):
        response = await media_client.get(f"/api/media/root/{MEDIA_ROOT_FILE_ID}")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/pdf")
        assert "attachment; filename=\"Sample Document.pdf\"" in response.headers[
            "content-disposition"
        ]

    @pytest.mark.asyncio
    async def test_media_endpoint_rejects_invalid_ids(self, media_client):
        response = await media_client.get("/api/media/not-a-uuid/file_abc")
        assert response.status_code == 400

        root_response = await media_client.get("/api/media/root/file-invalid!")
        assert root_response.status_code == 400

    @pytest.mark.asyncio
    async def test_media_endpoint_returns_404_for_missing_file(self, media_client):
        response = await media_client.get(
            f"/api/media/{MEDIA_CONVERSATION_ID}/file_00000000deadbeefdeadbeefdeadbeef"
        )

        assert response.status_code == 404


class TestConversationAttachments:
    @pytest.mark.asyncio
    async def test_conversation_response_contains_ordered_attachments(self, media_client):
        response = await media_client.get(f"/api/conversations/{MEDIA_CONVERSATION_ID}")

        assert response.status_code == 200
        message = response.json()["messages"][0]
        assert message["content"] == "Lead text\n[[ATTACHMENT:0]]\nMiddle text\n[[ATTACHMENT:1]]\n[[ATTACHMENT:2]]"
        assert [attachment["type"] for attachment in message["attachments"]] == [
            "image",
            "file",
            "audio",
        ]
        assert message["attachments"][0]["found"] is True
        assert message["attachments"][1]["filename"] == "Sample Document.pdf"

    @pytest.mark.asyncio
    async def test_conversation_response_marks_missing_attachments(self, media_client):
        response = await media_client.get(f"/api/conversations/{MEDIA_CONVERSATION_ID}")

        assert response.status_code == 200
        missing_message = response.json()["messages"][1]
        assert missing_message["attachments"][0]["found"] is False
        assert missing_message["content"] == "[[ATTACHMENT:0]]"


class TestAttachmentParsingPerformance:
    def test_text_only_messages_skip_attachment_work(self):
        content = "plain text only"

        cleaned, attachments = media_service.resolve_message_content(
            content, MEDIA_CONVERSATION_ID
        )

        assert cleaned == content
        assert attachments == []

    def test_many_attachments_preserve_order(self, monkeypatch):
        fake_path = Path("/tmp/fake-image.png")

        monkeypatch.setattr(
            media_service,
            "resolve_conversation_media_path",
            lambda conversation_id, file_id: fake_path,
        )
        monkeypatch.setattr(
            media_service,
            "get_media_metadata",
            lambda path: ("image/png", "fake-image.png"),
        )

        content = "\n".join(
            str(
                {
                    "content_type": "image_asset_pointer",
                    "asset_pointer": f"sediment://file_{index:032x}",
                    "size_bytes": 100 + index,
                }
            )
            for index in range(12)
        )

        cleaned, attachments = media_service.resolve_message_content(
            content, MEDIA_CONVERSATION_ID
        )

        assert len(attachments) == 12
        assert cleaned.splitlines()[0] == "[[ATTACHMENT:0]]"
        assert cleaned.splitlines()[-1] == "[[ATTACHMENT:11]]"