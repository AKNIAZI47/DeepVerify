"""Analytics tracking system."""
from typing import Dict, Optional
from datetime import datetime
from db import db
import logging

logger = logging.getLogger(__name__)

class AnalyticsTracker:
    """Tracks user analytics and events."""
    
    def __init__(self):
        self.collection = db["analytics_events"]
    
    async def track_event(self, event_type: str, user_id: Optional[str] = None, 
                         properties: Optional[Dict] = None):
        """Track analytics event."""
        doc = {
            "event_type": event_type,
            "user_id": user_id,
            "properties": properties or {},
            "timestamp": datetime.utcnow()
        }
        await self.collection.insert_one(doc)
        logger.debug(f"Tracked event: {event_type}")
    
    async def track_page_view(self, page: str, user_id: Optional[str] = None):
        """Track page view."""
        await self.track_event("page_view", user_id, {"page": page})
    
    async def track_analysis(self, user_id: Optional[str], verdict: str, confidence: float):
        """Track analysis event."""
        await self.track_event("analysis", user_id, {
            "verdict": verdict, "confidence": confidence
        })
    
    async def get_event_count(self, event_type: str, days: int = 7) -> int:
        """Get event count."""
        from datetime import timedelta
        start = datetime.utcnow() - timedelta(days=days)
        return await self.collection.count_documents({
            "event_type": event_type, "timestamp": {"$gte": start}
        })

_analytics: Optional[AnalyticsTracker] = None

def get_analytics() -> AnalyticsTracker:
    global _analytics
    if _analytics is None:
        _analytics = AnalyticsTracker()
    return _analytics
