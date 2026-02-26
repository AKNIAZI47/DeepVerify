"""Stripe subscription management."""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class SubscriptionManager:
    def __init__(self, stripe_key: Optional[str] = None):
        self.stripe_key = stripe_key
    
    async def create_subscription(self, user_id: str, plan: str) -> Dict:
        logger.info(f"Creating subscription for {user_id}: {plan}")
        return {"subscription_id": "sub_mock", "status": "active"}
    
    async def cancel_subscription(self, subscription_id: str):
        logger.info(f"Cancelling subscription {subscription_id}")

def get_subscription_manager() -> SubscriptionManager:
    return SubscriptionManager()
