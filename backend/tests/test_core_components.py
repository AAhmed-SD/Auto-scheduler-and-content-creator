import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.core.error_handler import ErrorHandler
from app.core.middleware import RequestLoggingMiddleware
from app.core.rate_limit import RateLimiter
from app.core.config import Settings
from app.core.logging import Logger

# Test Error Handler
def test_error_handler():
    app = FastAPI()
    error_handler = ErrorHandler(app)
    
    @app.get("/test-error")
    async def test_error():
        raise ValueError("Test error")
    
    client = TestClient(app)
    response = client.get("/test-error")
    assert response.status_code == 500
    assert "error" in response.json()

# Test Middleware
def test_request_logging_middleware():
    app = FastAPI()
    middleware = RequestLoggingMiddleware(app)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    client = TestClient(app)
    response = client.get("/test")
    assert response.status_code == 200

# Test Rate Limiter
def test_rate_limiter():
    limiter = RateLimiter(requests_per_minute=2)
    
    # Test within limit
    for _ in range(2):
        assert limiter.check_limit("test_ip") is True
    
    # Test exceeding limit
    assert limiter.check_limit("test_ip") is False

# Test Configuration
def test_config_validation():
    settings = Settings()
    
    # Test required fields
    assert settings.APP_NAME is not None
    assert settings.DEBUG is not None
    
    # Test environment-specific settings
    assert isinstance(settings.DEBUG, bool)

# Test Logger
def test_logger():
    logger = Logger()
    
    # Test log levels
    logger.debug("Test debug message")
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    
    # Test log formatting
    log_message = "Test message"
    formatted_message = logger.format_message(log_message, "INFO")
    assert "INFO" in formatted_message
    assert log_message in formatted_message

# Test Schema Validation
def test_analytics_schema():
    from app.schemas.analytics import AnalyticsMetrics
    
    # Test valid metrics
    valid_metrics = AnalyticsMetrics(
        followers=1000,
        engagement_rate=5.0,
        reach=500,
        impressions=1000
    )
    assert valid_metrics.followers == 1000
    
    # Test invalid metrics
    with pytest.raises(ValueError):
        AnalyticsMetrics(
            followers=-1,
            engagement_rate=5.0,
            reach=500,
            impressions=1000
        )

# Test Mock Data
def test_mock_data_generation():
    from app.mock_data.generators import generate_mock_analytics
    
    # Test data generation
    mock_data = generate_mock_analytics(days=7)
    assert len(mock_data) == 7
    
    # Test data validation
    for entry in mock_data:
        assert "date" in entry
        assert "metrics" in entry
        assert isinstance(entry["metrics"]["followers"], int)
        assert isinstance(entry["metrics"]["engagement_rate"], float)

# Test Request Validation
def test_request_validation():
    from app.core.middleware import validate_request
    
    # Test valid request
    valid_request = Request(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": []
        }
    )
    assert validate_request(valid_request) is True
    
    # Test invalid request
    invalid_request = Request(
        scope={
            "type": "http",
            "method": "INVALID",
            "path": "/test",
            "headers": []
        }
    )
    assert validate_request(invalid_request) is False 