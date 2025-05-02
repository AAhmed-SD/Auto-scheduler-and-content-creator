"""Project model for the application."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .base import BaseModel

# Association table for project members
project_members = Table(
    'project_members',
    BaseModel.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class Project(BaseModel):
    """Project model representing team projects."""

    __tablename__ = "projects"

    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    team_id = Column(Integer, ForeignKey("teams.id"))
    is_active = Column(Boolean, default=True)

    # Relationships
    team = relationship("Team", back_populates="projects")
    content_items = relationship("Content", back_populates="project")
    schedules = relationship("Schedule", back_populates="project")
    client_shares = relationship("ClientShare", back_populates="project")
    members = relationship("User", secondary=project_members, back_populates="projects")
