from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Market Intelligence API"
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")

    mongodb_uri: str = Field(alias="MONGODB_URI")
    mongodb_db: str = Field(default="market_intel", alias="MONGODB_DB")

    news_provider: str = Field(default="newsapi", alias="NEWS_PROVIDER")
    news_api_key: str = Field(alias="NEWS_API_KEY")
    news_api_base_url: str = Field(default="https://newsapi.org/v2", alias="NEWS_API_BASE_URL")
    world_news_api_base_url: str = Field(default="https://api.worldnewsapi.com", alias="WORLD_NEWS_API_BASE_URL")

    cache_ttl_seconds: int = Field(default=300, alias="CACHE_TTL_SECONDS")
    default_page_size: int = Field(default=20, alias="DEFAULT_PAGE_SIZE")
    max_page_size: int = Field(default=100, alias="MAX_PAGE_SIZE")


settings = Settings()
