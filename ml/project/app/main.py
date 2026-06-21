from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import ensure_indexes
from app.core.logging_config import setup_logging
from app.models.schemas import ErrorResponse
from app.routers.analytics import router as analytics_router
from app.routers.ingest import router as ingest_router
from app.routers.search import router as search_router
from app.services.cache import TTLCache

setup_logging()
cache = TTLCache(ttl_seconds=settings.cache_ttl_seconds)
base_dir = Path(__file__).resolve().parent.parent
dashboard_dir = base_dir / "dashboard"

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI-Powered Market Intelligence & Trend Analytics Platform",
)

if dashboard_dir.exists():
    app.mount("/dashboard", StaticFiles(directory=str(dashboard_dir), html=True), name="dashboard")


@app.on_event("startup")
async def startup_event() -> None:
    await ensure_indexes()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            detail=f"Validation failed: {exc.errors()}",
            timestamp=datetime.utcnow(),
        ).model_dump(mode="json"),
    )


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "AI Market Intelligence API is running"}


app.include_router(ingest_router)
app.include_router(analytics_router)
app.include_router(search_router)
