"""GDPR right to deletion."""
from db import users, history
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class DataDeleter:
    async def delete_user_data(self, user_id: str):
        await history.delete_many({"user_id": ObjectId(user_id)})
        await users.delete_one({"_id": ObjectId(user_id)})
        logger.info(f"Deleted all data for user {user_id}")

def get_data_deleter() -> DataDeleter:
    return DataDeleter()
