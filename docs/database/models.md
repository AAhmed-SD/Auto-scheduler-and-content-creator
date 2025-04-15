# Database Models Documentation

## Overview
This document provides detailed information about the database models used in the Auto-Scheduler & Content Creator platform. The models are built using SQLAlchemy and follow a domain-driven design approach.

## Base Model
All models inherit from the `Base` class which provides common functionality:

```python
class Base:
    id: Any
    __name__: str
    
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
```

## Core Models

### User Model
The `User` model represents platform users with the following fields:
- `id`: UUID primary key
- `email`: Unique email address
- `hashed_password`: Securely hashed password
- `full_name`: User's full name
- `is_active`: Account status
- `is_superuser`: Admin privileges

Relationships:
- `projects`: One-to-many with Project (owner)
- `team_memberships`: One-to-many with TeamMember
- `content`: One-to-many with Content (creator)
- `social_media_accounts`: One-to-many with SocialMediaAccount

### Project Model
The `Project` model represents content projects with the following fields:
- `id`: UUID primary key
- `name`: Project name
- `description`: Project description
- `owner_id`: Foreign key to User
- `settings`: JSON field for project-specific settings

Relationships:
- `owner`: Many-to-one with User
- `team_members`: One-to-many with TeamMember
- `content`: One-to-many with Content
- `social_media_accounts`: One-to-many with SocialMediaAccount
- `categories`: Many-to-many with Category
- `tags`: Many-to-many with Tag

### Content Model
The `Content` model represents content items with the following fields:
- `id`: UUID primary key
- `title`: Content title
- `description`: Content description
- `content_type`: Enum (TEXT, IMAGE, VIDEO, etc.)
- `status`: Enum (DRAFT, SCHEDULED, PUBLISHED, etc.)
- `project_id`: Foreign key to Project
- `creator_id`: Foreign key to User
- `media_urls`: JSON array of media URLs
- `metadata`: JSON field for additional data

Relationships:
- `project`: Many-to-one with Project
- `creator`: Many-to-one with User
- `categories`: Many-to-many with Category
- `tags`: Many-to-many with Tag
- `social_media_posts`: One-to-many with SocialMediaPost
- `approvals`: One-to-many with ContentApproval
- `performance_metrics`: One-to-many with ContentPerformance

### Social Media Models

#### SocialMediaPost
Represents posts on social media platforms:
- `id`: UUID primary key
- `content_id`: Foreign key to Content
- `platform`: Enum (INSTAGRAM, TIKTOK, etc.)
- `status`: Enum (DRAFT, SCHEDULED, PUBLISHED)
- `scheduled_time`: Scheduled publication time
- `published_time`: Actual publication time
- `platform_post_id`: Platform-specific post ID
- `platform_url`: URL of the published post
- `metadata`: JSON field for platform-specific data

Relationships:
- `content`: Many-to-one with Content
- `performance_metrics`: One-to-many with PostPerformance

#### PostPerformance
Tracks performance metrics for social media posts:
- `id`: UUID primary key
- `post_id`: Foreign key to SocialMediaPost
- `metrics`: JSON field for performance data
- `recorded_at`: Timestamp of metrics

Relationships:
- `post`: Many-to-one with SocialMediaPost

## Enums

### ContentType
```python
class ContentType(str, PyEnum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"
```

### ContentStatus
```python
class ContentStatus(str, PyEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"
```

### Platform
```python
class Platform(str, PyEnum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    PINTEREST = "pinterest"
    THREADS = "threads"
    TWITTER = "twitter"
```

### PostStatus
```python
class PostStatus(str, PyEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
```

## Best Practices

### Model Usage
1. Always use the base model for new models
2. Use UUIDs for primary keys
3. Implement proper relationships
4. Add appropriate indexes
5. Use enums for fixed choices
6. Implement soft delete using deleted_at

### Security
1. Never store plain text passwords
2. Use proper foreign key constraints
3. Implement row-level security
4. Validate input data
5. Use proper data types

### Performance
1. Add appropriate indexes
2. Use JSON fields for flexible data
3. Implement proper relationships
4. Use soft delete for data retention
5. Monitor query performance

## Migration Guidelines
1. Always create migrations for model changes
2. Test migrations before applying
3. Backup data before migrations
4. Document migration steps
5. Test rollback procedures

## Troubleshooting
1. Check relationship definitions
2. Verify foreign key constraints
3. Monitor query performance
4. Check index usage
5. Review error logs 