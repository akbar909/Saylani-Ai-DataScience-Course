from datetime import datetime, timezone
from typing import Literal

from beanie import Document, Indexed
from pydantic import Field


class Subscription(Document):
    organization_id: Indexed(str)
    stripe_subscription_id: str | None = None
    plan: Literal["starter", "pro"] = "starter"
    status: Literal["active", "past_due", "canceled"] = "active"
    current_period_end: datetime | None = None

    class Settings:
        name = "subscriptions"
