"""Tests for render segment building."""

from api.tests.conftest import build_formatted_message_content
from api.models.responses import Attachment
from api.services import formatting_service


def build_attachment(index: int) -> Attachment:
    return Attachment(
        type="image",
        url=f"/api/media/conv/file_{index}",
        filename=f"image-{index}.png",
        mime_type="image/png",
        width=640,
        height=480,
        size_bytes=1024,
        found=True,
    )


def test_build_render_segments_returns_markdown_for_plain_text() -> None:
    segments = formatting_service.build_render_segments("hello world", [])

    assert len(segments) == 1
    assert segments[0].kind == "markdown"
    assert segments[0].text == "hello world"


def test_build_render_segments_preserves_attachment_order() -> None:
    segments = formatting_service.build_render_segments(
        "Intro\n[[ATTACHMENT:0]]\nAfter",
        [build_attachment(0)],
    )

    assert [segment.kind for segment in segments] == ["markdown", "attachment", "markdown"]
    assert segments[1].attachment_index == 0


def test_build_render_segments_creates_fallback_for_structured_payload() -> None:
    segments = formatting_service.build_render_segments(
        "Intro\n{'content_type': 'unsupported_widget', 'metadata': {'kind': 'chart'}}",
        [],
    )

    assert [segment.kind for segment in segments] == ["markdown", "fallback"]
    assert segments[1].fallback_label == "Unsupported content"


def test_build_render_segments_keeps_markdown_block_intact() -> None:
    content = build_formatted_message_content()

    segments = formatting_service.build_render_segments(content, [])

    assert len(segments) == 1
    assert segments[0].kind == "markdown"
    assert segments[0].text == content


def test_build_render_segments_leaves_code_fences_as_markdown() -> None:
    segments = formatting_service.build_render_segments(
        "```json\n{'content_type': 'unsupported_widget'}\n```",
        [],
    )

    assert len(segments) == 1
    assert segments[0].kind == "markdown"
    assert "unsupported_widget" in segments[0].text