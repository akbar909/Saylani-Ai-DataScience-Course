from contextlib import asynccontextmanager

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import agent, auth, billing, documents, forecast, fraud, overview, webhooks
from app.core.config import get_settings
from app.core.database import init_database
from app.core.model_registry import ModelRegistry
from app.services.fraud import FraudService


@asynccontextmanager
async def lifespan(application: FastAPI):
    settings = get_settings()
    settings.upload_root.mkdir(parents=True, exist_ok=True)
    database_client = await init_database(settings)
    registry = ModelRegistry(settings)
    application.state.database_client = database_client
    application.state.model_registry = registry
    application.state.fraud_service = FraudService(registry)
    yield
    database_client.close()


settings = get_settings()
settings.upload_root.mkdir(parents=True, exist_ok=True)
app = FastAPI(title="AI Finance SaaS API", version="0.2.0", lifespan=lifespan)
app.mount("/uploads", StaticFiles(directory=settings.upload_root), name="uploads")
frontend_origins = [
    settings.frontend_origin,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
frontend_origins = [origin for origin in frontend_origins if origin]
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(fraud.router, prefix="/api/v1")
app.include_router(forecast.router, prefix="/api/v1")
app.include_router(overview.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(agent.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/health/models")
def model_health() -> dict[str, dict[str, object]]:
    registry: ModelRegistry = app.state.model_registry
    return {
        "creditcard_baseline": registry.status("creditcard_baseline"),
        "paysim_baseline": registry.status("paysim_baseline"),
    }
