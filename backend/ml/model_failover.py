"""Model failover mechanism for high availability."""
from typing import Optional, List, Dict
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ModelFailoverManager:
    """Manages model failover and fallback strategies."""
    
    def __init__(self):
        self.primary_model = None
        self.fallback_models: List = []
        self.health_checks: Dict[str, datetime] = {}
        self.failure_threshold = 3
        self.failure_counts: Dict[str, int] = {}
    
    def register_primary(self, model, version: str):
        """Register primary model."""
        self.primary_model = {"model": model, "version": version}
        self.failure_counts[version] = 0
        logger.info(f"Registered primary model: {version}")
    
    def register_fallback(self, model, version: str, priority: int = 1):
        """Register fallback model."""
        self.fallback_models.append({
            "model": model, "version": version, "priority": priority
        })
        self.fallback_models.sort(key=lambda x: x["priority"])
        self.failure_counts[version] = 0
        logger.info(f"Registered fallback model: {version} (priority: {priority})")
    
    def get_active_model(self):
        """Get currently active model (with failover)."""
        if self.primary_model and self._is_healthy(self.primary_model["version"]):
            return self.primary_model
        
        logger.warning("Primary model unhealthy, using fallback")
        for fallback in self.fallback_models:
            if self._is_healthy(fallback["version"]):
                return fallback
        
        logger.error("All models unhealthy, using primary anyway")
        return self.primary_model
    
    def record_failure(self, version: str):
        """Record model failure."""
        self.failure_counts[version] = self.failure_counts.get(version, 0) + 1
        logger.warning(f"Model {version} failure count: {self.failure_counts[version]}")
    
    def record_success(self, version: str):
        """Record model success."""
        self.failure_counts[version] = max(0, self.failure_counts.get(version, 0) - 1)
        self.health_checks[version] = datetime.utcnow()
    
    def _is_healthy(self, version: str) -> bool:
        """Check if model is healthy."""
        failures = self.failure_counts.get(version, 0)
        if failures >= self.failure_threshold:
            last_check = self.health_checks.get(version)
            if last_check and datetime.utcnow() - last_check < timedelta(minutes=5):
                return False
        return True
    
    def get_status(self) -> Dict:
        """Get failover status."""
        return {
            "primary": self.primary_model["version"] if self.primary_model else None,
            "fallbacks": [f["version"] for f in self.fallback_models],
            "health": {v: self._is_healthy(v) for v in self.failure_counts.keys()},
            "failures": self.failure_counts
        }

_failover_manager: Optional[ModelFailoverManager] = None

def get_failover_manager() -> ModelFailoverManager:
    global _failover_manager
    if _failover_manager is None:
        _failover_manager = ModelFailoverManager()
    return _failover_manager
