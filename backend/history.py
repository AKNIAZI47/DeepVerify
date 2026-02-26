from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from pydantic import BaseModel
from db import history
from dependencies import get_current_user

router = APIRouter(prefix="/api/v1/history", tags=["history"])

@router.get("")
async def list_history(user: dict = Depends(get_current_user), limit: int = 20, skip: int = 0):
    cursor = history.find({"user_id": user["_id"]}).sort("_id", -1).skip(skip).limit(limit)
    items = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["user_id"] = str(doc["user_id"])
        items.append(doc)
    return items

class ReviewPayload(BaseModel):
    history_id: str
    correct: bool

@router.post("/review")
async def review_entry(payload: ReviewPayload, user: dict = Depends(get_current_user)):
    try:
        hid = ObjectId(payload.history_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid history_id")
    doc = await history.find_one({"_id": hid, "user_id": user["_id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    await history.update_one(
        {"_id": hid},
        {"$set": {"reviewed": True, "correct": payload.correct}}
    )
    return {"status": "ok"}