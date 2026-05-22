from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    query: str = Field(default="business OR economy OR AI")
    category: str = Field(default="business")
    language: str = Field(default="en")
    page_size: int = Field(default=50, ge=1, le=100)
    from_days: int = Field(default=7, ge=1, le=30)


class IngestResponse(BaseModel):
    status: str
    message: str
    ingested_count: int = 0
    processed_count: int = 0


class TrendItem(BaseModel):
    keyword: str
    count: int


class TrendResponse(BaseModel):
    days: int
    total_keywords: int
    items: list[TrendItem]


class InsightsResponse(BaseModel):
    total_processed: int
    sentiment_distribution: dict[str, int]
    top_keywords: list[TrendItem]
    top_sources: list[dict[str, Any]]
    sample_items: list[dict[str, Any]]


class SummaryResponse(BaseModel):
    raw_count: int
    processed_count: int
    positive: int
    negative: int
    neutral: int
    avg_trend_score: float
    daily_counts: list[dict[str, Any]]
    growth_percentage: float


class SearchResponse(BaseModel):
    query: str
    page: int
    page_size: int
    total: int
    items: list[dict[str, Any]]


class ErrorResponse(BaseModel):
    detail: str
    timestamp: datetime
