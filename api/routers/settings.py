"""Settings router for user preferences."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from api.services.settings_service import load_settings, save_settings

router = APIRouter(tags=["Settings"])


class UserSettings(BaseModel):
    """User settings model."""

    theme: str = Field("light", description="UI theme: light, dark, system")
    default_export_format: str = Field("md", description="Default export format")
    openai_api_key: str | None = Field(
        None, description="OpenAI API key for embeddings"
    )
    sidebar_open: bool = Field(True, description="Whether sidebar is open")
    embedding_model: str = Field(
        "text-embedding-3-small", description="Model for embeddings"
    )
    items_per_page: int = Field(
        50, description="Number of conversations per page (FR-022)"
    )
    archive_media_dir: str | None = Field(
        None, description="Optional path to the extracted archive media directory"
    )
    code_line_numbers: bool = Field(False, description="Show line numbers in code blocks")
    long_prompt_truncation: bool = Field(True, description="Truncate user prompts longer than 500 characters")


class UserSettingsUpdate(BaseModel):
    """Partial update model for settings."""

    theme: str | None = None
    default_export_format: str | None = None
    openai_api_key: str | None = None
    sidebar_open: bool | None = None
    embedding_model: str | None = None
    items_per_page: int | None = None
    archive_media_dir: str | None = None
    code_line_numbers: bool | None = None
    long_prompt_truncation: bool | None = None


@router.get("/api/settings", response_model=UserSettings)
async def get_settings() -> UserSettings:
    """Get current user settings.

    Note (S-02): The OpenAI API key is returned decrypted. This is acceptable
    for a single-user, trusted-network deployment (FR-019). Do not expose this
    endpoint on an untrusted network without additional access controls.
    """
    settings = load_settings()
    return UserSettings(**settings)


@router.put("/api/settings", response_model=UserSettings)
async def update_settings(updates: UserSettingsUpdate) -> UserSettings:
    """Update user settings.

    Only provided fields will be updated.
    """
    current = load_settings()
    update_dict = updates.model_dump(exclude_unset=True)
    current.update(update_dict)
    save_settings(current)
    return UserSettings(**current)
