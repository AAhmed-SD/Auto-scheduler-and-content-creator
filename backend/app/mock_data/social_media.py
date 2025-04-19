from datetime import datetime, timedelta
from typing import List
import random
from ..schemas.social_media import (
    User, Template, Post, Analytics,
    Platform, MediaType, PostStatus,
    ContentStructure, PostContent, PostMetrics, AnalyticsMetrics
)

# Mock user data
MOCK_USERS: List[User] = [
    User(
        id="user1",
        username="business_account",
        platform=Platform.INSTAGRAM,
        followers=15000,
        following=500,
        profile_picture="https://via.placeholder.com/150"
    ),
    User(
        id="user2",
        username="company_page",
        platform=Platform.LINKEDIN,
        followers=5000,
        following=200,
        profile_picture="https://via.placeholder.com/150"
    )
]

# Mock content templates
CONTENT_TEMPLATES: List[Template] = [
    Template(
        id="template1",
        name="Product Announcement",
        platform=Platform.INSTAGRAM,
        structure=ContentStructure(
            caption="Exciting news! 🎉 Our new {product_name} is now available!",
            hashtags=["#newproduct", "#launch", "#excited"],
            media_type=MediaType.IMAGE
        )
    ),
    Template(
        id="template2",
        name="Company Update",
        platform=Platform.LINKEDIN,
        structure=ContentStructure(
            title="Company Milestone: {milestone}",
            content="We're thrilled to announce that we've reached {number} {metric}!",
            hashtags=["#companynews", "#milestone", "#growth"],
            media_type=MediaType.IMAGE
        )
    )
]

def generate_mock_posts(count: int = 10) -> List[Post]:
    posts = []
    for i in range(count):
        post = Post(
            id=f"post_{i}",
            platform=random.choice(list(Platform)),
            content=PostContent(
                text=f"Sample post content {i}",
                media_url=f"https://via.placeholder.com/500x300?text=Post+{i}",
                media_type=random.choice(list(MediaType)),
                hashtags=["#sample", "#mock", "#data"]
            ),
            scheduled_time=datetime.now() + timedelta(days=random.randint(1, 30)),
            status=random.choice(list(PostStatus)),
            metrics=PostMetrics(
                likes=random.randint(0, 1000),
                comments=random.randint(0, 100),
                shares=random.randint(0, 500),
                reach=random.randint(1000, 10000)
            )
        )
        posts.append(post)
    return posts

def generate_mock_analytics(days: int = 30) -> List[Analytics]:
    analytics = []
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        analytics.append(
            Analytics(
                date=date,
                metrics=AnalyticsMetrics(
                    followers=random.randint(1000, 2000),
                    engagement_rate=random.uniform(2.0, 5.0),
                    reach=random.randint(5000, 15000),
                    impressions=random.randint(8000, 20000)
                )
            )
        )
    return analytics 