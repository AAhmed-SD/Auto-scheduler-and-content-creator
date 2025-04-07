import os
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user import User
from app.models.content import Content, ContentType, ContentStatus
from app.services.auth_service import AuthService


def init_db() -> None:
    db = SessionLocal()
    auth_service = AuthService(db)

    try:
        # Create admin user
        admin = auth_service.create_user(
            email="admin@example.com", password="admin123", full_name="Admin User"
        )
        admin.is_superuser = True
        db.commit()

        # Create sample content
        content = Content(
            title="Sample Video Content",
            description="This is a sample video content",
            content_type=ContentType.VIDEO,
            status=ContentStatus.READY,
            style_template={
                "shot_composition": ["wide", "close-up"],
                "color_palette": ["#FF0000", "#00FF00"],
                "transition_style": "fade",
                "text_animation": "fade-in",
                "music_tempo": "slow",
            },
            media_url="https://example.com/sample.mp4",
            thumbnail_url="https://example.com/thumbnail.jpg",
            metadata={"duration": "60s", "resolution": "1080p"},
            user_id=admin.id,
        )
        db.add(content)
        db.commit()

        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
