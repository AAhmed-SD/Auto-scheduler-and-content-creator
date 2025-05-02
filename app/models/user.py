"""User model for the application."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel
from .enums import UserRole


class User(BaseModel):
    """User model representing application users."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Direct relationships
    created_content = relationship("Content", back_populates="creator")
    created_comments = relationship("Comment", back_populates="creator")
    assigned_tasks = relationship(
        "Task", foreign_keys="Task.assignee_id", back_populates="assignee"
    )
    created_tasks = relationship(
        "Task", foreign_keys="Task.creator_id", back_populates="creator"
    )
    approvals = relationship("Approval", back_populates="approver")
    client_approvals = relationship(
        "ClientApproval", foreign_keys="ClientApproval.client_id", back_populates="client"
    )
    agency_approvals = relationship(
        "ClientApproval", foreign_keys="ClientApproval.agency_id", back_populates="agency"
    )
    created_shares = relationship("ClientShare", back_populates="creator")
    created_versions = relationship("ContentVersion", back_populates="creator")

    # Many-to-many relationships
    teams = relationship("Team", secondary="team_members", back_populates="members")
    projects = relationship(
        "Project", secondary="project_members", back_populates="members"
    )

    # Relationships defined in other models:
    # owned_teams = relationship("Team", back_populates="owner")
    # project_roles = relationship("UserRole", back_populates="user")

    # New relationships
    notifications = relationship("Notification", back_populates="user")
    admin_logs = relationship("AdminLog", back_populates="admin")
