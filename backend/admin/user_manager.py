"""Admin user management."""
from db import users
from bson import ObjectId
from typing import List, Dict

class UserManager:
    async def list_users(self, skip: int = 0, limit: int = 50) -> List[Dict]:
        cursor = users.find().skip(skip).limit(limit)
        result = []
        async for user in cursor:
            user["_id"] = str(user["_id"])
            result.append(user)
        return result
    
    async def update_user_role(self, user_id: str, role: str):
        await users.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": role}})
    
    async def ban_user(self, user_id: str):
        await users.update_one({"_id": ObjectId(user_id)}, {"$set": {"banned": True}})

def get_user_manager() -> UserManager:
    return UserManager()
