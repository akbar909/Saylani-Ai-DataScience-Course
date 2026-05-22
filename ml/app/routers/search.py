from fastapi import APIRouter, HTTPException, Query

from app.core.config import settings
from app.models.schemas import SearchResponse
from app.services.analytics import search_data

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.default_page_size, ge=1, le=settings.max_page_size),
) -> SearchResponse:
    try:
        total, items = await search_data(query=q, page=page, page_size=page_size)
        return SearchResponse(
            query=q,
            page=page,
            page_size=page_size,
            total=total,
            items=items,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Search failed: {exc}") from exc
