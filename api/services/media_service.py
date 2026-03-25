"""Media parsing and filesystem lookup helpers for archive attachments."""

import ast
import mimetypes
import os
import re
import shutil
from pathlib import Path
from typing import Any

from chatgpt_archive import db as db_module

from api.models.responses import Attachment
from api.services.settings_service import load_settings

ATTACHMENT_TOKEN_RE = re.compile(r"\[\[ATTACHMENT:(\d+)\]\]")


def attachment_token(index: int) -> str:
    """Return the placeholder token used to preserve attachment order."""
    return f"[[ATTACHMENT:{index}]]"


def get_archive_media_dir(settings: dict[str, Any] | None = None) -> Path:
    """Resolve the archive media directory from env, settings, or the DB path."""
    env_path = os.environ.get("CHATGPT_ARCHIVE_DIR")
    if env_path:
        return Path(env_path).expanduser()

    settings = settings if settings is not None else load_settings()
    configured = settings.get("archive_media_dir") if settings else None
    if configured:
        return Path(str(configured)).expanduser()

    return db_module.get_db_path().parent / "media"


def persist_archive_media(source_dir: Path, destination_dir: Path | None = None) -> Path:
    """Merge extracted archive files into the permanent media directory."""
    source_dir = Path(source_dir).expanduser().resolve()
    destination_dir = (destination_dir or get_archive_media_dir()).expanduser().resolve()

    if source_dir == destination_dir:
        return destination_dir

    destination_dir.mkdir(parents=True, exist_ok=True)
    for source_path in source_dir.rglob("*"):
        relative_path = source_path.relative_to(source_dir)
        target_path = destination_dir / relative_path

        if source_path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
            continue

        target_path.parent.mkdir(parents=True, exist_ok=True)
        if not target_path.exists():
            shutil.copy2(source_path, target_path)

    return destination_dir


def resolve_message_content(
    content: str | None, conversation_id: str
) -> tuple[str | None, list[Attachment]]:
    """Parse attachment pointers from a stored message string.

    Returns cleaned content plus resolved attachments. If the message does not
    contain any asset pointers, the original content is returned unchanged.
    """
    if not content or "asset_pointer" not in content:
        return content, []

    attachments: list[Attachment] = []
    rendered_lines: list[str] = []

    for raw_line in content.splitlines():
        parsed = _parse_asset_pointer_line(raw_line)
        if parsed is None:
            rendered_lines.append(raw_line)
            continue

        attachment = _build_attachment(parsed, conversation_id)
        attachments.append(attachment)
        rendered_lines.append(attachment_token(len(attachments) - 1))

    cleaned = "\n".join(rendered_lines).strip()
    return cleaned or None, attachments


def resolve_conversation_media_path(conversation_id: str, file_id: str) -> Path | None:
    """Resolve a conversation-scoped media file from the archive."""
    archive_dir = get_archive_media_dir().expanduser().resolve()
    for subdir_name in ("image", "audio"):
        candidate_dir = archive_dir / conversation_id / subdir_name
        resolved = _find_first_prefix_match(candidate_dir, f"{file_id}-")
        if resolved is not None:
            return _ensure_relative_to_archive(resolved, archive_dir)
    return None


def resolve_root_media_path(file_id: str) -> Path | None:
    """Resolve a root-level archive file from the archive."""
    archive_dir = get_archive_media_dir().expanduser().resolve()
    resolved = _find_first_prefix_match(archive_dir, f"{file_id}-")
    if resolved is None:
        return None
    return _ensure_relative_to_archive(resolved, archive_dir)


def get_media_metadata(path: Path) -> tuple[str | None, str]:
    """Return detected MIME type and display filename for a stored media file."""
    mime_type = mimetypes.guess_type(path.name)[0]
    return mime_type, _display_filename(path)


def build_root_content_disposition(path: Path) -> str:
    """Build a content disposition header for root-level file downloads."""
    filename = _display_filename(path).replace('"', "")
    return f'attachment; filename="{filename}"'


def _build_attachment(parsed: dict[str, Any], conversation_id: str) -> Attachment:
    pointer = str(parsed["asset_pointer"])
    metadata = parsed.get("metadata") if isinstance(parsed.get("metadata"), dict) else {}
    size_bytes = _as_int(parsed.get("size_bytes") or metadata.get("size_bytes"))
    width = _as_int(parsed.get("width") or metadata.get("width"))
    height = _as_int(parsed.get("height") or metadata.get("height"))

    if pointer.startswith("sediment://"):
        file_id = pointer.removeprefix("sediment://")
        path = resolve_conversation_media_path(conversation_id, file_id)
        url = f"/api/media/{conversation_id}/{file_id}"
        attachment_type = "file"
        filename = file_id
        mime_type = None

        if path is not None:
            mime_type, filename = get_media_metadata(path)
            if mime_type and mime_type.startswith("image/"):
                attachment_type = "image"
            elif mime_type and mime_type.startswith("audio/"):
                attachment_type = "audio"

        return Attachment(
            type=attachment_type,
            url=url,
            filename=filename,
            mime_type=mime_type,
            width=width,
            height=height,
            size_bytes=size_bytes,
            found=path is not None,
        )

    file_id = pointer.removeprefix("file-service://")
    path = resolve_root_media_path(file_id)
    url = f"/api/media/root/{file_id}"
    filename = file_id
    mime_type = None
    if path is not None:
        mime_type, filename = get_media_metadata(path)

    return Attachment(
        type="file",
        url=url,
        filename=filename,
        mime_type=mime_type,
        width=width,
        height=height,
        size_bytes=size_bytes,
        found=path is not None,
    )


def _parse_asset_pointer_line(raw_line: str) -> dict[str, Any] | None:
    stripped = raw_line.strip()
    if "asset_pointer" not in stripped or not stripped.startswith("{"):
        return None

    try:
        parsed = ast.literal_eval(stripped)
    except (SyntaxError, ValueError):
        return None

    if not isinstance(parsed, dict):
        return None

    asset_pointer = parsed.get("asset_pointer")
    if not isinstance(asset_pointer, str):
        return None
    if not (
        asset_pointer.startswith("sediment://")
        or asset_pointer.startswith("file-service://")
    ):
        return None

    return parsed


def _find_first_prefix_match(directory: Path, prefix: str) -> Path | None:
    if not directory.exists() or not directory.is_dir():
        return None

    for entry in sorted(directory.iterdir(), key=lambda item: item.name):
        if entry.is_file() and entry.name.startswith(prefix):
            return entry.resolve()
    return None


def _ensure_relative_to_archive(path: Path, archive_dir: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(archive_dir):
        raise ValueError("Resolved media path escaped archive directory")
    return resolved


def _display_filename(path: Path) -> str:
    name = path.name
    if path.parent == get_archive_media_dir().expanduser().resolve() and name.startswith("file-"):
        parts = name.split("-", 2)
        if len(parts) == 3:
            return parts[2]
    return name


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return None