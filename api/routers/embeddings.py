"""Embedding generation endpoints."""

import sqlite3

import httpx
from fastapi import APIRouter, BackgroundTasks, Body, HTTPException, Query
from pydantic import BaseModel

from api.models.requests import EmbeddingRequest
from api.models.responses import ImportProgress
from api.services import archive_service, settings_service

router = APIRouter(tags=["Embeddings"])


class EmbeddingCancelledError(Exception):
    """Raised when embedding generation is cancelled by user."""

    pass


class ValidateKeyRequest(BaseModel):
    """API key validation request body."""

    api_key: str | None = None


async def validate_openai_api_key(api_key: str) -> tuple[bool, str]:
    """Validate OpenAI API key by making a test API call.

    Args:
        api_key: The OpenAI API key to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not api_key or not api_key.strip():
        return False, "OpenAI API key is required"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )

            if response.status_code == 200:
                return True, ""
            elif response.status_code == 401:
                return False, "Invalid API key"
            elif response.status_code == 429:
                return False, "API rate limit exceeded or insufficient quota"
            else:
                return False, f"API validation failed: {response.status_code}"
    except httpx.TimeoutException:
        return False, "API validation timed out"
    except httpx.RequestError as e:
        return False, f"Network error during API validation: {e}"


@router.post("/api/embeddings/validate-key")
async def validate_api_key(
    request: ValidateKeyRequest = Body(default_factory=ValidateKeyRequest),
) -> dict:
    """Validate an API key.

    If `api_key` is not provided, validates the stored key from settings.
    """
    api_key = (
        request.api_key
        if request.api_key is not None
        else settings_service.get_setting("openai_api_key")
    )
    is_valid, error = await validate_openai_api_key(api_key or "")

    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    return {"valid": True, "message": "API key is valid"}


@router.get("/api/embeddings/stats")
async def get_embedding_stats() -> dict:
    """Get embedding statistics for the archive."""
    try:
        conn = archive_service.get_connection()
        try:
            cursor = conn.cursor()
            # Total conversations
            cursor.execute("SELECT COUNT(*) FROM conversations")
            total = cursor.fetchone()[0]
            # Conversations with embeddings (when embedding table exists).
            try:
                cursor.execute(
                    """
                    SELECT COUNT(DISTINCT m.conversation_id)
                    FROM message_embeddings me
                    JOIN messages m ON m.id = me.message_id
                    """
                )
                with_embeddings = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                with_embeddings = 0
            return {
                "total": total,
                "withEmbeddings": with_embeddings,
            }
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/api/embeddings/cancel")
async def cancel_embedding_generation() -> dict:
    """Cancel the current embedding generation process."""
    cancelled = archive_service.cancel_embedding_generation()
    if cancelled:
        return {
            "cancelled": True,
            "message": "Cancellation requested. Will stop after current batch.",
        }
    return {"cancelled": False, "message": "No embedding generation in progress."}


@router.get("/api/embeddings/estimate")
async def estimate_embeddings(
    model: str = Query("text-embedding-3-small"),
) -> dict:
    """Estimate embedding generation cost."""
    try:
        from chatgpt_archive.embeddings import estimate_cost

        conn = archive_service.get_connection()
        try:
            result = estimate_cost(conn, model=model)
            return result
        finally:
            conn.close()
    except ImportError as e:
        raise HTTPException(
            status_code=400,
            detail="Semantic search dependencies not installed. "
            "Install with: pip install 'chatgpt-archive[semantic]'",
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/api/embeddings/generate", status_code=202, response_model=ImportProgress)
async def generate_embeddings(
    request: EmbeddingRequest,
    background_tasks: BackgroundTasks,
) -> ImportProgress:
    """Generate embeddings for semantic search."""
    try:
        from chatgpt_archive.embeddings import (
            EmbeddingProgress as EmbProgress,
        )
        from chatgpt_archive.embeddings import (
            embed_messages,
            estimate_cost,
        )

        if request.estimate_only:
            return ImportProgress(
                status="complete",
                current=0,
                total=0,
                percent=100.0,
                message="Use GET /api/embeddings/estimate for cost estimation",
            )

        # Validate API key before starting generation
        api_key = settings_service.get_setting("openai_api_key")
        is_valid, error = await validate_openai_api_key(api_key or "")
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"OpenAI API key validation failed: {error}. "
                "Please configure a valid API key in Settings.",
            )

        # Check cost limit if specified
        if request.max_cost is not None:
            conn = archive_service.get_connection()
            try:
                estimate = estimate_cost(conn, model=request.model)
                estimated_cost = estimate.get("estimated_cost", 0)
                if estimated_cost > request.max_cost:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Estimated cost (${estimated_cost:.2f}) exceeds "
                            f"limit (${request.max_cost:.2f}). "
                            "Increase max_cost parameter or reduce messages to embed."
                        ),
                    )
            finally:
                conn.close()

        # Capture max_cost and api_key for use in background task
        max_cost_limit = request.max_cost
        stored_api_key = api_key

        def progress_callback(progress: EmbProgress) -> None:
            """Update embedding progress during generation.

            Raises EmbeddingCancelledError if cancellation was requested or cost limit exceeded.
            """
            # Check for cancellation
            if archive_service.is_embedding_cancelled():
                archive_service.clear_embedding_cancellation()
                raise EmbeddingCancelledError("Embedding generation cancelled by user")

            # Check cost limit during processing
            if max_cost_limit is not None and progress.estimated_cost > max_cost_limit:
                raise EmbeddingCancelledError(
                    f"Cost limit exceeded (${progress.estimated_cost:.4f} > ${max_cost_limit:.2f})"
                )

            archive_service.update_embedding_progress(
                status="processing",
                current=progress.completed,
                total=progress.total,
                message=(
                    f"Processed {progress.completed}/{progress.total} messages "
                    f"(~${progress.estimated_cost:.4f})"
                ),
            )

        def run_embedding():
            # Clear any previous cancellation flag
            archive_service.clear_embedding_cancellation()

            archive_service.update_embedding_progress(
                status="processing",
                current=0,
                total=0,
                message="Starting embedding generation...",
            )
            conn = archive_service.get_connection()
            try:
                from chatgpt_archive.embeddings import APIKeyMissingError, EmbeddingError

                result = embed_messages(
                    conn,
                    model=request.model,
                    batch_size=request.batch_size,
                    progress_callback=progress_callback,
                    api_key=stored_api_key,
                )
                archive_service.update_embedding_progress(
                    status="complete",
                    current=result.completed,
                    total=result.total,
                    message=(
                        f"Completed! Embedded {result.completed} messages "
                        f"(~${result.estimated_cost:.4f})"
                    ),
                )
            except EmbeddingCancelledError:
                # Get current progress to show what was completed
                current_progress = archive_service.get_embedding_progress()
                archive_service.update_embedding_progress(
                    status="cancelled",
                    current=current_progress.get("current", 0),
                    total=current_progress.get("total", 0),
                    message="Embedding generation cancelled. Progress saved - can resume later.",
                )
            except APIKeyMissingError:
                archive_service.update_embedding_progress(
                    status="error",
                    current=0,
                    total=0,
                    message=(
                        "OpenAI API key not configured. "
                        "Set OPENAI_API_KEY environment variable "
                        "or configure in Settings."
                    ),
                )
            except EmbeddingError as e:
                error_msg = str(e).lower()
                if "rate limit" in error_msg or "429" in error_msg:
                    archive_service.update_embedding_progress(
                        status="error",
                        current=0,
                        total=0,
                        message="Rate limit exceeded. Please wait and try again later.",
                    )
                elif "quota" in error_msg or "insufficient" in error_msg:
                    archive_service.update_embedding_progress(
                        status="error",
                        current=0,
                        total=0,
                        message="API quota exceeded. Check your OpenAI account billing.",
                    )
                elif "invalid" in error_msg and "key" in error_msg:
                    archive_service.update_embedding_progress(
                        status="error",
                        current=0,
                        total=0,
                        message="Invalid API key. Please check your OpenAI API key in Settings.",
                    )
                else:
                    archive_service.update_embedding_progress(
                        status="error",
                        current=0,
                        total=0,
                        message=f"Embedding error: {e}",
                    )
            except Exception as e:
                error_msg = str(e).lower()
                # Handle OpenAI library errors that might not be wrapped
                if "rate_limit" in error_msg or "rate limit" in error_msg:
                    archive_service.update_embedding_progress(
                        status="error",
                        current=0,
                        total=0,
                        message="Rate limit exceeded. Please wait and try again later.",
                    )
                elif "authentication" in error_msg or "invalid api key" in error_msg:
                    archive_service.update_embedding_progress(
                        status="error",
                        current=0,
                        total=0,
                        message="Invalid API credentials. Please check your OpenAI API key.",
                    )
                elif "insufficient_quota" in error_msg or "billing" in error_msg:
                    archive_service.update_embedding_progress(
                        status="error",
                        current=0,
                        total=0,
                        message="Insufficient API quota. Check your OpenAI account billing.",
                    )
                else:
                    archive_service.update_embedding_progress(
                        status="error",
                        current=0,
                        total=0,
                        message=f"Unexpected error: {e}",
                    )
            finally:
                conn.close()

        background_tasks.add_task(run_embedding)

        return ImportProgress(
            status="pending",
            current=0,
            total=0,
            percent=0.0,
            message="Embedding generation started...",
        )
    except HTTPException:
        raise
    except ImportError as e:
        raise HTTPException(
            status_code=400,
            detail="Semantic search dependencies not installed.",
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
