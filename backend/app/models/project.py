from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import List, Dict, Any
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
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
    content = relationship("Content", back_populates="project")
    schedules = relationship("Schedule", back_populates="project")

    def has_access(self, user_id: int) -> bool:
        """Check if a user has access to this project."""
        if self.owner_id == user_id:  # Owner always has access
            return True
        if not self.is_private:  # Public projects
            return True
        return user_id in (self.allowed_users or [])
