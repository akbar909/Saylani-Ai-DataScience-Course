"""Gemini-powered document Q&A via the google-generativeai SDK."""
from __future__ import annotations

# pyrefly: ignore [missing-import]
import httpx

from app.core.config import get_settings
from app.rag.retriever import Retriever


async def answer_question(question: str, retriever: Retriever) -> dict[str, object]:
    sources = retriever.search(question, limit=6)
    settings = get_settings()

    context = "\n\n---\n\n".join(s.text for s in sources if s.text.strip())
    citations = [{"chunk_text": s.text, "page": s.page, "score": round(s.score, 4)} for s in sources]

    if not settings.gemini_api_key:
        # Fallback: return best-matching chunk as answer
        answer = sources[0].text if sources else "No relevant content found in the document."
        return {"answer": answer, "citations": citations}

    # Call Gemini REST API
    prompt = (
        f"You are a helpful financial document assistant. "
        f"Answer the following question based ONLY on the document context provided below. "
        f"If the context does not contain the answer, say so clearly.\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        f"ANSWER:"
    )
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024},
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            answer = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as exc:
        answer = f"Gemini could not generate a response: {exc}"

    return {"answer": answer, "citations": citations}
