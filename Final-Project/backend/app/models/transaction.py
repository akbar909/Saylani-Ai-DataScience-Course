from datetime import datetime, timezone

from beanie import Document, Indexed
from pydantic import Field


class Transaction(Document):
    organization_id: Indexed(str)
    amount: float
    currency: str = "USD"
    category: str
    description: str = ""
    transaction_date: datetime
    source: str = "manual"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "transactions"
        indexes = [
            [("organization_id", 1), ("transaction_date", -1)],
        ]
