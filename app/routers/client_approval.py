"""Client approval router for handling content approvals."""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.auth import get_current_user
from ..core.database import get_db
from ..models.collaboration import ApprovalStatus, ClientApproval
from ..models.content import Content
from ..models.user import User, UserRole
from ..schemas.client_approval import (
    ClientApprovalCreate,
    ClientApprovalResponse,
    ClientApprovalUpdate,
)

router = APIRouter(prefix="/client-approvals", tags=["client-approvals"])


@router.post("", response_model=ClientApprovalResponse)
async def create_client_approval(
    approval: ClientApprovalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientApprovalResponse:
    """Create a new client approval request."""
    # Verify the content exists
    content = db.query(Content).filter(Content.id == approval.content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found",
        )

    # Verify the client exists and has the correct role
    client = db.query(User).filter(
        User.id == approval.client_id,
        User.role == UserRole.CLIENT,
    ).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found or invalid role",
        )

    # Create the approval
    db_approval = ClientApproval(
        content_id=approval.content_id,
        client_id=approval.client_id,
        agency_id=current_user.id,
        status=ApprovalStatus.PENDING,
        is_urgent=approval.is_urgent,
        deadline=datetime.utcnow() + timedelta(days=approval.deadline_days),
    )
    db.add(db_approval)
    db.commit()
    db.refresh(db_approval)

    return ClientApprovalResponse.from_orm(db_approval)


@router.get("", response_model=List[ClientApprovalResponse])
async def list_client_approvals(
    status: Optional[ApprovalStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ClientApprovalResponse]:
    """List client approvals."""
    query = db.query(ClientApproval)

    if current_user.role == UserRole.CLIENT:
        query = query.filter(ClientApproval.client_id == current_user.id)
    else:
        query = query.filter(ClientApproval.agency_id == current_user.id)

    if status:
        query = query.filter(ClientApproval.status == status)

    approvals = query.all()
    return [ClientApprovalResponse.from_orm(approval) for approval in approvals]


@router.get("/{approval_id}", response_model=ClientApprovalResponse)
async def get_client_approval(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientApprovalResponse:
    """Get a specific client approval."""
    approval = db.query(ClientApproval).filter(ClientApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found",
        )

    # Check permissions
    if current_user.role != UserRole.CLIENT and approval.agency_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this approval",
        )

    return ClientApprovalResponse.from_orm(approval)


@router.patch("/{approval_id}", response_model=ClientApprovalResponse)
async def update_client_approval(
    approval_id: int,
    approval_update: ClientApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientApprovalResponse:
    """Update a client approval."""
    approval = db.query(ClientApproval).filter(ClientApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found",
        )

    # Check permissions
    if current_user.role != UserRole.CLIENT and approval.agency_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this approval",
        )

    # Update fields
    for field, value in approval_update.dict(exclude_unset=True).items():
        setattr(approval, field, value)

    db.commit()
    db.refresh(approval)

    return ClientApprovalResponse.from_orm(approval) 