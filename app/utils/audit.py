"""Audit logging utilities"""
from app import db
from app.models import AuditLog
from flask import request
import logging

logger = logging.getLogger(__name__)


def log_audit(user_id, action, details=None):
    """Log an audit event
    
    Args:
        user_id (int): ID of the user performing the action
        action (str): Action being performed
        details (str): Additional details about the action
    """
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=request.remote_addr if request else None
        )
        db.session.add(audit_log)
        db.session.commit()
        logger.info(f"Audit: User {user_id} - {action}")
    except Exception as e:
        logger.error(f"Failed to log audit: {str(e)}")
        db.session.rollback()
