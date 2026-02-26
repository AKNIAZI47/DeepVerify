"""Usage quota tracking."""
from db import db
from datetime import datetime

class UsageTracker:
    def __init__(self):
        self.collection = db["usage"]
    
    async def track_usage(self, user_id: str, resource: str):
        await self.collection.insert_one({
            "user_id": user_id,
            "resource": resource,
            "timestamp": datetime.utcnow()
        })
    
    async def get_usage(self, user_id: str, resource: str, days: int = 30) -> int:
        from datetime import timedelta
        start = datetime.utcnow() - timedelta(days=days)
        return await self.collection.count_documents({
            "user_id": user_id,
            "resource": resource,
            "timestamp": {"$gte": start}
        })
    
    async def check_quota(self, user_id: str, resource: str, limit: int) -> bool:
        usage = await self.get_usage(user_id, resource)
        return usage < limit

def get_usage_tracker() -> UsageTracker:
    return UsageTracker()
