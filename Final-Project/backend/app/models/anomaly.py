from datetime import datetime, timezone
from typing import Literal

from beanie import Document, Indexed
from pydantic import Field


class Anomaly(Document):
    organization_id: Indexed(str)
    transaction_id: str
    anomaly_score: float
    severity: Literal["low", "medium", "high"]
    reason: str
    reviewed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "anomalies"
        indexes = [
            [("organization_id", 1), ("severity", 1)],
        ]
