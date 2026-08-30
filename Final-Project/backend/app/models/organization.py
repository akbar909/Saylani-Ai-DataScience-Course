from datetime import datetime, timezone
from typing import Literal

from beanie import Document
from pydantic import Field


class Organization(Document):
    name: str
    plan: Literal["starter", "pro"] = "starter"
    stripe_customer_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "organizations"
