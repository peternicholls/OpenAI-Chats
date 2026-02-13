"""Search endpoints."""

from fastapi import APIRouter, HTTPException

from chatgpt_archive.search import InvalidQueryError
from api.models.requests import SearchRequest
from api.models.responses import PaginatedResponse, SearchResult
from api.services import archive_service

router = APIRouter(tags=["Search"])


@router.post("/api/search", response_model=PaginatedResponse)
async def search_conversations(request: SearchRequest) -> PaginatedResponse:
    """Search conversations with keyword, semantic, or hybrid search."""
    try:
        results = archive_service.search_conversations(
            query=request.query,
            from_date=request.from_date,
            to_date=request.to_date,
            limit=request.limit,
            offset=request.offset,
            search_type=request.search_type,
        )
        items = [SearchResult(**r) for r in results["items"]]
        return PaginatedResponse(
            total=results["total"],
            offset=results.get("offset", 0),
            limit=results.get("limit", request.limit),
            items=items,
        )
    except InvalidQueryError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
