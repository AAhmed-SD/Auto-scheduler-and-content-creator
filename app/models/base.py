"""Base model for SQLAlchemy models."""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class BaseModel:
    """Base model class."""

    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class BaseModel(Base):
    """Base model class with common fields for all models."""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False)


__all__ = ["Base", "BaseModel"]
