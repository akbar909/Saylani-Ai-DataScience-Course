from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.database import get_db
from app.services.processor import serialize_mongo_doc


async def get_trending_keywords(days: int = 7, page: int = 1, page_size: int = 20) -> tuple[int, list[dict[str, Any]]]:
    db = get_db()
    since = datetime.now(timezone.utc) - timedelta(days=days)

    pipeline = [
        {"$match": {"processed_at": {"$gte": since}}},
        {"$unwind": "$keywords"},
        {"$group": {"_id": "$keywords", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]

    all_items = await db.processed_data.aggregate(pipeline).to_list(length=1000)
    total = len(all_items)
    start = (page - 1) * page_size
    end = start + page_size

    items = [{"keyword": x["_id"], "count": x["count"]} for x in all_items[start:end]]
    return total, items


async def get_insights(page: int = 1, page_size: int = 10) -> dict[str, Any]:
    db = get_db()

    total_processed = await db.processed_data.count_documents({})

    sentiment_pipeline = [
        {"$group": {"_id": "$sentiment", "count": {"$sum": 1}}}
    ]
    sentiments = await db.processed_data.aggregate(sentiment_pipeline).to_list(length=10)
    sentiment_distribution = {item["_id"]: item["count"] for item in sentiments}

    top_keywords_pipeline = [
        {"$unwind": "$keywords"},
        {"$group": {"_id": "$keywords", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    top_keywords_raw = await db.processed_data.aggregate(top_keywords_pipeline).to_list(length=10)
    top_keywords = [{"keyword": item["_id"], "count": item["count"]} for item in top_keywords_raw]

    top_sources_pipeline = [
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    top_sources_raw = await db.processed_data.aggregate(top_sources_pipeline).to_list(length=10)
    top_sources = [{"source": item["_id"], "count": item["count"]} for item in top_sources_raw]

    start = (page - 1) * page_size
    sample_cursor = db.processed_data.find({}, sort=[("processed_at", -1)]).skip(start).limit(page_size)
    sample_items_raw = await sample_cursor.to_list(length=page_size)
    sample_items = [serialize_mongo_doc(doc) for doc in sample_items_raw]

    return {
        "total_processed": total_processed,
        "sentiment_distribution": {
            "positive": sentiment_distribution.get("positive", 0),
            "negative": sentiment_distribution.get("negative", 0),
            "neutral": sentiment_distribution.get("neutral", 0),
        },
        "top_keywords": top_keywords,
        "top_sources": top_sources,
        "sample_items": sample_items,
    }


async def get_summary(days: int = 7) -> dict[str, Any]:
    db = get_db()

    raw_count = await db.raw_data.count_documents({})
    processed_count = await db.processed_data.count_documents({})

    sentiment_counts = {
        "positive": await db.processed_data.count_documents({"sentiment": "positive"}),
        "negative": await db.processed_data.count_documents({"sentiment": "negative"}),
        "neutral": await db.processed_data.count_documents({"sentiment": "neutral"}),
    }

    avg_result = await db.processed_data.aggregate(
        [{"$group": {"_id": None, "avg": {"$avg": "$trend_score"}}}]
    ).to_list(length=1)
    avg_trend_score = round((avg_result[0]["avg"] if avg_result else 0.0) or 0.0, 2)

    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    daily_pipeline = [
        {"$match": {"processed_at": {"$gte": start_date}}},
        {
            "$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$processed_at"}
                },
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    daily_counts_raw = await db.processed_data.aggregate(daily_pipeline).to_list(length=days + 1)
    daily_counts = [{"date": item["_id"], "count": item["count"]} for item in daily_counts_raw]

    half = max(days // 2, 1)
    now = datetime.now(timezone.utc)
    prev_start = now - timedelta(days=days)
    prev_end = now - timedelta(days=half)
    curr_start = now - timedelta(days=half)

    prev_count = await db.processed_data.count_documents({"processed_at": {"$gte": prev_start, "$lt": prev_end}})
    curr_count = await db.processed_data.count_documents({"processed_at": {"$gte": curr_start}})

    growth_percentage = 0.0
    if prev_count > 0:
        growth_percentage = round(((curr_count - prev_count) / prev_count) * 100, 2)

    return {
        "raw_count": raw_count,
        "processed_count": processed_count,
        "positive": sentiment_counts["positive"],
        "negative": sentiment_counts["negative"],
        "neutral": sentiment_counts["neutral"],
        "avg_trend_score": avg_trend_score,
        "daily_counts": daily_counts,
        "growth_percentage": growth_percentage,
    }


async def search_data(query: str, page: int, page_size: int) -> tuple[int, list[dict[str, Any]]]:
    db = get_db()

    filter_query = {
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"content": {"$regex": query, "$options": "i"}},
            {"keywords": {"$regex": query, "$options": "i"}},
            {"source": {"$regex": query, "$options": "i"}},
        ]
    }

    total = await db.processed_data.count_documents(filter_query)

    start = (page - 1) * page_size
    cursor = db.processed_data.find(filter_query, sort=[("processed_at", -1)]).skip(start).limit(page_size)
    docs = await cursor.to_list(length=page_size)

    return total, [serialize_mongo_doc(doc) for doc in docs]
