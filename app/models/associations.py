"""Association tables for many-to-many relationships."""

from sqlalchemy import Column, ForeignKey, Integer, Table

from .base import Base

# Association table for team members
team_members = Table(
    "team_members",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)

# Association table for project members
project_members = Table(
    "project_members",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)

# Association table for content tags
content_tags = Table(
    "content_tags",
    Base.metadata,
    Column("content_id", Integer, ForeignKey("contents.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

comment_mentions = Table(
    "comment_mentions",
    Base.metadata,
    Column("comment_id", Integer, ForeignKey("comments.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
)
