from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class DocumentRead(BaseModel):
    id: str
    filename: str
    status: Literal["processing", "indexed", "failed"]
    created_at: datetime
    file_url: str | None = None


class DocumentQuestion(BaseModel):
    document_id: str
    question: str


class Citation(BaseModel):
    chunk_text: str
    page: int | None = None
    score: float


class DocumentAnswer(BaseModel):
    answer: str
    citations: list[Citation]
