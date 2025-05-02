"""Admin service for handling admin operations."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.admin import AdminLog, AdminLogType
from app.models.user import User
from app.services.notification import NotificationService


class AdminService:
    """Service for handling admin operations."""

    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)

    async def log_admin_action(
        self,
        admin: User,
        action_type: AdminLogType,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
    ) -> AdminLog:
        """Log an admin action."""
        admin_log = AdminLog(
            admin_id=admin.id,
            type=action_type,
            action=action,
            details=json.dumps(details) if details else None,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
        )
        self.db.add(admin_log)
        self.db.commit()
        self.db.refresh(admin_log)
        return admin_log

    async def get_admin_logs(
        self,
        admin_id: Optional[int] = None,
        action_type: Optional[AdminLogType] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[AdminLog]:
        """Get admin logs with optional filtering."""
        query = self.db.query(AdminLog)
        if admin_id:
            query = query.filter(AdminLog.admin_id == admin_id)
        if action_type:
            query = query.filter(AdminLog.type == action_type)
        return query.order_by(AdminLog.created_at.desc()).offset(offset).limit(limit).all()

    async def notify_system_error(
        self,
        error_message: str,
        error_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send system error notification to admins."""
        admins = self.db.query(User).filter(User.is_admin == True).all()
        for admin in admins:
            await self.notification_service.create_notification(
                user=admin,
                notification_type=NotificationType.ERROR,
                title="System Error",
                message=error_message,
                data=error_details,
            )

    async def override_content_status(
        self,
        admin: User,
        content_id: int,
        new_status: str,
        reason: str,
        request: Optional[Request] = None,
    ) -> None:
        """Override content status manually."""
        # Log the override action
        await self.log_admin_action(
            admin=admin,
            action_type=AdminLogType.CONTENT_OVERRIDE,
            action=f"Override content {content_id} status to {new_status}",
            details={"content_id": content_id, "new_status": new_status, "reason": reason},
            request=request,
        )

        # TODO: Implement actual content status override logic
        # This would involve updating the content status in the database
        # and potentially triggering notifications to content owners

    async def manage_user(
        self,
        admin: User,
        user_id: int,
        action: str,
        details: Dict[str, Any],
        request: Optional[Request] = None,
    ) -> None:
        """Manage user account (suspend, activate, etc.)."""
        # Log the user management action
        await self.log_admin_action(
            admin=admin,
            action_type=AdminLogType.USER_MANAGEMENT,
            action=f"{action} user {user_id}",
            details=details,
            request=request,
        )

        # TODO: Implement actual user management logic
        # This would involve updating user status, permissions, etc. 