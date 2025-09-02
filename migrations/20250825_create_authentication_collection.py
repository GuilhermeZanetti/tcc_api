import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from src.config import settings

async def run_migration():
    """
    Creates the 'authentication' collection and an index on 'hashed_api_key'.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]
    collection = db["authentication"]

    # Create index on hashed_api_key for efficient lookups
    await collection.create_index("hashed_api_key", unique=True)
    print("Migration successful: 'authentication' collection and index created.")

if __name__ == "__main__":
    asyncio.run(run_migration())
