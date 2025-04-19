from sqlalchemy import Column, Integer, Float, JSON, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
from datetime import datetime, timedelta
from ..database import Base
from ..schemas.social_media import Platform

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

class AnalyticsModel(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    platform = Column(Enum(Platform), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # Metrics
    followers = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    reach = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    
    # Relationships
    project = relationship("ProjectModel", back_populates="analytics")
    
    @classmethod
    def validate_date_range(cls, start_date: datetime, end_date: datetime) -> bool:
        if start_date > end_date:
            raise ValueError("Start date must be before end date")
        
        if end_date > datetime.now():
            raise ValueError("End date cannot be in the future")
            
        # Maximum range is 1 year
        if end_date - start_date > timedelta(days=365):
            raise ValueError("Date range cannot exceed 1 year")
            
        return True
    
    @classmethod
    def validate_aggregation_period(cls, period: str, data_points: list) -> bool:
        min_points = {
            'day': 1,
            'week': 3,
            'month': 7
        }
        
        if len(data_points) < min_points[period]:
            raise ValueError(f"Minimum {min_points[period]} data points required for {period} aggregation")
            
        return True 