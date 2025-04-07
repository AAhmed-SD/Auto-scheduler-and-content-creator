from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
from functools import lru_cache
import json

load_dotenv()


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Auto Scheduler & Content Creator"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./sql_app.db"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Firebase Configuration
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_PRIVATE_KEY: str = os.getenv("FIREBASE_PRIVATE_KEY", "").replace(
        "\\n", "\n"
    )
    FIREBASE_CLIENT_EMAIL: str = os.getenv("FIREBASE_CLIENT_EMAIL", "")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Storage
    UPLOAD_FOLDER: str = "uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB

    # Social Media API Keys
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    TIKTOK_ACCESS_TOKEN: Optional[str] = os.getenv("TIKTOK_ACCESS_TOKEN")
    YOUTUBE_API_KEY: Optional[str] = os.getenv("YOUTUBE_API_KEY")

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:19006"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Admin
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")

    # Firebase credentials
    FIREBASE_CREDENTIALS: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"

    def get_firebase_credentials(self) -> Dict[str, Any]:
        """Get Firebase credentials as a dictionary"""
        try:
            private_key = self.FIREBASE_PRIVATE_KEY
            if isinstance(private_key, str):
                try:
                    private_key = json.loads(private_key)
                except json.JSONDecodeError:
                    pass

            return {
                "type": "service_account",
                "project_id": self.FIREBASE_PROJECT_ID,
                "private_key": private_key,
                "client_email": self.FIREBASE_CLIENT_EMAIL,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        except Exception as e:
            raise ValueError(f"Error getting Firebase credentials: {str(e)}")


@lru_cache()
def get_settings() -> Settings:
    try:
        return Settings()
    except Exception as e:
        raise ValueError(f"Error loading settings: {str(e)}")


settings = get_settings()
