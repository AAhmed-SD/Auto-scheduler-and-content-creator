from pydantic_settings import BaseSettings
from typing import List
import secrets

class Settings(BaseSettings):
    # Database
    database_url: str
    echo_sql: bool = True
    test: bool = False
    
    # Project
    project_name: str = "My FastAPI project"
    debug_logs: bool = False
    
    # Security
    session_secret: str = secrets.token_urlsafe(32)
    allowed_origins: List[str] = ["http://localhost:3000"]
    redis_url: str = "redis://localhost:6379"
    
    # SSL
    ssl_keyfile: str = None
    ssl_certfile: str = None
    
    # Rate Limiting
    rate_limit_times: int = 10
    rate_limit_minutes: int = 1
    
    # JWT
    jwt_secret_key: str = secrets.token_urlsafe(32)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # File Upload
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_image_types: List[str] = ["image/jpeg", "image/png", "image/gif"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 