"""Audit logging for compliance and security."""
from typing import Dict, Optional
from datetime import datetime
from db import db
import logging

logger = logging.getLogger(__name__)

class AuditLogger:
    """Logs audit events for compliance."""
    
    def __init__(self):
        self.collection = db["audit_logs"]
    
    async def log_event(self, action: str, user_id: Optional[str], 
                       resource_type: str, resource_id: Optional[str] = None,
                       details: Optional[Dict] = None, ip_address: Optional[str] = None):
        """Log audit event."""
        doc = {
            "action": action,
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address,
            "timestamp": datetime.utcnow()
        }
        await self.collection.insert_one(doc)
        logger.info(f"Audit: {action} on {resource_type} by {user_id}")
    
    async def log_data_access(self, user_id: str, resource_type: str, 
                             resource_id: str, ip_address: str):
        """Log data access."""
        await self.log_event("data_access", user_id, resource_type, 
                           resource_id, ip_address=ip_address)
    
    async def log_data_modification(self, user_id: str, resource_type: str,
                                   resource_id: str, changes: Dict, ip_address: str):
        """Log data modification."""
        await self.log_event("data_modification", user_id, resource_type,
                           resource_id, details={"changes": changes}, 
                           ip_address=ip_address)
    
    async def log_data_deletion(self, user_id: str, resource_type: str,
                               resource_id: str, ip_address: str):
        """Log data deletion."""
        await self.log_event("data_deletion", user_id, resource_type,
                           resource_id, ip_address=ip_address)

_audit_logger: Optional[AuditLogger] = None

def get_audit_logger() -> AuditLogger:
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
