from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .associations import comment_mentions
from .base import BaseModel
from .enums import ContentStatus, TaskStatus


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUESTED_CHANGES = "requested_changes"


class Comment(BaseModel):
    __tablename__ = "comments"

    content = Column(String(1000), nullable=False)
    content_item_id = Column(Integer, ForeignKey("contents.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    content_item = relationship("Content", back_populates="comments")
    creator = relationship("User", back_populates="created_comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")
    mentioned_users = relationship("User", secondary=comment_mentions)


class Approval(BaseModel):
    """Approval model for content review."""

    __tablename__ = "approvals"

    content_id = Column(Integer, ForeignKey("contents.id"))
    approver_id = Column(Integer, ForeignKey("users.id"))
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    content = relationship("Content", back_populates="approvals")
    approver = relationship("User", back_populates="approvals")


class ClientApproval(BaseModel):
    """Client approval model for content review."""

    __tablename__ = "client_approvals"

    content_id = Column(Integer, ForeignKey("contents.id"))
    client_id = Column(Integer, ForeignKey("users.id"))
    agency_id = Column(Integer, ForeignKey("users.id"))
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    feedback = Column(Text)
    requested_changes = Column(Text)
    is_urgent = Column(Boolean, default=False)
    deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    content = relationship("Content", back_populates="client_approvals")
    client = relationship("User", foreign_keys=[client_id], back_populates="client_approvals")
    agency = relationship("User", foreign_keys=[agency_id], back_populates="agency_approvals")


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class Task(BaseModel):
    __tablename__ = "tasks"

    title = Column(String(255), nullable=False)
    description = Column(String(1000))
    content_item_id = Column(Integer, ForeignKey("contents.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO)
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    content_item = relationship("Content", back_populates="tasks")
    assignee = relationship(
        "User", foreign_keys=[assignee_id], back_populates="assigned_tasks"
    )
    creator = relationship(
        "User", foreign_keys=[creator_id], back_populates="created_tasks"
    )


class ClientShare(BaseModel):
    __tablename__ = "client_shares"

    project_id = Column(Integer, ForeignKey("projects.id"))
    share_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    creator_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    project = relationship("Project", back_populates="client_shares")
    creator = relationship("User", back_populates="created_shares")


class ContentVersion(BaseModel):
    __tablename__ = "content_versions"

    content_item_id = Column(Integer, ForeignKey("contents.id"))
    version_number = Column(Integer, nullable=False)
    content_data = Column(JSON, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)

    # Relationships
    content_item = relationship("Content", back_populates="versions")
    creator = relationship("User", back_populates="created_versions")
