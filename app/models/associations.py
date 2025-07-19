"""Association tables for many-to-many relationships."""

from sqlalchemy import Column, ForeignKey, Integer, Table

from .base import Base

# Association table for project members
project_members = Table(
    "project_members",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)
