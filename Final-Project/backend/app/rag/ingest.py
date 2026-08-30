from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentChunk:
    text: str
    page: int | None = None
    score: float = 0.0


def extract_text(file_path: str | Path) -> str:
    """Extract plain text from .docx, .pdf, or .txt files."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".docx":
        try:
            from docx import Document  # type: ignore[import-untyped]
            doc = Document(str(path))
            return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
        except Exception as exc:
            return f"[Could not read .docx: {exc}]"

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader  # type: ignore[import-untyped]
            reader = PdfReader(str(path))
            pages: list[str] = []
            for page in reader.pages:
                text = page.extract_text() or ""
                if text.strip():
                    pages.append(text)
            return "\n".join(pages)
        except Exception as exc:
            return f"[Could not read .pdf: {exc}]"

    if suffix in {".txt", ".md", ".csv"}:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception as exc:
            return f"[Could not read file: {exc}]"

    return f"[Unsupported file type: {suffix}]"


def chunk_text(text: str, chunk_size: int = 1200) -> list[DocumentChunk]:
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    return [DocumentChunk(text=text[index : index + chunk_size]) for index in range(0, len(text), chunk_size)]
