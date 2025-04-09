from sqlalchemy import Column, Integer, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Analytics(BaseModel):
    __tablename__ = "analytics"
    
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    click_through_rate = Column(Float, default=0.0)
    engagement_rate = Column(Float, default=0.0)
    platform_specific_metrics = Column(JSON, nullable=True)
    
    # Foreign Keys
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    content = relationship("Content", back_populates="analytics")
    user = relationship("User", back_populates="analytics")
    
    def __repr__(self):
        return f"<Analytics for Content {self.content_id}>" 