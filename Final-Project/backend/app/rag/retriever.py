from app.rag.ingest import DocumentChunk


class Retriever:
    def __init__(self, chunks: list[DocumentChunk] | None = None) -> None:
        self.chunks = chunks or []

    def search(self, query: str, limit: int = 5) -> list[DocumentChunk]:
        terms = set(query.lower().split())
        def _score(chunk: DocumentChunk) -> float:
            return len(terms.intersection(chunk.text.lower().split())) / max(len(terms), 1)
        scored = sorted(self.chunks, key=_score, reverse=True)
        return [DocumentChunk(text=c.text, page=c.page, score=_score(c)) for c in scored[:limit]]
