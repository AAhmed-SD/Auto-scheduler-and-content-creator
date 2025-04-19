from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any, TypeVar, Generic, Generator
from .config import get_settings

load_dotenv()

# Initialize settings
settings = get_settings()

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Database tables
TABLES: Dict[str, str] = {
    "users": "users",
    "content": "content",
    "schedules": "schedules",
    "media": "media",
    "platforms": "platforms",
    "analytics": "analytics",
}

T = TypeVar('T')

class DatabaseResponse(Generic[T]):
    def __init__(self, data: Optional[T] = None):
        self.data = data

def get_db() -> Generator:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
