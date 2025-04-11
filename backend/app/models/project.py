from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import List, Dict, Any
import uuid
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Security fields
    is_private = Column(Boolean, default=True)
    allowed_users: Column[List[int]] = Column(JSON, default=[])  # List of user IDs with access
    api_keys: Column[Dict[str, Any]] = Column(JSON, default={})  # Project-specific API keys

    # Relationships
    owner = relationship("User", back_populates="projects")
    team_members = relationship("TeamMember", back_populates="project")
    content = relationship("Content", back_populates="project")
    social_media_accounts = relationship("SocialMediaAccount", back_populates="project")
    categories = relationship("Category", back_populates="project")
    tags = relationship("Tag", back_populates="project")

    def __repr__(self):
        return f"<Project {self.name}>"

    def has_access(self, user_id: int) -> bool:
        """Check if a user has access to this project."""
        if self.owner_id == user_id:  # Owner always has access
            return True
        if not self.is_private:  # Public projects
            return True
        return user_id in (self.allowed_users or [])
