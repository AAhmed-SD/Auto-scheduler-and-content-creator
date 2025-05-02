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
    project = relationship('Project', back_populates='contents')
    versions = relationship('ContentVersion', back_populates='content')
    schedules = relationship('Schedule', back_populates='content')
    approvals = relationship('Approval', back_populates='content')
    client_approvals = relationship('ClientApproval', back_populates='content')

class ContentVersion(BaseModel):
    """Content version model."""
    __tablename__ = 'content_versions'

    content_id = Column(Integer, ForeignKey('contents.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    content_data = Column(Text, nullable=False)
    change_summary = Column(String(500))

    # Relationships
    content = relationship('Content', back_populates='versions')

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
