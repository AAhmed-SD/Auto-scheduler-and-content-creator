import pytest
from fastapi.testclient import TestClient
from app.schemas.social_media import Platform, MediaType, PostStatus

def test_get_users(client: TestClient):
    response = client.get("/mock/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) > 0
    assert all(isinstance(user["id"], str) for user in users)

def test_get_user(client: TestClient):
    # Test existing user
    response = client.get("/mock/users/user1")
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == "user1"
    
    # Test non-existent user
    response = client.get("/mock/users/nonexistent")
    assert response.status_code == 404

def test_get_templates(client: TestClient):
    # Test all templates
    response = client.get("/mock/templates")
    assert response.status_code == 200
    templates = response.json()
    assert isinstance(templates, list)
    assert len(templates) > 0

    # Test filtered by platform
    response = client.get("/mock/templates", params={"platform": "instagram"})
    assert response.status_code == 200
    templates = response.json()
    assert all(t["platform"] == "instagram" for t in templates)

def test_get_posts(client: TestClient):
    # Test default posts
    response = client.get("/mock/posts")
    assert response.status_code == 200
    posts = response.json()
    assert isinstance(posts, list)
    assert len(posts) <= 10  # Default limit

    # Test with limit
    response = client.get("/mock/posts", params={"limit": 5})
    assert response.status_code == 200
    posts = response.json()
    assert len(posts) <= 5

    # Test with platform filter
    response = client.get("/mock/posts", params={"platform": "instagram"})
    assert response.status_code == 200
    posts = response.json()
    assert all(p["platform"] == "instagram" for p in posts)

    # Test with status filter
    response = client.get("/mock/posts", params={"status": "scheduled"})
    assert response.status_code == 200
    posts = response.json()
    assert all(p["status"] == "scheduled" for p in posts)

def test_create_post(client: TestClient):
    post_data = {
        "platform": "instagram",
        "content": {
            "text": "Test post",
            "media_type": "image",
            "media_url": "https://example.com/image.jpg",
            "hashtags": ["#test"]
        },
        "scheduled_time": "2024-02-20T12:00:00Z"
    }
    response = client.post("/mock/posts", json=post_data)
    assert response.status_code == 200
    created_post = response.json()
    assert created_post["platform"] == post_data["platform"]
    assert created_post["content"]["text"] == post_data["content"]["text"]
    assert created_post["status"] == "scheduled"

def test_update_post(client: TestClient):
    update_data = {
        "platform": "instagram",
        "content": {
            "text": "Updated test post",
            "media_type": "image",
            "media_url": "https://example.com/image.jpg",
            "hashtags": ["#test", "#updated"]
        },
        "scheduled_time": "2024-02-20T12:00:00Z"
    }
    response = client.put("/mock/posts/post_1", json=update_data)
    assert response.status_code == 200
    updated_post = response.json()
    assert updated_post["id"] == "post_1"
    assert updated_post["content"]["text"] == update_data["content"]["text"]

def test_delete_post(client: TestClient):
    response = client.delete("/mock/posts/post_1")
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Post post_1 deleted successfully"

def test_get_analytics(client: TestClient):
    # Test default analytics
    response = client.get("/mock/analytics")
    assert response.status_code == 200
    analytics = response.json()
    assert isinstance(analytics, list)
    assert len(analytics) == 30  # Default days

    # Test with custom days
    response = client.get("/mock/analytics", params={"days": 7})
    assert response.status_code == 200
    analytics = response.json()
    assert len(analytics) == 7

def test_validation_errors(client: TestClient):
    # Test invalid platform
    response = client.get("/mock/posts", params={"platform": "invalid"})
    assert response.status_code == 422

    # Test invalid status
    response = client.get("/mock/posts", params={"status": "invalid"})
    assert response.status_code == 422

    # Test invalid limit
    response = client.get("/mock/posts", params={"limit": 0})
    assert response.status_code == 422
    response = client.get("/mock/posts", params={"limit": 101})
    assert response.status_code == 422

    # Test invalid post creation
    invalid_post = {
        "platform": "invalid",
        "content": {
            "text": "Test post",
            "media_type": "invalid",
        }
    }
    response = client.post("/mock/posts", json=invalid_post)
    assert response.status_code == 422 