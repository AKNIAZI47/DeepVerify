"""
Database index creation script.

This script creates indexes on MongoDB collections to improve query performance.
Run this script during deployment or database setup.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_indexes():
    """Create database indexes for optimal query performance."""
    settings = get_settings()
    
    logger.info(f"Connecting to MongoDB: {settings.mongo_uri}")
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db]
    
    try:
        # Users collection indexes
        logger.info("Creating indexes on 'users' collection...")
        users = db["users"]
        
        # Email index (unique, for login/signup)
        await users.create_index("email", unique=True, name="idx_users_email")
        logger.info("  ✓ Created unique index on email")
        
        # Created at index (for sorting/filtering)
        await users.create_index("created_at", name="idx_users_created_at")
        logger.info("  ✓ Created index on created_at")
        
        # Lockout index (for checking locked accounts)
        await users.create_index("locked_until", name="idx_users_locked_until")
        logger.info("  ✓ Created index on locked_until")
        
        # History collection indexes
        logger.info("Creating indexes on 'history' collection...")
        history = db["history"]
        
        # User ID index (for fetching user's history)
        await history.create_index("user_id", name="idx_history_user_id")
        logger.info("  ✓ Created index on user_id")
        
        # Compound index for user queries (user_id + _id descending for pagination)
        await history.create_index(
            [("user_id", 1), ("_id", -1)],
            name="idx_history_user_id_id_desc"
        )
        logger.info("  ✓ Created compound index on user_id + _id (desc)")
        
        # Verdict index (for statistics)
        await history.create_index("verdict", name="idx_history_verdict")
        logger.info("  ✓ Created index on verdict")
        
        # Reviewed index (for filtering reviewed entries)
        await history.create_index("reviewed", name="idx_history_reviewed")
        logger.info("  ✓ Created index on reviewed")
        
        # Compound index for reviewed + correct (for statistics)
        await history.create_index(
            [("reviewed", 1), ("correct", 1)],
            name="idx_history_reviewed_correct"
        )
        logger.info("  ✓ Created compound index on reviewed + correct")
        
        # List all indexes
        logger.info("\nUsers collection indexes:")
        async for index in users.list_indexes():
            logger.info(f"  - {index['name']}: {index.get('key', {})}")
        
        logger.info("\nHistory collection indexes:")
        async for index in history.list_indexes():
            logger.info(f"  - {index['name']}: {index.get('key', {})}")
        
        logger.info("\n✅ All indexes created successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error creating indexes: {e}", exc_info=True)
        raise
    
    finally:
        client.close()


async def drop_indexes():
    """Drop all custom indexes (for testing/reset)."""
    settings = get_settings()
    
    logger.info(f"Connecting to MongoDB: {settings.mongo_uri}")
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db]
    
    try:
        logger.info("Dropping custom indexes...")
        
        users = db["users"]
        history = db["history"]
        
        # Drop all indexes except _id (which is automatic)
        await users.drop_indexes()
        await history.drop_indexes()
        
        logger.info("✅ All custom indexes dropped!")
        
    except Exception as e:
        logger.error(f"❌ Error dropping indexes: {e}", exc_info=True)
        raise
    
    finally:
        client.close()


async def show_indexes():
    """Show all current indexes."""
    settings = get_settings()
    
    logger.info(f"Connecting to MongoDB: {settings.mongo_uri}")
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db]
    
    try:
        users = db["users"]
        history = db["history"]
        
        logger.info("\nUsers collection indexes:")
        async for index in users.list_indexes():
            logger.info(f"  - {index['name']}: {index.get('key', {})}")
        
        logger.info("\nHistory collection indexes:")
        async for index in history.list_indexes():
            logger.info(f"  - {index['name']}: {index.get('key', {})}")
        
    except Exception as e:
        logger.error(f"❌ Error showing indexes: {e}", exc_info=True)
        raise
    
    finally:
        client.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            asyncio.run(create_indexes())
        elif command == "drop":
            asyncio.run(drop_indexes())
        elif command == "show":
            asyncio.run(show_indexes())
        else:
            print("Usage: python create_indexes.py [create|drop|show]")
            sys.exit(1)
    else:
        # Default: create indexes
        asyncio.run(create_indexes())
