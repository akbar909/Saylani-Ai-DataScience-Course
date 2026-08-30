from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AnomalyRead(BaseModel):
    id: str
    transaction_id: str
    anomaly_score: float = Field(ge=0, le=1)
    severity: Literal["low", "medium", "high"]
    reason: str
    reviewed: bool
    created_at: datetime
