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


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CREATOR = "creator"
    REVIEWER = "reviewer"
    CLIENT = "client"
