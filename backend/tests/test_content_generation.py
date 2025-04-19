import pytest
from datetime import datetime, timedelta
from app.schemas.social_media import (
    Platform,
    MediaType,
    PostStatus,
    Post,
    PostContent,
    Template,
    ContentStructure
)

class TestContentGeneration:
    def test_template_content_generation(self, client):
        # Test basic template substitution
        template = Template(
            id="test_template",
            name="Product Launch",
            platform=Platform.INSTAGRAM,
            structure=ContentStructure(
                caption="Introducing {product_name}! {description}",
                hashtags=["#launch", "#product"],
                media_type=MediaType.IMAGE
            )
        )

        variables = {
            "product_name": "New Product",
            "description": "Amazing features!"
        }

        # Test template rendering
        content = template.structure.caption.format(**variables)
        assert content == "Introducing New Product! Amazing features!"
        assert "#launch" in template.structure.hashtags

    def test_ai_content_generation(self, client):
        # Test AI prompt validation
        prompt = {
            "text": "Create a post about our new product launch",
            "tone": "professional",
            "target_audience": "tech enthusiasts",
            "key_points": [
                "innovative features",
                "competitive pricing",
                "early bird discount"
            ]
        }

        # Simulate AI response validation
        response = client.post("/mock/generate-content", json=prompt)
        assert response.status_code == 200
        content = response.json()

        assert "text" in content
        assert "media_type" in content
        assert "hashtags" in content

    def test_post_scheduling(self):
        # Test scheduling in the past
        with pytest.raises(ValueError):
            Post(
                platform=Platform.INSTAGRAM,
                content=PostContent(
                    text="Test post",
                    media_type=MediaType.IMAGE,
                    media_url="https://example.com/image.jpg",
                    hashtags=["#test"]
                ),
                scheduled_time=datetime.now() - timedelta(minutes=1),
                status=PostStatus.SCHEDULED
            )

        # Test valid scheduling
        future_time = datetime.now() + timedelta(days=1)
        post = Post(
            platform=Platform.INSTAGRAM,
            content=PostContent(
                text="Test post",
                media_type=MediaType.IMAGE,
                media_url="https://example.com/image.jpg",
                hashtags=["#test"]
            ),
            scheduled_time=future_time,
            status=PostStatus.SCHEDULED
        )
        assert post.scheduled_time > datetime.now()

    def test_content_length_limits(self):
        # Test platform-specific content length limits
        platform_limits = {
            Platform.TWITTER: 280,
            Platform.INSTAGRAM: 2200,
            Platform.LINKEDIN: 3000,
            Platform.FACEBOOK: 63206
        }

        for platform, limit in platform_limits.items():
            # Test content at limit
            content = "a" * limit
            post = Post(
                platform=platform,
                content=PostContent(
                    text=content,
                    media_type=MediaType.TEXT,
                    hashtags=["#test"]
                ),
                scheduled_time=datetime.now() + timedelta(days=1),
                status=PostStatus.SCHEDULED
            )
            assert len(post.content.text) == limit

            # Test content exceeding limit
            with pytest.raises(ValueError):
                Post(
                    platform=platform,
                    content=PostContent(
                        text="a" * (limit + 1),
                        media_type=MediaType.TEXT,
                        hashtags=["#test"]
                    ),
                    scheduled_time=datetime.now() + timedelta(days=1),
                    status=PostStatus.SCHEDULED
                )

    def test_hashtag_validation(self):
        # Test invalid hashtags
        invalid_hashtags = [
            "no_hash",  # Missing #
            "#",  # Empty hashtag
            "#invalid space",  # Space in hashtag
            "#" + "a" * 140,  # Too long
            "#123"  # Numbers only
        ]

        for hashtag in invalid_hashtags:
            with pytest.raises(ValueError):
                PostContent(
                    text="Test post",
                    media_type=MediaType.TEXT,
                    hashtags=[hashtag]
                )

        # Test valid hashtags
        valid_hashtags = [
            "#test",
            "#Test123",
            "#UPPERCASE",
            "#under_score",
            "#😊"  # Emoji hashtag
        ]

        content = PostContent(
            text="Test post",
            media_type=MediaType.TEXT,
            hashtags=valid_hashtags
        )
        assert all(tag in content.hashtags for tag in valid_hashtags)

    def test_media_type_compatibility(self):
        # Test platform-specific media type restrictions
        incompatible_combinations = [
            (Platform.TWITTER, MediaType.VIDEO, "https://example.com/large_video.mp4"),  # Too large
            (Platform.INSTAGRAM, MediaType.TEXT, None),  # Instagram requires media
            (Platform.LINKEDIN, MediaType.VIDEO, "https://example.com/invalid_format.mov")  # Invalid format
        ]

        for platform, media_type, media_url in incompatible_combinations:
            with pytest.raises(ValueError):
                Post(
                    platform=platform,
                    content=PostContent(
                        text="Test post",
                        media_type=media_type,
                        media_url=media_url,
                        hashtags=["#test"]
                    ),
                    scheduled_time=datetime.now() + timedelta(days=1),
                    status=PostStatus.SCHEDULED
                )

    def test_cross_platform_content_adaptation(self):
        # Test content adaptation across platforms
        original_content = PostContent(
            text="Original post with #hashtag and @mention",
            media_type=MediaType.IMAGE,
            media_url="https://example.com/image.jpg",
            hashtags=["#test"]
        )

        # Test platform-specific adaptations
        platforms = [Platform.TWITTER, Platform.INSTAGRAM, Platform.LINKEDIN, Platform.FACEBOOK]
        for platform in platforms:
            adapted_post = Post(
                platform=platform,
                content=original_content,
                scheduled_time=datetime.now() + timedelta(days=1),
                status=PostStatus.SCHEDULED
            )
            
            # Verify platform-specific modifications
            if platform == Platform.TWITTER:
                assert len(adapted_post.content.text) <= 280
            elif platform == Platform.INSTAGRAM:
                assert adapted_post.content.media_url is not None
            elif platform == Platform.LINKEDIN:
                assert "@mention" not in adapted_post.content.text 