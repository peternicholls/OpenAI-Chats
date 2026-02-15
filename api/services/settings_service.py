"""Settings service for persistent user preferences.

Manages user settings stored in a JSON file alongside the database
at ~/.chatgpt-archive/settings.json.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


DEFAULT_SETTINGS = {
    "theme": "light",
    "default_export_format": "md",
    "sidebar_open": True,
    "openai_api_key": "",
    "embedding_model": "text-embedding-3-small",
}


def get_settings_path() -> Path:
    """Get path to settings JSON file."""
    db_path = os.environ.get("CHATGPT_ARCHIVE_DB", "")
    if db_path:
        return Path(db_path).parent / "settings.json"
    return Path.home() / ".chatgpt-archive" / "settings.json"


def load_settings() -> dict[str, Any]:
    """Load settings from JSON file.

    Returns:
        Settings dictionary merged with defaults.
        If file is missing, returns defaults.
        If file is corrupted, logs warning and returns defaults.
    """
    settings_path = get_settings_path()
    settings = dict(DEFAULT_SETTINGS)

    if settings_path.exists():
        try:
            with open(settings_path, encoding="utf-8") as f:
                stored = json.load(f)
            settings.update(stored)
        except json.JSONDecodeError as e:
            logger.warning("Settings file corrupted, using defaults: %s", e)
        except OSError as e:
            logger.warning("Failed to read settings file, using defaults: %s", e)

    return settings


def save_settings(settings: dict[str, Any]) -> None:
    """Save settings to JSON file.

    Args:
        settings: Settings dictionary to persist.
    """
    settings_path = get_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def get_setting(key: str) -> Any:
    """Get a single setting value.

    Args:
        key: Setting key name.

    Returns:
        Setting value or None if not found.
    """
    settings = load_settings()
    return settings.get(key)


def update_setting(key: str, value: Any) -> dict[str, Any]:
    """Update a single setting and persist.

    Args:
        key: Setting key name.
        value: New value.

    Returns:
        Updated settings dictionary.
    """
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
    return settings
