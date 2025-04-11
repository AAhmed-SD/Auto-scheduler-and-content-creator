from sqlalchemy import Column, String, UUID, ForeignKey, JSON, DateTime, Enum
from sqlalchemy.orm import relationship
import uuid
from enum import Enum as PyEnum

from app.models.base import Base

class Platform(str, PyEnum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    PINTEREST = "pinterest"
    THREADS = "threads"
    TWITTER = "twitter"

class PostStatus(str, PyEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"

class SocialMediaPost(Base):
    __tablename__ = "social_media_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("content.id"), nullable=False)
    platform = Column(Enum(Platform), nullable=False)
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)
    scheduled_time = Column(DateTime)
    published_time = Column(DateTime)
    platform_post_id = Column(String)
    platform_url = Column(String)
    metadata = Column(JSON, default={})
    
    # Relationships
    content = relationship("Content", back_populates="social_media_posts")
    performance_metrics = relationship("PostPerformance", back_populates="post")
    
    def __repr__(self):
        return f"<SocialMediaPost {self.platform} - {self.status}>"

class PostPerformance(Base):
    __tablename__ = "post_performance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("social_media_posts.id"), nullable=False)
    metrics = Column(JSON, default={})
    recorded_at = Column(DateTime, nullable=False)
    
    # Relationships
    post = relationship("SocialMediaPost", back_populates="performance_metrics")
    
    def __repr__(self):
        return f"<PostPerformance {self.post_id}>" 