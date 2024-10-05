from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# Global variable to store the database client
client = None
db = None


async def init_db():
    """Initialize MongoDB connection."""
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    await client.server_info()
    print("Connected to MongoDB")


async def close_db():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        print("MongoDB connection closed")


async def get_db():
    return db
