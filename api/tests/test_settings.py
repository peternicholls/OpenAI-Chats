"""Tests for settings service — encryption, persistence, and defaults.

T033: Covers settings encryption round-trip, key generation, load/save
cycle, and items_per_page default (T016/T017).
"""

import json

import pytest

from api.services.settings_service import (
    DEFAULT_SETTINGS,
    ENCRYPTED_SETTINGS,
    _decrypt_value,
    _encrypt_value,
    load_settings,
    save_settings,
    get_setting,
    update_setting,
)


@pytest.fixture(autouse=True)
def isolated_settings(tmp_path, monkeypatch):
    """Redirect settings + encryption key to a temp directory."""
    db_path = tmp_path / "chats.db"
    monkeypatch.setenv("CHATGPT_ARCHIVE_DB", str(db_path))
    # Also redirect the key so tests don't touch ~/.chatgpt-archive
    yield tmp_path


# ---------------------------------------------------------------------------
# Default settings
# ---------------------------------------------------------------------------


class TestDefaultSettings:
    def test_items_per_page_default_is_50(self):
        assert DEFAULT_SETTINGS["items_per_page"] == 50

    def test_openai_api_key_in_encrypted_settings(self):
        assert "openai_api_key" in ENCRYPTED_SETTINGS

    def test_load_settings_returns_defaults_when_no_file(self):
        settings = load_settings()
        for key, value in DEFAULT_SETTINGS.items():
            assert key in settings
            assert settings[key] == value


# ---------------------------------------------------------------------------
# Encryption helpers
# ---------------------------------------------------------------------------


class TestEncryptionHelpers:
    def test_encrypt_returns_enc_prefix(self):
        token = _encrypt_value("sk-super-secret")
        assert token.startswith("enc:")

    def test_decrypt_round_trip(self):
        plain = "sk-my-api-key-12345"
        encrypted = _encrypt_value(plain)
        assert encrypted != plain
        decrypted = _decrypt_value(encrypted)
        assert decrypted == plain

    def test_encrypt_empty_string_returns_unchanged(self):
        assert _encrypt_value("") == ""

    def test_decrypt_empty_string_returns_unchanged(self):
        assert _decrypt_value("") == ""

    def test_decrypt_plain_value_passthrough(self):
        """Values without 'enc:' prefix are returned as-is."""
        assert _decrypt_value("not-encrypted") == "not-encrypted"

    def test_decrypt_invalid_token_returns_empty(self):
        """Tampered ciphertext should return empty string, not raise."""
        result = _decrypt_value("enc:AAAAAAAAAAAAAAAA")
        assert result == ""


# ---------------------------------------------------------------------------
# Persistence round-trip
# ---------------------------------------------------------------------------


class TestSettingsPersistence:
    def test_save_and_load_plain_setting(self):
        save_settings({**DEFAULT_SETTINGS, "theme": "dark"})
        loaded = load_settings()
        assert loaded["theme"] == "dark"

    def test_save_and_load_items_per_page(self):
        save_settings({**DEFAULT_SETTINGS, "items_per_page": 25})
        loaded = load_settings()
        assert loaded["items_per_page"] == 25

    def test_save_encrypts_api_key_on_disk(self, tmp_path):
        from api.services.settings_service import get_settings_path

        settings = {**DEFAULT_SETTINGS, "openai_api_key": "sk-secret"}
        save_settings(settings)

        # Read raw JSON — should NOT contain the plain key
        raw = json.loads(get_settings_path().read_text())
        assert raw["openai_api_key"] != "sk-secret"
        assert raw["openai_api_key"].startswith("enc:")

    def test_load_decrypts_api_key(self):
        save_settings({**DEFAULT_SETTINGS, "openai_api_key": "sk-decrypted"})
        loaded = load_settings()
        assert loaded["openai_api_key"] == "sk-decrypted"

    def test_load_returns_defaults_on_corrupt_file(self, tmp_path):
        from api.services.settings_service import get_settings_path

        get_settings_path().parent.mkdir(parents=True, exist_ok=True)
        get_settings_path().write_text("{invalid json")
        settings = load_settings()
        # Should fall back to defaults rather than raise
        assert settings["theme"] == DEFAULT_SETTINGS["theme"]

    def test_update_setting_persists(self):
        update_setting("theme", "system")
        assert get_setting("theme") == "system"
