"""Project model for the application."""

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel

class Project(BaseModel):
    """Project model representing user projects."""

    __tablename__ = "projects"

    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    is_active = Column(Boolean, default=True)

    # Relationships
    content_items = relationship("Content", back_populates="project")
    schedules = relationship("Schedule", back_populates="project")
    members = relationship("User", secondary="project_members", back_populates="projects")
