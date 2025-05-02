import os

import pytest
from fastapi.testclient import TestClient

from app.core.logging_config import setup_logging
from app.core.redis_config import RedisConfig
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def redis_client():
    return RedisConfig()


@pytest.fixture
def test_logger():
    return setup_logging()


@pytest.fixture(autouse=True)
def setup_test_env():
    # Set test environment variables
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DATABASE_URL"] = (
        "postgresql://postgres:postgres@localhost:5432/autoscheduler_test"
    )
    os.environ["REDIS_HOST"] = "localhost"
    os.environ["REDIS_PORT"] = "6379"

    yield

    # Cleanup after tests
    if os.path.exists("logs"):
        for file in os.listdir("logs"):
            if file.endswith(".log"):
                os.remove(os.path.join("logs", file))
