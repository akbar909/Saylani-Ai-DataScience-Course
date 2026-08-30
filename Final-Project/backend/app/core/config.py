from functools import lru_cache
from pathlib import Path

# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = PROJECT_ROOT.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(WORKSPACE_ROOT / ".env", PROJECT_ROOT / ".env"),
        extra="ignore",
        protected_namespaces=(),
    )

    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "ai_finance_saas"
    jwt_secret: str = ""
    frontend_origin: str = "http://localhost:3000"
    model_artifact_root: Path = PROJECT_ROOT / "ml" / "artifacts"
    upload_root: Path = PROJECT_ROOT / "uploads"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id_pro: str = "price_pro_monthly"


@lru_cache
def get_settings() -> Settings:
    return Settings()
