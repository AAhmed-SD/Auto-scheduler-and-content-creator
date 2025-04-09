from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base

class Platform(str, enum.Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    THREADS = "threads"
    PINTEREST = "pinterest"
    LINKEDIN = "linkedin"

class ScheduleStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    repeat = Column(Boolean, default=False)
    repeat_interval = Column(String, nullable=True)
    platform = Column(Enum(Platform), nullable=False)
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.PENDING)
    platform_specific_data = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    content = relationship("Content", back_populates="schedules")
    user = relationship("User", back_populates="schedules")

    def __repr__(self):
        return f"<Schedule {self.id} for {self.platform} at {self.scheduled_time}>" 