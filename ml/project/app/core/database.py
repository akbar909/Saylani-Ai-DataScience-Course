from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings


client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global client
    if client is None:
        client = AsyncIOMotorClient(settings.mongodb_uri)
    return client


def get_db() -> AsyncIOMotorDatabase:
    return get_client()[settings.mongodb_db]


async def ensure_indexes() -> None:
    db = get_db()

    await db.raw_data.create_index("url", unique=True)
    await db.raw_data.create_index("published_at")
    await db.raw_data.create_index([("title", "text"), ("content", "text")])

    await db.processed_data.create_index("raw_id", unique=True)
    await db.processed_data.create_index("processed_at")
    await db.processed_data.create_index("keywords")
    await db.processed_data.create_index("sentiment")
