from fastapi import APIRouter
from db import users, history

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])

@router.get("")
async def global_stats():
    total_users = await users.count_documents({})
    total_analyses = await history.count_documents({})
    total_real = await history.count_documents({"verdict": {"$regex": "AUTHENTIC|Real", "$options": "i"}})
    total_fake = await history.count_documents({"verdict": {"$regex": "QUESTIONABLE|Fake", "$options": "i"}})
    total_uncertain = await history.count_documents({"verdict": {"$regex": "Uncertain", "$options": "i"}})
    total_reviews = await history.count_documents({"reviewed": True})
    correct_votes = await history.count_documents({"reviewed": True, "correct": True})
    return {
        "total_users": total_users,
        "total_analyses": total_analyses,
        "total_real": total_real,
        "total_fake": total_fake,
        "total_uncertain": total_uncertain,
        "total_reviews": total_reviews,
        "correct_votes": correct_votes,
    }