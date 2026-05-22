import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.models.schemas import IngestRequest, IngestResponse
from app.services.cache import TTLCache
from app.services.news_api import fetch_news_articles
from app.services.processor import process_recent_raw_data, store_raw_articles

router = APIRouter(tags=["ingestion"])
logger = logging.getLogger(__name__)


def get_cache() -> TTLCache:
    from app.main import cache

    return cache


async def run_ingestion_pipeline(payload: IngestRequest) -> tuple[int, int]:
    articles = await fetch_news_articles(
        query=payload.query,
        category=payload.category,
        language=payload.language,
        page_size=payload.page_size,
        from_days=payload.from_days,
    )

    inserted_count = await store_raw_articles(articles)
    processed_count = await process_recent_raw_data(limit=max(inserted_count, payload.page_size))

    get_cache().invalidate_prefix("analytics:")

    return inserted_count, processed_count


async def run_ingestion_pipeline_background(payload: IngestRequest) -> None:
    try:
        ingested_count, processed_count = await run_ingestion_pipeline(payload)
        logger.info(
            "Background ingestion completed: ingested=%s processed=%s",
            ingested_count,
            processed_count,
        )
    except Exception as exc:
        logger.error("Background ingestion failed: %s", exc)


@router.post("/ingest", response_model=IngestResponse)
async def ingest_data(payload: IngestRequest, background_tasks: BackgroundTasks, run_in_background: bool = True) -> IngestResponse:
    try:
        if run_in_background:
            background_tasks.add_task(run_ingestion_pipeline_background, payload)
            return IngestResponse(
                status="accepted",
                message="Ingestion started in background",
            )

        ingested_count, processed_count = await run_ingestion_pipeline(payload)
        return IngestResponse(
            status="success",
            message="Ingestion and processing completed",
            ingested_count=ingested_count,
            processed_count=processed_count,
        )

    except Exception as exc:
        logger.exception("Ingestion failed")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc
