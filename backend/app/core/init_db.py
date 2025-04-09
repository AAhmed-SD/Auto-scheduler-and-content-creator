from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import get_settings
from .database import Base
from .models import user, content, schedule, analytics

settings = get_settings()

def init_db():
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Add any initial data here if needed
        pass
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Database tables created successfully!") 