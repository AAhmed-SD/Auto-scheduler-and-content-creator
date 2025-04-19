import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import Generator
from app.main import app

# Create a test app instance
app = FastAPI()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(scope="module")
def mock_user_token() -> str:
    # TODO: Implement proper JWT token generation for testing
    return "test_token"

@pytest.fixture
def mock_project_data():
    return {
        "name": "Test Project",
        "description": "A test project",
        "platform": "instagram",
        "generation_type": "template_based",
        "template_id": "template1"
    }

@pytest.fixture
def mock_ai_project_data():
    return {
        "name": "AI Test Project",
        "description": "An AI-generated test project",
        "platform": "instagram",
        "generation_type": "ai_generated",
        "content_prompt": {
            "text": "Create an engaging post about new product launch",
            "tone": "professional",
            "target_audience": "young professionals",
            "key_points": ["innovative features", "competitive pricing"],
            "inspiration_media": [
                {
                    "url": "https://example.com/inspiration.jpg",
                    "media_type": "image",
                    "description": "Similar product launch"
                }
            ]
        }
    }

@pytest.fixture
def mock_analytics_routes(client):
    # Mock routes for analytics testing
    @app.get("/mock/analytics")
    async def get_analytics(days: int = 30):
        from datetime import datetime, timedelta
        from app.schemas.analytics import Analytics, AnalyticsMetrics
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        data = []
        current_date = start_date
        base_followers = 1000
        
        while current_date <= end_date:
            followers = base_followers + len(data) * 10  # Simulate growth
            data.append({
                "date": current_date.isoformat(),
                "metrics": {
                    "followers": followers,
                    "engagement_rate": 5.0,
                    "reach": followers // 2,
                    "impressions": followers
                }
            })
            current_date += timedelta(days=1)
        
        return data

    @app.get("/mock/analytics/platform/{platform}")
    async def get_platform_metrics(platform: str):
        platform_metrics = {
            "INSTAGRAM": {
                "metrics": {
                    "likes": 100,
                    "comments": 50,
                    "saves": 20,
                    "shares": 30
                }
            },
            "TWITTER": {
                "metrics": {
                    "likes": 200,
                    "retweets": 80,
                    "replies": 40,
                    "quotes": 10
                }
            },
            "FACEBOOK": {
                "metrics": {
                    "likes": 300,
                    "comments": 100,
                    "shares": 50,
                    "reactions": 200
                }
            },
            "LINKEDIN": {
                "metrics": {
                    "likes": 150,
                    "comments": 70,
                    "shares": 40,
                    "clicks": 90
                }
            }
        }
        return platform_metrics.get(platform, {"metrics": {}})

    @app.get("/mock/analytics/aggregate")
    async def get_aggregated_analytics(period: str):
        from datetime import datetime, timedelta
        from app.schemas.analytics import Analytics, AnalyticsMetrics
        
        end_date = datetime.now()
        if period == "day":
            points = 24
            delta = timedelta(hours=1)
        elif period == "week":
            points = 7
            delta = timedelta(days=1)
        else:  # month
            points = 31
            delta = timedelta(days=1)
        
        data = []
        current_date = end_date - (points * delta)
        
        for _ in range(points):
            data.append({
                "date": current_date.isoformat(),
                "metrics": {
                    "followers": 1000,
                    "engagement_rate": 5.0,
                    "reach": 500,
                    "impressions": 1000
                }
            })
            current_date += delta
        
        return data

    return client 