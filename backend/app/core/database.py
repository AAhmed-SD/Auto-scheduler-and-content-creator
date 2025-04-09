from supabase import create_client, Client
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any, TypeVar, Generic, Generator
from .config import get_settings

load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    supabase_url=os.getenv("SUPABASE_URL") or "", 
    supabase_key=os.getenv("SUPABASE_KEY") or ""
)

# SQLAlchemy setup
settings = get_settings()

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

async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    response = supabase.table(TABLES["users"]).select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None


async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    response = (
        supabase.table(TABLES["users"]).select("*").eq("username", username).execute()
    )
    return response.data[0] if response.data else None


async def create_user(user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    response = supabase.table(TABLES["users"]).insert(user_data).execute()
    return response.data[0] if response.data else None


async def create_content(content_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    response = supabase.table(TABLES["content"]).insert(content_data).execute()
    return response.data[0] if response.data else None


async def get_user_content(user_id: str) -> List[Dict[str, Any]]:
    response = (
        supabase.table(TABLES["content"]).select("*").eq("user_id", user_id).execute()
    )
    return response.data


async def create_schedule(schedule_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    response = supabase.table(TABLES["schedules"]).insert(schedule_data).execute()
    return response.data[0] if response.data else None


async def get_user_schedules(user_id: str) -> List[Dict[str, Any]]:
    response = (
        supabase.table(TABLES["schedules"]).select("*").eq("user_id", user_id).execute()
    )
    return response.data


async def update_schedule_status(schedule_id: str, status: str) -> Optional[Dict[str, Any]]:
    response = (
        supabase.table(TABLES["schedules"])
        .update({"status": status})
        .eq("id", schedule_id)
        .execute()
    )
    return response.data[0] if response.data else None


async def create_media(media_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    response = supabase.table(TABLES["media"]).insert(media_data).execute()
    return response.data[0] if response.data else None


async def get_user_media(user_id: str) -> List[Dict[str, Any]]:
    response = (
        supabase.table(TABLES["media"]).select("*").eq("user_id", user_id).execute()
    )
    return response.data


async def create_platform(platform_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    response = supabase.table(TABLES["platforms"]).insert(platform_data).execute()
    return response.data[0] if response.data else None


async def get_user_platforms(user_id: str) -> List[Dict[str, Any]]:
    response = (
        supabase.table(TABLES["platforms"]).select("*").eq("user_id", user_id).execute()
    )
    return response.data


async def create_analytics(analytics_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    response = supabase.table(TABLES["analytics"]).insert(analytics_data).execute()
    return response.data[0] if response.data else None


async def get_content_analytics(content_id: str) -> List[Dict[str, Any]]:
    response = (
        supabase.table(TABLES["analytics"])
        .select("*")
        .eq("content_id", content_id)
        .execute()
    )
    return response.data

def get_db() -> Generator:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
