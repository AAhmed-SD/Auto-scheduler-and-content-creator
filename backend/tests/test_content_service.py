import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.content_service import ContentService
from app.models.user import User
from app.models.content import Content, ContentType, ContentStatus
from app.services.auth_service import AuthService

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    auth_service = AuthService(db_session)
    user = auth_service.create_user(
        email="test@example.com", password="test123", full_name="Test User"
    )
    return user


@pytest.mark.asyncio
async def test_analyze_style(db_session):
    content_service = ContentService(db_session)
    result = await content_service.analyze_style(
        reference_url="https://example.com/video", content_type="video"
    )
    assert isinstance(result, dict)
    assert "shot_composition" in result
    assert "color_palette" in result
    assert "transition_style" in result
    assert "text_animation" in result
    assert "music_tempo" in result


@pytest.mark.asyncio
async def test_generate_content(db_session, test_user):
    content_service = ContentService(db_session)
    result = await content_service.generate_content(
        template_id="template_123",
        content_type="video",
        quote="Test quote",
        style_adjustments={"color": "blue"},
        music_preference="slow",
    )
    assert isinstance(result, dict)
    assert "content_id" in result
    assert "status" in result
    assert result["status"] == ContentStatus.GENERATING.value

    # Verify content was created in database
    content = (
        db_session.query(Content).filter(Content.id == result["content_id"]).first()
    )
    assert content is not None
    assert content.user_id == test_user.id
    assert content.content_type == ContentType.VIDEO


@pytest.mark.asyncio
async def test_schedule_content(db_session, test_user):
    # First create a content
    content_service = ContentService(db_session)
    content = Content(
        title="Test Content",
        description="Test Description",
        content_type=ContentType.VIDEO,
        status=ContentStatus.READY,
        user_id=test_user.id,
    )
    db_session.add(content)
    db_session.commit()

    # Then schedule it
    result = await content_service.schedule_content(
        content_id=content.id,
        platforms=["instagram", "tiktok"],
        schedule={"time": "2024-03-20T10:00:00"},
        captions={"instagram": "Test caption"},
        hashtags={"instagram": ["#test", "#content"]},
    )
    assert isinstance(result, dict)
    assert "schedule_id" in result
    assert "status" in result
    assert result["status"] == "scheduled"
    assert "platform_status" in result
    assert len(result["platform_status"]) == 2

    # Verify content status was updated
    db_session.refresh(content)
    assert content.status == ContentStatus.SCHEDULED
