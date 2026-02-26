from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config.settings import get_settings

settings = get_settings()

# Create client with timeouts to prevent hanging
client = AsyncIOMotorClient(
    settings.mongo_uri,
    serverSelectionTimeoutMS=5000,  # 5 second timeout
    connectTimeoutMS=5000,
    socketTimeoutMS=5000,
)

db = client[settings.mongo_db]
users = db["users"]
history = db["history"]


def get_db() -> AsyncIOMotorDatabase:
    """Get database instance."""
    return db