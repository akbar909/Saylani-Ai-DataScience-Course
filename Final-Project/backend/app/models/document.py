from datetime import datetime, timezone
from typing import Literal

from beanie import Document, Indexed
from pydantic import Field


class UploadedDocument(Document):
    organization_id: Indexed(str)
    filename: str
    file_url: str
    status: Literal["processing", "indexed", "failed"] = "processing"
    vector_namespace: str | None = None
    file_path: str | None = None
    uploaded_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "documents"
