from datetime import datetime
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field, validator
from .social_media import Platform
from .projects import ProjectStatus

class PostMetrics(BaseModel):
    likes: int = Field(ge=0)
    comments: int = Field(ge=0)
    shares: int = Field(ge=0)
    reach: int = Field(ge=0)
    
    @validator('*')
    def validate_non_negative(cls, v):
        if v < 0:
            raise ValueError("Metrics cannot be negative")
        return v

class AnalyticsMetrics(BaseModel):
    followers: int = Field(ge=0)
    engagement_rate: float = Field(ge=0, le=100)
    reach: int = Field(ge=0)
    impressions: int = Field(ge=0)
    
    @validator('reach')
    def validate_reach(cls, v, values):
        if 'impressions' in values and v > values['impressions']:
            raise ValueError("Reach cannot exceed impressions")
        return v

    @validator('impressions')
    def validate_impressions(cls, v, values):
        if 'reach' in values and values['reach'] > v:
            raise ValueError("Reach cannot exceed impressions")
        return v

    @validator('engagement_rate')
    def validate_engagement_rate(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Engagement rate must be between 0 and 100")
        return v

class Analytics(BaseModel):
    date: datetime
    metrics: AnalyticsMetrics
    
    @validator('date')
    def validate_date(cls, v):
        now = datetime.now()
        if v > now:
            raise ValueError("Analytics date cannot be in the future")
        return v

class PlatformMetrics(BaseModel):
    platform: Platform
    required_metrics: Set[str]
    
    class Config:
        use_enum_values = True

class DashboardStats(BaseModel):
    total_projects: int = Field(ge=0)
    projects_by_status: Dict[ProjectStatus, int]
    projects_by_platform: Dict[Platform, int]
    recent_projects: List[str]  # List of project IDs
    
    @validator('projects_by_status')
    def validate_status_totals(cls, v, values):
        if 'total_projects' in values and sum(v.values()) != values['total_projects']:
            raise ValueError("Status totals must match total projects")
        return v
    
    @validator('projects_by_platform')
    def validate_platform_totals(cls, v, values):
        if 'total_projects' in values and sum(v.values()) != values['total_projects']:
            raise ValueError("Platform totals must match total projects")
        return v

class AggregatedAnalytics(BaseModel):
    period: str = Field(..., regex='^(day|week|month)$')
    data_points: List[Analytics]
    
    @validator('data_points')
    def validate_data_points(cls, v, values):
        if not v:
            raise ValueError("Data points cannot be empty")
            
        if 'period' in values:
            expected_counts = {
                'day': 24,    # Hourly data points
                'week': 7,    # Daily data points
                'month': 31   # Monthly data points (max)
            }
            if values['period'] in ['day', 'week']:
                if len(v) != expected_counts[values['period']]:
                    raise ValueError(f"Expected {expected_counts[values['period']]} data points for {values['period']} period")
            elif len(v) > expected_counts[values['period']]:
                raise ValueError(f"Maximum {expected_counts[values['period']]} data points allowed for {values['period']} period")
        return v 