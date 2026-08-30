from datetime import datetime, timezone

from beanie import Document, Indexed
from pydantic import BaseModel, Field


class ForecastPoint(BaseModel):
    date: datetime
    value: float
    lower_bound: float
    upper_bound: float


class Forecast(Document):
    organization_id: Indexed(str)
    metric: str
    horizon_days: int
    predicted_values: list[ForecastPoint] = Field(default_factory=list)
    model_version: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "forecasts"
