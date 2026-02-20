"""Search endpoints."""

import logging

from fastapi import APIRouter, HTTPException

from api.middleware.validation import validate_pagination, validate_query_param
from api.models.requests import SearchRequest
from api.models.responses import PaginatedResponse, SearchResult
from api.services import archive_service
from chatgpt_archive.search import InvalidQueryError

router = APIRouter(tags=["Search"])
logger = logging.getLogger(__name__)


@router.post("/api/search", response_model=PaginatedResponse)
async def search_conversations(request: SearchRequest) -> PaginatedResponse:
    """Search conversations with keyword, semantic, or hybrid search."""
    # Validate query parameter for injection attacks
    try:
        validated_query = validate_query_param("query", request.query, max_length=500)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
    # Validate pagination
    validated_offset, validated_limit = validate_pagination(request.offset, request.limit)

    try:
        results = archive_service.search_conversations(
            query=validated_query,
            from_date=request.from_date,
            to_date=request.to_date,
            limit=validated_limit,
            offset=validated_offset,
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
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Search request failed")
        raise HTTPException(status_code=500, detail="Internal server error") from e
