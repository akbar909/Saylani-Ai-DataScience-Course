from datetime import datetime, timezone
from typing import Literal

from beanie import Document, Indexed
from pydantic import Field


class User(Document):
    organization_id: str
    email: Indexed(str, unique=True)
    hashed_password: str
    role: Literal["owner", "admin", "member"] = "member"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"
