from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.core.config import settings


async def fetch_news_articles(
    query: str,
    category: str,
    language: str,
    page_size: int,
    from_days: int,
) -> list[dict[str, Any]]:
    from_date = (datetime.now(timezone.utc) - timedelta(days=from_days)).date().isoformat()
    provider = settings.news_provider.lower().strip()

    if provider == "worldnewsapi":
        url = f"{settings.world_news_api_base_url}/search-news"
        params = {
            "text": query,
            "language": language,
            "earliest-publish-date": from_date,
            "number": page_size,
        }
        headers = {"x-api-key": settings.news_api_key}
    else:
        url = f"{settings.news_api_base_url}/everything"
        params = {
            "q": query,
            "language": language,
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "from": from_date,
            "apiKey": settings.news_api_key,
        }
        headers = {}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params, headers=headers)
        try:
            payload = response.json()
        except ValueError:
            payload = {}

    if response.status_code >= 400:
        error_message = payload.get("message") or payload.get("error") or response.text or "Unknown provider error"
        raise ValueError(f"News provider request failed ({response.status_code}): {error_message}")

    if provider == "worldnewsapi":
        raw_articles = payload.get("news", [])
    else:
        if payload.get("status") != "ok":
            raise ValueError(payload.get("message", "Failed to fetch from News API"))
        raw_articles = payload.get("articles", [])

    normalized: list[dict[str, Any]] = []
    for article in raw_articles:
        source = article.get("source")
        source_name = "unknown"
        if isinstance(source, dict):
            source_name = source.get("name") or source.get("title") or "unknown"
        elif isinstance(source, str) and source:
            source_name = source
        else:
            source_name = article.get("source_name") or article.get("author") or "unknown"

        published_at = article.get("publishedAt") or article.get("publish_date") or article.get("published_at")
        content = article.get("content") or article.get("text") or article.get("summary") or article.get("description") or ""
        description = article.get("description") or article.get("summary") or ""

        normalized.append(
            {
                "title": article.get("title") or "",
                "source": source_name,
                "published_at": published_at,
                "content": content,
                "description": description,
                "url": article.get("url") or "",
                "category": category,
                "ingested_at": datetime.now(timezone.utc),
            }
        )

    return normalized
