from datetime import datetime, timezone

from beanie import Document, Indexed
from pydantic import Field


class AgentLog(Document):
    organization_id: Indexed(str)
    action_type: str
    description: str
    metadata: dict[str, object] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "agentLogs"
        indexes = [[("organization_id", 1), ("created_at", -1)]]
