import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json
import random
import string
from typing import Dict, Any, List
from app.core.error_handler import ErrorHandler
from app.core.middleware import RequestLoggingMiddleware
from app.core.rate_limit import RateLimiter
from app.core.config import Settings
from app.core.logging import Logger
from app.core.security import SecurityManager
from app.core.monitoring import PerformanceMonitor

class TestCoreComponentsRigorous:
    """Comprehensive test suite for core components following industry best practices."""
    
    @pytest.fixture
    def app(self) -> FastAPI:
        """Create test FastAPI application."""
        app = FastAPI()
        return app
    
    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def security_manager(self) -> SecurityManager:
        """Create security manager instance."""
        return SecurityManager()
    
    @pytest.fixture
    def performance_monitor(self) -> PerformanceMonitor:
        """Create performance monitor instance."""
        return PerformanceMonitor()

    # Security Tests
    def test_security_headers(self, client: TestClient):
        """Test security headers are properly set."""
        response = client.get("/")
        headers = response.headers
        
        # OWASP recommended security headers
        required_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self'",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        }
        
        for header, value in required_headers.items():
            assert header in headers
            assert headers[header] == value

    def test_input_validation(self, client: TestClient):
        """Test input validation against common attack vectors."""
        # SQL Injection attempts
        sql_injection_attempts = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "UNION SELECT * FROM users"
        ]
        
        for attempt in sql_injection_attempts:
            response = client.get(f"/test?input={attempt}")
            assert response.status_code == 400
            
        # XSS attempts
        xss_attempts = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')"
        ]
        
        for attempt in xss_attempts:
            response = client.post("/test", json={"input": attempt})
            assert response.status_code == 400

    # Performance Tests
    def test_response_time(self, client: TestClient, performance_monitor: PerformanceMonitor):
        """Test response time under various conditions."""
        # Test normal load
        start_time = datetime.now()
        response = client.get("/")
        end_time = datetime.now()
        assert (end_time - start_time).total_seconds() < 1.0
        
        # Test under load
        with performance_monitor.measure("high_load"):
            responses = [client.get("/") for _ in range(100)]
            assert all(r.status_code == 200 for r in responses)
            assert performance_monitor.get_metric("high_load") < 5.0  # 5 seconds max

    def test_memory_usage(self, performance_monitor: PerformanceMonitor):
        """Test memory usage patterns."""
        # Test memory growth
        initial_memory = performance_monitor.get_memory_usage()
        
        # Generate large dataset
        large_data = [{"id": i, "data": "x" * 1000} for i in range(10000)]
        
        current_memory = performance_monitor.get_memory_usage()
        memory_increase = current_memory - initial_memory
        
        assert memory_increase < 100 * 1024 * 1024  # Less than 100MB increase

    # Error Handling Tests
    def test_error_handling_comprehensive(self, app: FastAPI, client: TestClient):
        """Test comprehensive error handling scenarios."""
        error_handler = ErrorHandler(app)
        
        # Test various error types
        error_scenarios = [
            (ValueError, "Invalid value"),
            (TypeError, "Type mismatch"),
            (KeyError, "Missing key"),
            (AttributeError, "Invalid attribute"),
            (Exception, "Unexpected error")
        ]
        
        for error_type, message in error_scenarios:
            @app.get(f"/test-{error_type.__name__}")
            async def test_error():
                raise error_type(message)
            
            response = client.get(f"/test-{error_type.__name__}")
            assert response.status_code == 500
            error_data = response.json()
            assert "error" in error_data
            assert "trace_id" in error_data
            assert error_data["error"]["message"] == message

    # Rate Limiting Tests
    def test_rate_limiting_advanced(self):
        """Test advanced rate limiting scenarios."""
        limiter = RateLimiter(requests_per_minute=60)
        
        # Test burst handling
        for _ in range(30):  # Half of limit
            assert limiter.check_limit("test_ip") is True
        
        # Test sustained rate
        for _ in range(30):  # Remaining half
            assert limiter.check_limit("test_ip") is True
        
        # Test limit exceeded
        assert limiter.check_limit("test_ip") is False
        
        # Test different IPs
        for i in range(60):
            assert limiter.check_limit(f"ip_{i}") is True

    # Configuration Tests
    def test_config_validation_comprehensive(self):
        """Test comprehensive configuration validation."""
        settings = Settings()
        
        # Test all required fields
        required_fields = [
            "APP_NAME", "DEBUG", "ENVIRONMENT",
            "API_VERSION", "LOG_LEVEL", "CORS_ORIGINS"
        ]
        
        for field in required_fields:
            assert hasattr(settings, field)
            assert getattr(settings, field) is not None
        
        # Test environment-specific validation
        assert settings.ENVIRONMENT in ["development", "staging", "production"]
        assert isinstance(settings.DEBUG, bool)
        assert isinstance(settings.API_VERSION, str)
        assert isinstance(settings.CORS_ORIGINS, list)

    # Logging Tests
    def test_logging_comprehensive(self):
        """Test comprehensive logging functionality."""
        logger = Logger()
        
        # Test all log levels
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in log_levels:
            message = f"Test {level} message"
            logger.log(level, message)
            
            # Verify log format
            log_entry = logger.get_last_entry()
            assert level in log_entry
            assert message in log_entry
            assert "timestamp" in log_entry
            assert "trace_id" in log_entry
        
        # Test structured logging
        structured_data = {
            "user_id": "123",
            "action": "login",
            "status": "success"
        }
        logger.info("User action", extra=structured_data)
        log_entry = logger.get_last_entry()
        assert all(key in log_entry for key in structured_data.keys())

    # Request Validation Tests
    def test_request_validation_comprehensive(self):
        """Test comprehensive request validation."""
        from app.core.middleware import validate_request
        
        # Test valid requests
        valid_requests = [
            {
                "type": "http",
                "method": "GET",
                "path": "/api/v1/test",
                "headers": [("Content-Type", "application/json")]
            },
            {
                "type": "http",
                "method": "POST",
                "path": "/api/v1/data",
                "headers": [("Content-Type", "application/json")]
            }
        ]
        
        for request_data in valid_requests:
            request = Request(scope=request_data)
            assert validate_request(request) is True
        
        # Test invalid requests
        invalid_requests = [
            {
                "type": "http",
                "method": "INVALID",
                "path": "/test",
                "headers": []
            },
            {
                "type": "http",
                "method": "GET",
                "path": "/../etc/passwd",
                "headers": []
            },
            {
                "type": "http",
                "method": "POST",
                "path": "/api/v1/test",
                "headers": [("Content-Type", "text/html")]
            }
        ]
        
        for request_data in invalid_requests:
            request = Request(scope=request_data)
            assert validate_request(request) is False

    # Mock Data Tests
    def test_mock_data_comprehensive(self):
        """Test comprehensive mock data generation and validation."""
        from app.mock_data.generators import (
            generate_mock_analytics,
            generate_mock_user,
            generate_mock_content
        )
        
        # Test analytics data
        analytics_data = generate_mock_analytics(days=30)
        assert len(analytics_data) == 30
        
        for entry in analytics_data:
            assert isinstance(entry["date"], str)
            assert isinstance(entry["metrics"], dict)
            assert all(isinstance(v, (int, float)) for v in entry["metrics"].values())
        
        # Test user data
        user_data = generate_mock_user()
        assert isinstance(user_data["id"], str)
        assert isinstance(user_data["email"], str)
        assert "@" in user_data["email"]
        
        # Test content data
        content_data = generate_mock_content()
        assert isinstance(content_data["id"], str)
        assert isinstance(content_data["text"], str)
        assert len(content_data["text"]) > 0 