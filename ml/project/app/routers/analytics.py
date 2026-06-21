from fastapi import APIRouter, HTTPException, Query

from app.core.config import settings
from app.models.schemas import InsightsResponse, SummaryResponse, TrendResponse
from app.services.analytics import get_insights, get_summary, get_trending_keywords
from app.services.cache import TTLCache

router = APIRouter(tags=["analytics"])


def get_cache() -> TTLCache:
    from app.main import cache

    return cache


@router.get("/trends", response_model=TrendResponse)
async def trends(
    days: int = Query(default=7, ge=1, le=30),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.default_page_size, ge=1, le=settings.max_page_size),
) -> TrendResponse:
    cache_key = f"analytics:trends:{days}:{page}:{page_size}"
    cached = get_cache().get(cache_key)
    if cached is not None:
        return TrendResponse(**cached)

    try:
        total, items = await get_trending_keywords(days=days, page=page, page_size=page_size)
        payload = {"days": days, "total_keywords": total, "items": items}
        get_cache().set(cache_key, payload)
        return TrendResponse(**payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to compute trends: {exc}") from exc


@router.get("/insights", response_model=InsightsResponse)
async def insights(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
) -> InsightsResponse:
    cache_key = f"analytics:insights:{page}:{page_size}"
    cached = get_cache().get(cache_key)
    if cached is not None:
        return InsightsResponse(**cached)

    try:
        data = await get_insights(page=page, page_size=page_size)
        get_cache().set(cache_key, data)
        return InsightsResponse(**data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch insights: {exc}") from exc


@router.get("/analytics/summary", response_model=SummaryResponse)
async def analytics_summary(days: int = Query(default=7, ge=2, le=60)) -> SummaryResponse:
    cache_key = f"analytics:summary:{days}"
    cached = get_cache().get(cache_key)
    if cached is not None:
        return SummaryResponse(**cached)

    try:
        data = await get_summary(days=days)
        get_cache().set(cache_key, data)
        return SummaryResponse(**data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch summary: {exc}") from exc
