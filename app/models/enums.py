import enum


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    PENDING_REVIEW = "pending_review"
    NEEDS_REVISION = "needs_revision"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
