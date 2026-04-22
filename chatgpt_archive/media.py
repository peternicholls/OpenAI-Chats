"""Core media filesystem helpers shared by CLI and API layers."""

import os
import shutil
from pathlib import Path

from chatgpt_archive.db import get_db_path


def get_archive_media_dir(
    db_path: Path | None = None, configured_dir: str | Path | None = None
) -> Path:
    """Resolve the archive media directory from env, config, or DB location."""
    env_path = os.environ.get("CHATGPT_ARCHIVE_DIR")
    if env_path:
        return Path(env_path).expanduser()

    if configured_dir:
        return Path(configured_dir).expanduser()

    resolved_db_path = db_path.expanduser() if db_path is not None else get_db_path()
    return resolved_db_path.parent / "media"


def persist_archive_media(source_dir: Path, destination_dir: Path | None = None) -> Path:
    """Merge extracted archive files into the permanent media directory."""
    source_dir = Path(source_dir).expanduser().resolve()
    destination_dir = (
        destination_dir or get_archive_media_dir()
    ).expanduser().resolve()

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
        if target_path.exists():
            continue

        try:
            os.link(source_path, target_path)
        except OSError:
            shutil.copy2(source_path, target_path)

    return destination_dir