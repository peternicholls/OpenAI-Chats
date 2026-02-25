"""Pydantic request models for the ChatGPT Archive API."""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Search query parameters."""

    query: str = Field(..., min_length=1, max_length=500, description="Search term")
    from_date: str | None = Field(None, description="ISO date or YYYY-MM-DD")
    to_date: str | None = Field(None, description="ISO date or YYYY-MM-DD")
    limit: int = Field(20, ge=1, le=100, description="Max results")
    offset: int = Field(0, ge=0, description="Pagination offset")
    search_type: str = Field("keyword", description="keyword, semantic, hybrid")


class TagRequest(BaseModel):
    """Add/remove tag."""

    tag_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Tag name",
    )


class ExportRequest(BaseModel):
    """Export conversation."""

    format: str = Field(..., description="md, json, yaml, html, xml, csv, xlsx")


class EmbeddingRequest(BaseModel):
    """Generate embeddings."""

    model: str = Field("text-embedding-3-small", description="OpenAI embedding model")
    batch_size: int = Field(100, ge=1, le=500, description="Messages per batch")
    estimate_only: bool = Field(False, description="Return cost estimate only")
    max_cost: float | None = Field(
        5.00,
        ge=0.0,
        le=1000.0,
        description="Maximum cost in USD (default $5.00, None=unlimited)",
    )
