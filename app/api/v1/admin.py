"""Admin API endpoints."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.admin import AdminLog, AdminLogType
from app.models.user import User
from app.schemas.admin import AdminLogResponse, ContentOverrideRequest, UserManagementRequest
from app.services.admin import AdminService

router = APIRouter()


@router.get("/logs", response_model=List[AdminLogResponse])
async def get_admin_logs(
    admin_id: Optional[int] = None,
    action_type: Optional[AdminLogType] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> List[AdminLog]:
    """Get admin logs."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    admin_service = AdminService(db)
    return await admin_service.get_admin_logs(
        admin_id=admin_id,
        action_type=action_type,
        limit=limit,
        offset=offset,
    )


@router.post("/content/override")
async def override_content_status(
    content_override: ContentOverrideRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
    request: Request = None,
) -> Dict[str, Any]:
    """Override content status manually."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    admin_service = AdminService(db)
    await admin_service.override_content_status(
        admin=current_user,
        content_id=content_override.content_id,
        new_status=content_override.new_status,
        reason=content_override.reason,
        request=request,
    )
    return {"message": "Content status overridden successfully"}


@router.post("/users/manage")
async def manage_user(
    user_management: UserManagementRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
    request: Request = None,
) -> Dict[str, Any]:
    """Manage user account."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    admin_service = AdminService(db)
    await admin_service.manage_user(
        admin=current_user,
        user_id=user_management.user_id,
        action=user_management.action,
        details=user_management.details,
        request=request,
    )
    return {"message": "User management action completed successfully"} 