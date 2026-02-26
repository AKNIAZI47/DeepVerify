"""
ML Model performance tracking system.

This module tracks model predictions, accuracy, and performance metrics
over time to monitor model drift and quality.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import logging
from motor.motor_asyncio import AsyncIOMotorCollection
from db import db

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """
    Tracks ML model performance metrics.
    
    Records predictions, user feedback, and calculates accuracy metrics.
    """
    
    def __init__(self, collection: Optional[AsyncIOMotorCollection] = None):
        """
        Initialize performance tracker.
        
        Args:
            collection: MongoDB collection for storing metrics
        """
        self.collection = collection or db["model_performance"]
    
    async def record_prediction(
        self,
        model_version: str,
        input_text: str,
        prediction: str,
        confidence: float,
        probabilities: Dict[str, float],
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Record a model prediction.
        
        Args:
            model_version: Model version used
            input_text: Input text (hashed for privacy)
            prediction: Model prediction
            confidence: Confidence score
            probabilities: Class probabilities
            metadata: Optional metadata
            
        Returns:
            Prediction ID
        """
        import hashlib
        
        # Hash input text for privacy
        text_hash = hashlib.sha256(input_text.encode()).hexdigest()
        
        doc = {
            "model_version": model_version,
            "text_hash": text_hash,
            "text_length": len(input_text),
            "prediction": prediction,
            "confidence": confidence,
            "probabilities": probabilities,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow(),
            "feedback": None,
            "correct": None,
        }
        
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)
    
    async def record_feedback(
        self,
        prediction_id: str,
        correct: bool,
        actual_label: Optional[str] = None,
    ):
        """
        Record user feedback on a prediction.
        
        Args:
            prediction_id: Prediction ID
            correct: Whether prediction was correct
            actual_label: Actual label if prediction was wrong
        """
        from bson import ObjectId
        
        update = {
            "$set": {
                "feedback": {
                    "correct": correct,
                    "actual_label": actual_label,
                    "timestamp": datetime.utcnow(),
                }
            }
        }
        
        await self.collection.update_one(
            {"_id": ObjectId(prediction_id)},
            update
        )
        
        logger.info(f"Recorded feedback for prediction {prediction_id}: correct={correct}")
    
    async def get_accuracy(
        self,
        model_version: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """
        Calculate model accuracy from user feedback.
        
        Args:
            model_version: Filter by model version
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            Dict with accuracy metrics
        """
        query = {"feedback": {"$ne": None}}
        
        if model_version:
            query["model_version"] = model_version
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        cursor = self.collection.find(query)
        
        total = 0
        correct = 0
        
        async for doc in cursor:
            total += 1
            if doc["feedback"]["correct"]:
                correct += 1
        
        accuracy = (correct / total * 100) if total > 0 else 0.0
        
        return {
            "total_predictions": total,
            "correct_predictions": correct,
            "incorrect_predictions": total - correct,
            "accuracy": accuracy,
            "model_version": model_version,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        }
    
    async def get_confidence_distribution(
        self,
        model_version: Optional[str] = None,
        bins: int = 10,
    ) -> Dict:
        """
        Get distribution of confidence scores.
        
        Args:
            model_version: Filter by model version
            bins: Number of bins for histogram
            
        Returns:
            Dict with confidence distribution
        """
        query = {}
        if model_version:
            query["model_version"] = model_version
        
        cursor = self.collection.find(query)
        
        confidences = []
        async for doc in cursor:
            confidences.append(doc["confidence"])
        
        if not confidences:
            return {
                "bins": [],
                "counts": [],
                "mean": 0.0,
                "median": 0.0,
                "std_dev": 0.0,
            }
        
        # Calculate histogram
        bin_edges = [i / bins for i in range(bins + 1)]
        counts = [0] * bins
        
        for conf in confidences:
            bin_idx = min(int(conf * bins), bins - 1)
            counts[bin_idx] += 1
        
        return {
            "bins": bin_edges,
            "counts": counts,
            "mean": statistics.mean(confidences),
            "median": statistics.median(confidences),
            "std_dev": statistics.stdev(confidences) if len(confidences) > 1 else 0.0,
            "total_predictions": len(confidences),
        }
    
    async def get_prediction_volume(
        self,
        model_version: Optional[str] = None,
        days: int = 7,
    ) -> Dict:
        """
        Get prediction volume over time.
        
        Args:
            model_version: Filter by model version
            days: Number of days to analyze
            
        Returns:
            Dict with daily prediction counts
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = {
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }
        
        if model_version:
            query["model_version"] = model_version
        
        # Aggregate by day
        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$timestamp"
                        }
                    },
                    "count": {"$sum": 1},
                    "avg_confidence": {"$avg": "$confidence"},
                }
            },
            {"$sort": {"_id": 1}},
        ]
        
        daily_stats = {}
        async for doc in self.collection.aggregate(pipeline):
            daily_stats[doc["_id"]] = {
                "count": doc["count"],
                "avg_confidence": doc["avg_confidence"],
            }
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily_stats": daily_stats,
            "total_predictions": sum(s["count"] for s in daily_stats.values()),
        }
    
    async def get_error_analysis(
        self,
        model_version: Optional[str] = None,
        limit: int = 100,
    ) -> Dict:
        """
        Analyze incorrect predictions.
        
        Args:
            model_version: Filter by model version
            limit: Maximum number of errors to analyze
            
        Returns:
            Dict with error analysis
        """
        query = {
            "feedback.correct": False
        }
        
        if model_version:
            query["model_version"] = model_version
        
        cursor = self.collection.find(query).limit(limit)
        
        errors = []
        error_types = defaultdict(int)
        confidence_ranges = {
            "high (>80%)": 0,
            "medium (50-80%)": 0,
            "low (<50%)": 0,
        }
        
        async for doc in cursor:
            predicted = doc["prediction"]
            actual = doc["feedback"].get("actual_label", "Unknown")
            confidence = doc["confidence"]
            
            errors.append({
                "predicted": predicted,
                "actual": actual,
                "confidence": confidence,
                "timestamp": doc["timestamp"].isoformat(),
            })
            
            error_types[f"{predicted} -> {actual}"] += 1
            
            if confidence > 0.8:
                confidence_ranges["high (>80%)"] += 1
            elif confidence > 0.5:
                confidence_ranges["medium (50-80%)"] += 1
            else:
                confidence_ranges["low (<50%)"] += 1
        
        return {
            "total_errors": len(errors),
            "error_types": dict(error_types),
            "confidence_distribution": confidence_ranges,
            "recent_errors": errors[:20],  # Return 20 most recent
        }
    
    async def get_model_comparison(
        self,
        version1: str,
        version2: str,
        days: int = 7,
    ) -> Dict:
        """
        Compare performance of two model versions.
        
        Args:
            version1: First model version
            version2: Second model version
            days: Number of days to analyze
            
        Returns:
            Dict with comparison metrics
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get metrics for both versions
        metrics1 = await self.get_accuracy(version1, start_date, end_date)
        metrics2 = await self.get_accuracy(version2, start_date, end_date)
        
        conf_dist1 = await self.get_confidence_distribution(version1)
        conf_dist2 = await self.get_confidence_distribution(version2)
        
        return {
            "version1": {
                "version": version1,
                "accuracy": metrics1["accuracy"],
                "total_predictions": metrics1["total_predictions"],
                "avg_confidence": conf_dist1["mean"],
            },
            "version2": {
                "version": version2,
                "accuracy": metrics2["accuracy"],
                "total_predictions": metrics2["total_predictions"],
                "avg_confidence": conf_dist2["mean"],
            },
            "comparison": {
                "accuracy_diff": metrics2["accuracy"] - metrics1["accuracy"],
                "confidence_diff": conf_dist2["mean"] - conf_dist1["mean"],
                "better_version": version2 if metrics2["accuracy"] > metrics1["accuracy"] else version1,
            },
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days,
            },
        }


# Global performance tracker instance
_performance_tracker: Optional[PerformanceTracker] = None


def get_performance_tracker() -> PerformanceTracker:
    """
    Get global performance tracker instance.
    
    Returns:
        PerformanceTracker instance
    """
    global _performance_tracker
    
    if _performance_tracker is None:
        _performance_tracker = PerformanceTracker()
    
    return _performance_tracker
