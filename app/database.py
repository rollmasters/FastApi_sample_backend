
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


# Global variable to store the database client
client = None
db = None
db_spatial_ai =None



async def init_db():
    """Initialize MongoDB connection."""
    global client, db, db_spatial_ai
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    db_spatial_ai = client[settings.MONGODB_DB_NAME_SPETIAL_AI]
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

async def get_db_spatial_ai():
    return db_spatial_ai


