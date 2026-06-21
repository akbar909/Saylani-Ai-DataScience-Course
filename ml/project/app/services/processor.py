from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from app.core.database import get_db
from app.utils.text import extract_keywords, sentiment_label


def _compute_trend_score(sentiment: str, sentiment_score: float, keyword_count: int) -> float:
    sentiment_boost = {"positive": 1.1, "neutral": 1.0, "negative": 0.9}.get(sentiment, 1.0)
    return round((keyword_count * 1.5 + abs(sentiment_score) * 100) * sentiment_boost, 2)


async def store_raw_articles(articles: list[dict[str, Any]]) -> int:
    db = get_db()
    inserted = 0

    for article in articles:
        if not article.get("url"):
            continue

        result = await db.raw_data.update_one(
            {"url": article["url"]},
            {"$setOnInsert": article},
            upsert=True,
        )
        if result.upserted_id is not None:
            inserted += 1

    return inserted


async def process_recent_raw_data(limit: int = 200) -> int:
    db = get_db()

    cursor = db.raw_data.find({}, sort=[("ingested_at", -1)]).limit(limit)
    raw_docs = await cursor.to_list(length=limit)
    processed_count = 0

    for raw in raw_docs:
        text = f"{raw.get('title', '')} {raw.get('content', '')}"
        keywords = extract_keywords(text)
        sentiment, score = sentiment_label(text)
        trend_score = _compute_trend_score(sentiment, score, len(keywords))

        processed_doc = {
            "raw_id": raw.get("_id"),
            "title": raw.get("title", ""),
            "source": raw.get("source", "unknown"),
            "published_at": raw.get("published_at"),
            "content": raw.get("content", ""),
            "category": raw.get("category", "general"),
            "keywords": keywords,
            "sentiment": sentiment,
            "score": round(score, 4),
            "trend_score": trend_score,
            "processed_at": datetime.now(timezone.utc),
        }

        result = await db.processed_data.update_one(
            {"raw_id": raw.get("_id")},
            {"$set": processed_doc},
            upsert=True,
        )

        if result.modified_count > 0 or result.upserted_id is not None:
            processed_count += 1

    return processed_count


def serialize_mongo_doc(doc: dict[str, Any]) -> dict[str, Any]:
    serialized: dict[str, Any] = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            serialized[key] = str(value)
        else:
            serialized[key] = value
    return serialized
