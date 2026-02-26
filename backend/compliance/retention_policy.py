"""Data retention policy."""
from datetime import datetime, timedelta
from db import history
import logging

logger = logging.getLogger(__name__)

class RetentionPolicy:
    def __init__(self, retention_days: int = 365):
        self.retention_days = retention_days
    
    async def cleanup_old_data(self):
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        result = await history.delete_many({"timestamp": {"$lt": cutoff}})
        logger.info(f"Deleted {result.deleted_count} old records")
        return result.deleted_count

def get_retention_policy() -> RetentionPolicy:
    return RetentionPolicy()
