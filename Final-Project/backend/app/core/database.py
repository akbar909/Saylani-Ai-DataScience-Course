from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import Settings
from app.models.anomaly import Anomaly
from app.models.agent_log import AgentLog
from app.models.document import UploadedDocument
from app.models.forecast import Forecast
from app.models.organization import Organization
from app.models.subscription import Subscription
from app.models.transaction import Transaction
from app.models.user import User


async def init_database(settings: Settings) -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(settings.mongodb_url)
    await init_beanie(
        database=client[settings.mongodb_database],
        document_models=[Organization, User, Transaction, Forecast, Anomaly, UploadedDocument, AgentLog, Subscription],
    )
    return client
