"""Embedding generation endpoints."""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks

from api.models.requests import EmbeddingRequest
from api.models.responses import ImportProgress
from api.services import archive_service

router = APIRouter(tags=["Embeddings"])


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
    except ImportError:
        raise HTTPException(
            status_code=400,
            detail="Semantic search dependencies not installed. "
            "Install with: pip install 'chatgpt-archive[semantic]'",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/embeddings/generate", status_code=202, response_model=ImportProgress)
async def generate_embeddings(
    request: EmbeddingRequest,
    background_tasks: BackgroundTasks,
) -> ImportProgress:
    """Generate embeddings for semantic search."""
    try:
        from chatgpt_archive.embeddings import embed_messages

        if request.estimate_only:
            return ImportProgress(
                status="complete",
                current=0,
                total=0,
                percent=100.0,
                message="Use GET /api/embeddings/estimate for cost estimation",
            )

        def run_embedding():
            conn = archive_service.get_connection()
            try:
                embed_messages(
                    conn,
                    model=request.model,
                    batch_size=request.batch_size,
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
    except ImportError:
        raise HTTPException(
            status_code=400,
            detail="Semantic search dependencies not installed.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
