from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Enum, UUID, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, cast
import enum
import uuid

from app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CREATOR = "creator"
    EDITOR = "editor"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    role = Column(Enum(UserRole), default=UserRole.CREATOR)
    profile_picture = Column(String, nullable=True)
    timezone = Column(String, default="UTC")

    # Security fields
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String)
    last_login = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime(timezone=True))
    security_settings: Column[Dict[str, Any]] = Column(
        JSON,
        default={
            "session_timeout": 30,  # minutes
            "password_history": [],  # Store hashes of previous passwords
            "login_notifications": True,
        },
    )

    # Relationships
    projects = relationship("Project", back_populates="owner")
    team_memberships = relationship("TeamMember", back_populates="user")
    content = relationship("Content", back_populates="creator")
    social_media_accounts = relationship("SocialMediaAccount", back_populates="user")
    schedules = relationship("Schedule", back_populates="user")
    analytics = relationship("Analytics", back_populates="user")

    def is_account_locked(self) -> bool:
        """Check if the account is currently locked."""
        if not self.account_locked_until:
            return False
        current_time = datetime.now()
        return bool(current_time < cast(datetime, self.account_locked_until))

    def increment_failed_attempts(self) -> None:
        """Increment failed login attempts and lock account if necessary."""
        if self.failed_login_attempts is None:
            self.failed_login_attempts = cast(Column[int], 1)
        else:
            self.failed_login_attempts = cast(Column[int], int(self.failed_login_attempts) + 1)
            
        if self.failed_login_attempts >= 5:  # Lock after 5 failed attempts
            self.account_locked_until = cast(Column[datetime], datetime.now() + timedelta(minutes=30))

    def __repr__(self):
        return f"<User {self.email}>"
