"""Content model module."""

from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import BaseModel

class Content(BaseModel):
    """Content model."""
    __tablename__ = 'contents'

    title = Column(String(200), nullable=False)
    description = Column(Text)
    content_type = Column(String(50), nullable=False)
    status = Column(String(20), default='draft')
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)

    # Relationships
    creator = relationship('User', back_populates='created_content')
    project = relationship('Project', back_populates='content_items')
    schedules = relationship('Schedule', back_populates='content')

class Schedule(BaseModel):
    """Schedule model."""
    __tablename__ = 'schedules'

    content_id = Column(Integer, ForeignKey('contents.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    platform = Column(String(50), nullable=False)
    status = Column(String(20), default='pending')
    scheduled_at = Column(String(50), nullable=False)

    # Relationships
    content = relationship('Content', back_populates='schedules')
    project = relationship('Project', back_populates='schedules')
