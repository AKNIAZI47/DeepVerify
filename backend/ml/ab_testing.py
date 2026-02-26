"""A/B testing framework for ML models."""
from typing import Dict, Optional
from datetime import datetime
import random
import hashlib
from db import db
import logging

logger = logging.getLogger(__name__)

class ABTestManager:
    """Manages A/B tests for model versions."""
    
    def __init__(self):
        self.collection = db["ab_tests"]
        self.assignments = db["ab_assignments"]
    
    async def create_test(self, name: str, version_a: str, version_b: str, 
                         traffic_split: float = 0.5, metadata: Optional[Dict] = None) -> str:
        """Create new A/B test."""
        doc = {
            "name": name,
            "version_a": version_a,
            "version_b": version_b,
            "traffic_split": traffic_split,
            "metadata": metadata or {},
            "active": True,
            "created_at": datetime.utcnow(),
            "metrics": {"a": {"count": 0, "correct": 0}, "b": {"count": 0, "correct": 0}}
        }
        result = await self.collection.insert_one(doc)
        logger.info(f"Created A/B test: {name}")
        return str(result.inserted_id)
    
    async def assign_variant(self, test_id: str, user_id: str) -> str:
        """Assign user to variant (A or B)."""
        existing = await self.assignments.find_one({"test_id": test_id, "user_id": user_id})
        if existing:
            return existing["variant"]
        
        test = await self.collection.find_one({"_id": test_id})
        hash_val = int(hashlib.md5(f"{test_id}{user_id}".encode()).hexdigest(), 16)
        variant = "a" if (hash_val % 100) < (test["traffic_split"] * 100) else "b"
        
        await self.assignments.insert_one({
            "test_id": test_id, "user_id": user_id, "variant": variant,
            "assigned_at": datetime.utcnow()
        })
        return variant
    
    async def record_result(self, test_id: str, variant: str, correct: bool):
        """Record test result."""
        await self.collection.update_one(
            {"_id": test_id},
            {"$inc": {f"metrics.{variant}.count": 1, 
                     f"metrics.{variant}.correct": 1 if correct else 0}}
        )
    
    async def get_results(self, test_id: str) -> Dict:
        """Get A/B test results."""
        test = await self.collection.find_one({"_id": test_id})
        if not test:
            return {}
        
        metrics_a = test["metrics"]["a"]
        metrics_b = test["metrics"]["b"]
        
        acc_a = (metrics_a["correct"] / metrics_a["count"] * 100) if metrics_a["count"] > 0 else 0
        acc_b = (metrics_b["correct"] / metrics_b["count"] * 100) if metrics_b["count"] > 0 else 0
        
        return {
            "name": test["name"],
            "version_a": {"version": test["version_a"], "accuracy": acc_a, "count": metrics_a["count"]},
            "version_b": {"version": test["version_b"], "accuracy": acc_b, "count": metrics_b["count"]},
            "winner": test["version_a"] if acc_a > acc_b else test["version_b"],
            "confidence": abs(acc_a - acc_b)
        }

_ab_manager: Optional[ABTestManager] = None

def get_ab_manager() -> ABTestManager:
    global _ab_manager
    if _ab_manager is None:
        _ab_manager = ABTestManager()
    return _ab_manager
