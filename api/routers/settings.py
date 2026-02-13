"""Settings router for user preferences."""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

from api.services.settings_service import load_settings, save_settings

router = APIRouter(tags=["Settings"])


class UserSettings(BaseModel):
    """User settings model."""

    theme: str = Field("light", description="UI theme: light, dark, system")
    default_export_format: str = Field("md", description="Default export format")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key for embeddings")
    sidebar_open: bool = Field(True, description="Whether sidebar is open")
    embedding_model: str = Field("text-embedding-3-small", description="Model for embeddings")


class UserSettingsUpdate(BaseModel):
    """Partial update model for settings."""

    theme: Optional[str] = None
    default_export_format: Optional[str] = None
    openai_api_key: Optional[str] = None
    sidebar_open: Optional[bool] = None
    embedding_model: Optional[str] = None


@router.get("/api/settings", response_model=UserSettings)
async def get_settings() -> UserSettings:
    """Get current user settings."""
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
