"""Content moderation tools."""
from db import db
from datetime import datetime
from typing import List, Dict

class ContentModerator:
    def __init__(self):
        self.queue = db["moderation_queue"]
    
    async def flag_content(self, content_id: str, reason: str, reporter_id: str):
        await self.queue.insert_one({
            "content_id": content_id,
            "reason": reason,
            "reporter_id": reporter_id,
            "status": "pending",
            "created_at": datetime.utcnow()
        })
    
    async def get_queue(self, status: str = "pending") -> List[Dict]:
        cursor = self.queue.find({"status": status})
        return [doc async for doc in cursor]
    
    async def resolve(self, queue_id: str, action: str, moderator_id: str):
        await self.queue.update_one(
            {"_id": queue_id},
            {"$set": {"status": "resolved", "action": action, "moderator_id": moderator_id}}
        )

def get_content_moderator() -> ContentModerator:
    return ContentModerator()
