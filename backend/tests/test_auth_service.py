import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.auth_service import AuthService
from app.models.user import User
from datetime import timedelta

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


def test_verify_password():
    auth_service = AuthService(None)
    password = "test123"
    hashed_password = auth_service.get_password_hash(password)
    assert auth_service.verify_password(password, hashed_password)
    assert not auth_service.verify_password("wrong_password", hashed_password)


def test_create_user(db_session):
    auth_service = AuthService(db_session)
    user = auth_service.create_user(
        email="test@example.com", password="test123", full_name="Test User"
    )
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.hashed_password is not None
    assert user.hashed_password != "test123"  # Password should be hashed


def test_create_duplicate_user(db_session):
    auth_service = AuthService(db_session)
    auth_service.create_user(
        email="test@example.com", password="test123", full_name="Test User"
    )
    with pytest.raises(Exception) as exc_info:
        auth_service.create_user(
            email="test@example.com", password="test123", full_name="Test User"
        )
    assert "Email already registered" in str(exc_info.value)


def test_authenticate_user(db_session):
    auth_service = AuthService(db_session)
    auth_service.create_user(
        email="test@example.com", password="test123", full_name="Test User"
    )

    # Test correct credentials
    user = auth_service.authenticate_user("test@example.com", "test123")
    assert user is not None
    assert user.email == "test@example.com"

    # Test wrong password
    user = auth_service.authenticate_user("test@example.com", "wrong_password")
    assert user is None

    # Test non-existent user
    user = auth_service.authenticate_user("nonexistent@example.com", "test123")
    assert user is None


def test_create_access_token():
    auth_service = AuthService(None)
    data = {"sub": "test@example.com"}
    token = auth_service.create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_with_expiry():
    auth_service = AuthService(None)
    data = {"sub": "test@example.com"}
    expires_delta = timedelta(minutes=30)
    token = auth_service.create_access_token(data, expires_delta)
    assert isinstance(token, str)
    assert len(token) > 0
