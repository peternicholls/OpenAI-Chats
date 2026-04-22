"""Helpers for building ordered render segments from message content."""

import ast
import re
from typing import Any

from api.models.responses import (
    Attachment,
    AttachmentSegment,
    FallbackSegment,
    MarkdownSegment,
    RenderSegment,
)
from api.services import media_service

CODE_FENCE_RE = re.compile(r"^\s*```")
CITATION_TOKEN_RE = re.compile(
    r"\uE200(?:file)?cite(?:\uE202turn\d+(?:search|view|file|news)\d+)+\uE201"
)
STRUCTURED_KEYS = {
    "asset_pointer",
    "content_type",
    "metadata",
    "mime_type",
    "attachments",
}
MAX_STRUCTURED_PAYLOAD_LENGTH = 10_000


def resolve_inline_citations(
    content: str | None, metadata: dict[str, Any] | None
) -> str | None:
    """Replace inline citation tokens with readable markdown using message metadata."""
    if not content:
        return content

    replacements = _collect_content_reference_replacements(content, metadata)
    replacements.extend(_collect_file_citation_replacements(content, metadata))
    resolved = _apply_replacements(content, replacements)
    return CITATION_TOKEN_RE.sub("", resolved)


def build_render_segments(
    content: str | None, attachments: list[Attachment]
) -> list[RenderSegment]:
    """Convert stored message content plus resolved attachments into render segments."""
    if not content:
        return [
            AttachmentSegment(kind="attachment", attachment_index=index)
            for index, _attachment in enumerate(attachments)
        ]

    segments: list[RenderSegment] = []
    markdown_lines: list[str] = []
    rendered_attachment_indexes: set[int] = set()
    in_code_fence = False

    for raw_line in content.splitlines():
        stripped = raw_line.strip()

        if CODE_FENCE_RE.match(raw_line):
            markdown_lines.append(raw_line)
            in_code_fence = not in_code_fence
            continue

        if not in_code_fence:
            token_match = media_service.ATTACHMENT_TOKEN_RE.fullmatch(stripped)
            if token_match is not None:
                _flush_markdown_segment(markdown_lines, segments)
                attachment_index = int(token_match.group(1))
                segments.append(
                    AttachmentSegment(
                        kind="attachment", attachment_index=attachment_index
                    )
                )
                rendered_attachment_indexes.add(attachment_index)
                continue

            fallback_segment = classify_structured_payload(raw_line)
            if fallback_segment is not None:
                _flush_markdown_segment(markdown_lines, segments)
                segments.append(fallback_segment)
                continue

        markdown_lines.append(raw_line)

    _flush_markdown_segment(markdown_lines, segments)

    for index, _attachment in enumerate(attachments):
        if index in rendered_attachment_indexes:
            continue
        segments.append(AttachmentSegment(kind="attachment", attachment_index=index))

    return segments


def classify_structured_payload(raw_text: str) -> FallbackSegment | None:
    """Return a fallback segment when a line contains structured transport payload data."""
    stripped = raw_text.strip()
    if not stripped:
        return None

    if not _looks_like_structured_payload(stripped):
        return None

    parsed = _parse_payload(stripped)
    if parsed is None:
        if _mentions_structured_keys(stripped):
            return FallbackSegment(
                kind="fallback",
                text=stripped,
                fallback_label="Malformed content",
            )
        return None

    if not _contains_structured_keys(parsed):
        return None

    fallback_label = "Unsupported content"
    if _contains_asset_pointer(parsed):
        fallback_label = "Malformed attachment payload"

    return FallbackSegment(
        kind="fallback", text=stripped, fallback_label=fallback_label
    )


def _flush_markdown_segment(
    markdown_lines: list[str], segments: list[RenderSegment]
) -> None:
    if not markdown_lines:
        return

    text = "\n".join(markdown_lines).strip("\n")
    markdown_lines.clear()
    if not text.strip():
        return

    segments.append(MarkdownSegment(kind="markdown", text=text))


def _looks_like_structured_payload(text: str) -> bool:
    return (text.startswith("{") and text.endswith("}")) or (
        text.startswith("[") and text.endswith("]")
    )


def _parse_payload(text: str) -> Any | None:
    if len(text) > MAX_STRUCTURED_PAYLOAD_LENGTH:
        return None
    try:
        return ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return None


def _mentions_structured_keys(text: str) -> bool:
    lowered = text.lower()
    return any(key in lowered for key in STRUCTURED_KEYS)


def _contains_structured_keys(value: Any) -> bool:
    if isinstance(value, dict):
        if STRUCTURED_KEYS.intersection(value):
            return True
        return any(_contains_structured_keys(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_structured_keys(item) for item in value)
    return False


def _contains_asset_pointer(value: Any) -> bool:
    if isinstance(value, dict):
        if "asset_pointer" in value:
            return True
        return any(_contains_asset_pointer(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_asset_pointer(item) for item in value)
    return False


def _collect_content_reference_replacements(
    content: str, metadata: dict[str, Any] | None
) -> list[tuple[int, int, str]]:
    if not metadata:
        return []

    content_references = metadata.get("content_references")
    if not isinstance(content_references, list):
        return []

    replacements: list[tuple[int, int, str]] = []
    search_start = 0
    for reference in content_references:
        if not isinstance(reference, dict):
            continue
        matched_text = reference.get("matched_text")
        alt = reference.get("alt")
        if not isinstance(matched_text, str) or not isinstance(alt, str):
            continue

        start = content.find(matched_text, search_start)
        if start == -1:
            start = content.find(matched_text)
        if start == -1:
            continue

        end = start + len(matched_text)
        replacements.append((start, end, alt))
        search_start = end

    return replacements


def _collect_file_citation_replacements(
    content: str, metadata: dict[str, Any] | None
) -> list[tuple[int, int, str]]:
    if not metadata:
        return []

    citations = metadata.get("citations")
    if not isinstance(citations, list):
        return []

    replacements: list[tuple[int, int, str]] = []
    for citation in citations:
        if not isinstance(citation, dict):
            continue
        start = citation.get("start_ix")
        end = citation.get("end_ix")
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        if start < 0 or end <= start or end > len(content):
            continue

        replacement = _format_file_citation(citation)
        if replacement is None:
            continue

        replacements.append((start, end, replacement))

    return replacements


def _format_file_citation(citation: dict[str, Any]) -> str | None:
    metadata = citation.get("metadata")
    if not isinstance(metadata, dict):
        return None

    raw_label = metadata.get("title") or metadata.get("name") or "Source"
    if not isinstance(raw_label, str):
        raw_label = "Source"

    label = " ".join(raw_label.split()).strip()
    if not label:
        label = "Source"

    return f"(Source: {label})"


def _apply_replacements(content: str, replacements: list[tuple[int, int, str]]) -> str:
    if not replacements:
        return content

    resolved = content
    applied_spans: list[tuple[int, int]] = []
    for start, end, replacement in sorted(
        replacements, key=lambda item: item[0], reverse=True
    ):
        if any(
            start < existing_end and end > existing_start
            for existing_start, existing_end in applied_spans
        ):
            continue
        resolved = resolved[:start] + replacement + resolved[end:]
        applied_spans.append((start, end))

    return resolved
