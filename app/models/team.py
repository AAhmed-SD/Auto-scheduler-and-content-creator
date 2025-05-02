"""Team model module."""

from typing import Dict

from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

from .base import Base, BaseModel

team_members = Table(
    'team_members',
    Base.metadata,
    Column('team_id', Integer, ForeignKey('teams.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class Team(BaseModel):
    """Team model."""
    __tablename__ = 'teams'

    name = Column(String(100), nullable=False)
    description = Column(String(500))
    members = relationship('User', secondary=team_members, back_populates='teams')
    projects = relationship('Project', back_populates='team')

    def to_dict(self) -> Dict:
        """Convert team to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }
