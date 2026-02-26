"""Webhook management system."""
from typing import Dict, List, Optional
from datetime import datetime
from db import db
import requests
import logging

logger = logging.getLogger(__name__)

class WebhookManager:
    """Manages webhook subscriptions and delivery."""
    
    def __init__(self):
        self.collection = db["webhooks"]
        self.deliveries = db["webhook_deliveries"]
    
    async def create_webhook(self, user_id: str, url: str, events: List[str],
                            secret: Optional[str] = None) -> str:
        """Create webhook subscription."""
        doc = {
            "user_id": user_id,
            "url": url,
            "events": events,
            "secret": secret,
            "active": True,
            "created_at": datetime.utcnow()
        }
        result = await self.collection.insert_one(doc)
        logger.info(f"Created webhook for user {user_id}")
        return str(result.inserted_id)
    
    async def trigger_webhook(self, event_type: str, payload: Dict):
        """Trigger webhooks for event."""
        cursor = self.collection.find({"events": event_type, "active": True})
        
        async for webhook in cursor:
            try:
                response = requests.post(
                    webhook["url"],
                    json={"event": event_type, "data": payload},
                    headers={"X-Webhook-Secret": webhook.get("secret", "")},
                    timeout=10
                )
                
                await self.deliveries.insert_one({
                    "webhook_id": webhook["_id"],
                    "event_type": event_type,
                    "status_code": response.status_code,
                    "success": response.status_code < 400,
                    "timestamp": datetime.utcnow()
                })
                
                logger.info(f"Webhook delivered: {event_type} to {webhook['url']}")
            except Exception as e:
                logger.error(f"Webhook delivery failed: {e}")
                await self.deliveries.insert_one({
                    "webhook_id": webhook["_id"],
                    "event_type": event_type,
                    "error": str(e),
                    "success": False,
                    "timestamp": datetime.utcnow()
                })

_webhook_manager: Optional[WebhookManager] = None

def get_webhook_manager() -> WebhookManager:
    global _webhook_manager
    if _webhook_manager is None:
        _webhook_manager = WebhookManager()
    return _webhook_manager
