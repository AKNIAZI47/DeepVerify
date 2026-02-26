"""GDPR data export."""
from typing import Dict
from db import users, history
from bson import ObjectId

class DataExporter:
    async def export_user_data(self, user_id: str) -> Dict:
        user = await users.find_one({"_id": ObjectId(user_id)})
        user_history = []
        async for doc in history.find({"user_id": ObjectId(user_id)}):
            doc["_id"] = str(doc["_id"])
            doc["user_id"] = str(doc["user_id"])
            user_history.append(doc)
        
        return {
            "user": {k: str(v) if isinstance(v, ObjectId) else v for k, v in user.items()},
            "history": user_history,
            "exported_at": str(__import__('datetime').datetime.utcnow())
        }

def get_data_exporter() -> DataExporter:
    return DataExporter()
