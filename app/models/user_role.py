from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class UserRole(BaseModel):
    __tablename__ = "user_roles"

    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    role = Column(String(50), nullable=False)  # e.g., 'admin', 'editor', 'viewer'
    permissions = Column(String(500))  # JSON string of permissions

    # Relationships
    user = relationship("User", back_populates="project_roles")
    project = relationship("Project", back_populates="user_roles")
