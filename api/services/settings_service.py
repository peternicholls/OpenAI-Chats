"""Settings service for persistent user preferences.

Manages user settings stored in a JSON file alongside the database
at ~/.chatgpt-archive/settings.json.

Sensitive settings (like API keys) are encrypted using Fernet symmetric encryption.
"""

import base64
import json
import logging
import os
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


DEFAULT_SETTINGS = {
    "theme": "light",
    "default_export_format": "md",
    "sidebar_open": True,
    "openai_api_key": "",
    "embedding_model": "text-embedding-3-small",
    "items_per_page": 50,
}

# Settings that should be encrypted at rest
ENCRYPTED_SETTINGS = {"openai_api_key"}


def _get_encryption_key() -> bytes:
    """Get or generate the encryption key.

    The key is stored in a separate file (.chatgpt-archive/encryption.key).
    If no key exists, a new one is generated.
    """
    key_path = get_settings_path().parent / "encryption.key"

    if key_path.exists():
        try:
            key = key_path.read_bytes().strip()
            # Validate it's a valid Fernet key
            Fernet(key)
            return key
        except (OSError, ValueError) as e:
            logger.warning("Invalid encryption key, generating new one: %s", e)

    # Generate new key
    key = Fernet.generate_key()
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_bytes(key)
    # Restrict permissions (owner read/write only)
    key_path.chmod(0o600)
    logger.info("Generated new encryption key at %s", key_path)
    return key


def _encrypt_value(value: str) -> str:
    """Encrypt a string value using Fernet.

    Returns base64-encoded encrypted string prefixed with 'enc:'.
    """
    if not value:
        return value

    try:
        key = _get_encryption_key()
        f = Fernet(key)
        encrypted = f.encrypt(value.encode("utf-8"))
        return f"enc:{base64.urlsafe_b64encode(encrypted).decode('ascii')}"
    except Exception as e:
        logger.error("Encryption failed: %s", e)
        return value


def _decrypt_value(value: str) -> str:
    """Decrypt a Fernet-encrypted string.

    Expects base64-encoded string prefixed with 'enc:'.
    Returns original value if decryption fails or value is not encrypted.
    """
    if not value or not value.startswith("enc:"):
        return value

    try:
        key = _get_encryption_key()
        f = Fernet(key)
        encrypted_data = base64.urlsafe_b64decode(value[4:])
        return f.decrypt(encrypted_data).decode("utf-8")
    except (InvalidToken, ValueError) as e:
        logger.warning("Decryption failed (key may have changed): %s", e)
        return ""
    except Exception as e:
        logger.error("Unexpected decryption error: %s", e)
        return ""


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
        Encrypted values are automatically decrypted.
    """
    settings_path = get_settings_path()
    settings = dict(DEFAULT_SETTINGS)

    if settings_path.exists():
        try:
            with open(settings_path, encoding="utf-8") as f:
                stored = json.load(f)
            
            # Decrypt encrypted settings
            for key, value in stored.items():
                if key in ENCRYPTED_SETTINGS and isinstance(value, str):
                    stored[key] = _decrypt_value(value)
            
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
        Sensitive settings are automatically encrypted.
    """
    settings_path = get_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    # Create a copy with encrypted values
    settings_to_save = dict(settings)
    for key in ENCRYPTED_SETTINGS:
        if key in settings_to_save and settings_to_save[key]:
            settings_to_save[key] = _encrypt_value(settings_to_save[key])

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings_to_save, f, indent=2)


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
