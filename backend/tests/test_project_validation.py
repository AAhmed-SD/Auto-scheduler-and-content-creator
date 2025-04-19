import pytest
from datetime import datetime, timedelta
from app.schemas.projects import (
    ProjectStatus,
    ContentGenerationType,
    Project,
    ProjectCreate,
    ProjectUpdate,
    ContentPrompt,
    InspirationMedia
)
from app.schemas.social_media import Platform

class TestProjectValidation:
    def test_project_name_validation(self):
        # Test empty name
        with pytest.raises(ValueError):
            ProjectCreate(
                name="",
                platform=Platform.INSTAGRAM,
                generation_type=ContentGenerationType.TEMPLATE_BASED
            )

        # Test too long name
        with pytest.raises(ValueError):
            ProjectCreate(
                name="a" * 101,
                platform=Platform.INSTAGRAM,
                generation_type=ContentGenerationType.TEMPLATE_BASED
            )

        # Test valid name
        project = ProjectCreate(
            name="Valid Project Name",
            platform=Platform.INSTAGRAM,
            generation_type=ContentGenerationType.TEMPLATE_BASED
        )
        assert project.name == "Valid Project Name"

    def test_platform_validation(self):
        # Test invalid platform
        with pytest.raises(ValueError):
            ProjectCreate(
                name="Test Project",
                platform="invalid_platform",
                generation_type=ContentGenerationType.TEMPLATE_BASED
            )

        # Test each valid platform
        for platform in Platform:
            project = ProjectCreate(
                name="Test Project",
                platform=platform,
                generation_type=ContentGenerationType.TEMPLATE_BASED
            )
            assert project.platform == platform

    def test_content_prompt_validation(self):
        # Test empty prompt text
        with pytest.raises(ValueError):
            ContentPrompt(text="")

        # Test valid prompt with all optional fields
        prompt = ContentPrompt(
            text="Create engaging content",
            tone="professional",
            target_audience="young professionals",
            key_points=["point1", "point2"],
            inspiration_media=[
                InspirationMedia(
                    url="https://example.com/image.jpg",
                    media_type="image",
                    description="Test image"
                )
            ]
        )
        assert prompt.text == "Create engaging content"
        assert len(prompt.key_points) == 2
        assert len(prompt.inspiration_media) == 1

    def test_inspiration_media_validation(self):
        # Test invalid URL
        with pytest.raises(ValueError):
            InspirationMedia(
                url="invalid_url",
                media_type="image"
            )

        # Test invalid media type
        with pytest.raises(ValueError):
            InspirationMedia(
                url="https://example.com/image.jpg",
                media_type="invalid_type"
            )

        # Test valid media
        media = InspirationMedia(
            url="https://example.com/image.jpg",
            media_type="image",
            description="Test image"
        )
        assert str(media.url) == "https://example.com/image.jpg"

    def test_project_update_validation(self):
        # Test partial update
        update = ProjectUpdate(name="Updated Name")
        assert update.name == "Updated Name"
        assert update.platform is None
        assert update.status is None

        # Test invalid status update
        with pytest.raises(ValueError):
            ProjectUpdate(status="invalid_status")

        # Test valid status update
        update = ProjectUpdate(status=ProjectStatus.IN_PROGRESS)
        assert update.status == ProjectStatus.IN_PROGRESS

    def test_template_based_project_validation(self):
        # Test template project without template_id
        with pytest.raises(ValueError):
            ProjectCreate(
                name="Template Project",
                platform=Platform.INSTAGRAM,
                generation_type=ContentGenerationType.TEMPLATE_BASED,
                content_prompt=ContentPrompt(text="Should not have prompt")
            )

        # Test valid template project
        project = ProjectCreate(
            name="Template Project",
            platform=Platform.INSTAGRAM,
            generation_type=ContentGenerationType.TEMPLATE_BASED,
            template_id="template1"
        )
        assert project.template_id == "template1"
        assert project.content_prompt is None

    def test_ai_generated_project_validation(self):
        # Test AI project without prompt
        with pytest.raises(ValueError):
            ProjectCreate(
                name="AI Project",
                platform=Platform.INSTAGRAM,
                generation_type=ContentGenerationType.AI_GENERATED,
                template_id="template1"
            )

        # Test valid AI project
        project = ProjectCreate(
            name="AI Project",
            platform=Platform.INSTAGRAM,
            generation_type=ContentGenerationType.AI_GENERATED,
            content_prompt=ContentPrompt(
                text="Create content",
                tone="professional"
            )
        )
        assert project.template_id is None
        assert project.content_prompt.text == "Create content"

    def test_project_dates_validation(self):
        # Test project with dates in the past
        past_date = datetime.now() - timedelta(days=1)
        project = Project(
            id="1",
            user_id="user1",
            name="Test Project",
            platform=Platform.INSTAGRAM,
            generation_type=ContentGenerationType.TEMPLATE_BASED,
            created_at=past_date,
            updated_at=datetime.now()
        )
        assert project.created_at < project.updated_at

        # Test project with invalid date order
        with pytest.raises(ValueError):
            Project(
                id="1",
                user_id="user1",
                name="Test Project",
                platform=Platform.INSTAGRAM,
                generation_type=ContentGenerationType.TEMPLATE_BASED,
                created_at=datetime.now(),
                updated_at=past_date
            ) 