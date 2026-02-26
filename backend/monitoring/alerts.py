"""Alerting system for critical events."""
from typing import Dict, List, Optional
from datetime import datetime
import logging
import requests

logger = logging.getLogger(__name__)

class AlertManager:
    """Manages alerts and notifications."""
    
    def __init__(self):
        self.webhooks: List[str] = []
        self.email_recipients: List[str] = []
    
    def add_webhook(self, url: str):
        """Add webhook URL."""
        self.webhooks.append(url)
    
    async def send_alert(self, severity: str, title: str, message: str, 
                        metadata: Optional[Dict] = None):
        """Send alert."""
        alert = {
            "severity": severity,
            "title": title,
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.warning(f"ALERT [{severity}]: {title} - {message}")
        
        for webhook in self.webhooks:
            try:
                requests.post(webhook, json=alert, timeout=5)
            except Exception as e:
                logger.error(f"Failed to send alert to {webhook}: {e}")
    
    async def alert_high_error_rate(self, error_rate: float):
        """Alert on high error rate."""
        await self.send_alert(
            "critical",
            "High Error Rate Detected",
            f"Error rate: {error_rate:.1f}%",
            {"error_rate": error_rate}
        )
    
    async def alert_model_degradation(self, version: str, accuracy: float):
        """Alert on model accuracy degradation."""
        await self.send_alert(
            "warning",
            "Model Performance Degradation",
            f"Model {version} accuracy dropped to {accuracy:.1f}%",
            {"version": version, "accuracy": accuracy}
        )

_alert_manager: Optional[AlertManager] = None

def get_alert_manager() -> AlertManager:
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager
