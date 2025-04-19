import pytest
from datetime import datetime, timedelta
from app.schemas.social_media import Platform
from app.schemas.analytics import (
    PostMetrics, 
    AnalyticsMetrics, 
    Analytics, 
    DashboardStats, 
    PlatformMetrics,
    AggregatedAnalytics
)
from app.schemas.projects import ProjectStatus
from pydantic import ValidationError
from ..app.models.analytics import AnalyticsModel

class TestAnalytics:
    def test_metrics_calculation(self):
        # Test engagement rate calculation
        metrics = AnalyticsMetrics(
            followers=1000,
            engagement_rate=5.0,
            reach=500,
            impressions=1000
        )
        assert metrics.followers == 1000
        assert metrics.engagement_rate == 5.0
        
        # Test engagement rate validation
        with pytest.raises(ValidationError) as exc_info:
            AnalyticsMetrics(
                followers=1000,
                engagement_rate=101.0,
                reach=500,
                impressions=1000
            )
        assert "ensure this value is less than or equal to 100" in str(exc_info.value)

        # Test reach validation
        with pytest.raises(ValueError, match="Reach cannot exceed impressions"):
            metrics = AnalyticsMetrics(
                followers=1000,
                engagement_rate=5.0,
                reach=1500,
                impressions=1000
            )

    def test_analytics_date_range(self):
        # Test analytics for date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        analytics_list = []
        current_date = start_date
        
        while current_date <= end_date:
            analytics_list.append(
                Analytics(
                    date=current_date,
                    metrics=AnalyticsMetrics(
                        followers=1000,
                        engagement_rate=5.0,
                        reach=500,
                        impressions=1000
                    )
                )
            )
            current_date += timedelta(days=1)

        assert len(analytics_list) == 31
        assert analytics_list[0].date == start_date
        assert analytics_list[-1].date.date() == end_date.date()

        # Test future date validation
        future_date = datetime.now() + timedelta(days=1)
        with pytest.raises(ValueError, match="Analytics date cannot be in the future"):
            Analytics(
                date=future_date,
                metrics=AnalyticsMetrics(
                    followers=1000,
                    engagement_rate=5.0,
                    reach=500,
                    impressions=1000
                )
            )

    def test_post_metrics_validation(self):
        # Test negative values
        with pytest.raises(ValidationError) as exc_info:
            PostMetrics(
                likes=-1,
                comments=0,
                shares=0,
                reach=0
            )
        assert "ensure this value is greater than or equal to 0" in str(exc_info.value)

        # Test valid metrics
        metrics = PostMetrics(
            likes=100,
            comments=50,
            shares=25,
            reach=1000
        )
        
        # Calculate engagement rate
        engagement = (metrics.likes + metrics.comments + metrics.shares) / metrics.reach * 100
        assert 0 <= engagement <= 100

        # Test each field with negative value
        test_cases = {
            'likes': {'comments': 0, 'shares': 0, 'reach': 0},
            'comments': {'likes': 0, 'shares': 0, 'reach': 0},
            'shares': {'likes': 0, 'comments': 0, 'reach': 0},
            'reach': {'likes': 0, 'comments': 0, 'shares': 0}
        }

        for field, base_values in test_cases.items():
            with pytest.raises(ValidationError) as exc_info:
                PostMetrics(**{**base_values, field: -1})
            assert "ensure this value is greater than or equal to 0" in str(exc_info.value)

    def test_dashboard_stats_calculation(self):
        # Test dashboard statistics calculation
        stats = DashboardStats(
            total_projects=10,
            projects_by_status={
                ProjectStatus.DRAFT: 3,
                ProjectStatus.IN_PROGRESS: 4,
                ProjectStatus.COMPLETED: 2,
                ProjectStatus.ARCHIVED: 1
            },
            projects_by_platform={
                Platform.INSTAGRAM: 4,
                Platform.TWITTER: 2,
                Platform.FACEBOOK: 3,
                Platform.LINKEDIN: 1
            },
            recent_projects=["project1", "project2"]
        )

        # Verify totals match
        assert stats.total_projects == sum(stats.projects_by_status.values())
        assert stats.total_projects == sum(stats.projects_by_platform.values())

        # Verify all statuses are accounted for
        assert set(stats.projects_by_status.keys()) == set(ProjectStatus)
        
        # Verify all platforms are accounted for
        assert set(stats.projects_by_platform.keys()) == set(Platform)

        # Test invalid totals
        with pytest.raises(ValueError, match="Status totals must match total projects"):
            DashboardStats(
                total_projects=10,
                projects_by_status={
                    ProjectStatus.DRAFT: 3,
                    ProjectStatus.IN_PROGRESS: 4,
                    ProjectStatus.COMPLETED: 2,
                    ProjectStatus.ARCHIVED: 2  # Sum = 11
                },
                projects_by_platform={
                    Platform.INSTAGRAM: 4,
                    Platform.TWITTER: 2,
                    Platform.FACEBOOK: 3,
                    Platform.LINKEDIN: 1
                },
                recent_projects=[]
            )

        with pytest.raises(ValueError, match="Platform totals must match total projects"):
            DashboardStats(
                total_projects=10,
                projects_by_status={
                    ProjectStatus.DRAFT: 3,
                    ProjectStatus.IN_PROGRESS: 4,
                    ProjectStatus.COMPLETED: 2,
                    ProjectStatus.ARCHIVED: 1
                },
                projects_by_platform={
                    Platform.INSTAGRAM: 4,
                    Platform.TWITTER: 2,
                    Platform.FACEBOOK: 3,
                    Platform.LINKEDIN: 2  # Sum = 11
                },
                recent_projects=[]
            )

    def test_trend_analysis(self, mock_analytics_routes):
        # Test trend calculation
        response = mock_analytics_routes.get("/mock/analytics", params={"days": 30})
        assert response.status_code == 200
        data = response.json()

        # Calculate day-over-day growth
        for i in range(1, len(data)):
            current_day = data[i]["metrics"]["followers"]
            previous_day = data[i-1]["metrics"]["followers"]
            growth_rate = (current_day - previous_day) / previous_day * 100
            assert -100 <= growth_rate <= 100  # Reasonable growth range

        # Test invalid days parameter
        response = mock_analytics_routes.get("/mock/analytics", params={"days": 0})
        assert response.status_code == 200
        assert len(response.json()) == 1  # Should return at least current day

    def test_performance_metrics(self):
        # Test various performance calculations
        metrics_list = [
            AnalyticsMetrics(
                followers=1000 + i*100,
                engagement_rate=5.0,
                reach=500 + i*50,
                impressions=1000 + i*100
            )
            for i in range(7)  # Week of data
        ]

        # Test follower growth
        follower_growth = (metrics_list[-1].followers - metrics_list[0].followers)
        assert follower_growth >= 0

        # Test average engagement rate
        avg_engagement = sum(m.engagement_rate for m in metrics_list) / len(metrics_list)
        assert 0 <= avg_engagement <= 100

        # Test reach to impression ratio
        for metrics in metrics_list:
            reach_ratio = metrics.reach / metrics.impressions
            assert 0 <= reach_ratio <= 1

    def test_platform_specific_metrics(self, mock_analytics_routes):
        # Test platform-specific metric requirements
        platform_metrics = {
            Platform.INSTAGRAM: {"likes", "comments", "saves", "shares"},
            Platform.TWITTER: {"likes", "retweets", "replies", "quotes"},
            Platform.FACEBOOK: {"likes", "comments", "shares", "reactions"},
            Platform.LINKEDIN: {"likes", "comments", "shares", "clicks"}
        }

        for platform, required_metrics in platform_metrics.items():
            response = mock_analytics_routes.get(f"/mock/analytics/platform/{platform.name}")
            assert response.status_code == 200
            data = response.json()
            
            # Verify all required metrics are present
            assert all(metric in data["metrics"] for metric in required_metrics)

        # Test invalid platform
        response = mock_analytics_routes.get("/mock/analytics/platform/INVALID")
        assert response.status_code == 200
        assert response.json()["metrics"] == {}

    def test_platform_metrics_model(self):
        # Test PlatformMetrics model
        metrics = PlatformMetrics(
            platform=Platform.INSTAGRAM,
            required_metrics={"likes", "comments", "shares"}
        )
        assert metrics.platform == Platform.INSTAGRAM
        assert "likes" in metrics.required_metrics

        # Test enum values in config
        assert metrics.dict()["platform"] == Platform.INSTAGRAM.value

    def test_aggregated_analytics_validation(self):
        # Test data points validation for different periods
        now = datetime.now()
        hourly_points = [
            Analytics(
                date=now - timedelta(hours=i),
                metrics=AnalyticsMetrics(
                    followers=1000,
                    engagement_rate=5.0,
                    reach=500,
                    impressions=1000
                )
            )
            for i in range(24)
        ]

        # Test day period validation
        agg = AggregatedAnalytics(period="day", data_points=hourly_points)
        assert len(agg.data_points) == 24

        # Test week period validation
        with pytest.raises(ValueError):
            AggregatedAnalytics(period="week", data_points=hourly_points)

        # Test month period validation (max points)
        monthly_points = hourly_points * 2  # 48 points
        with pytest.raises(ValueError):
            AggregatedAnalytics(period="month", data_points=monthly_points)

def test_date_range_edge_cases():
    # Test future end date
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now() + timedelta(days=1)
    with pytest.raises(ValueError, match="End date cannot be in the future"):
        AnalyticsModel.validate_date_range(start_date, end_date)
    
    # Test start date after end date
    start_date = datetime.now()
    end_date = datetime.now() - timedelta(days=1)
    with pytest.raises(ValueError, match="Start date must be before end date"):
        AnalyticsModel.validate_date_range(start_date, end_date)
    
    # Test range exceeding 1 year
    start_date = datetime.now() - timedelta(days=400)
    end_date = datetime.now()
    with pytest.raises(ValueError, match="Date range cannot exceed 1 year"):
        AnalyticsModel.validate_date_range(start_date, end_date)

def test_aggregation_edge_cases():
    # Test daily aggregation with no data points
    with pytest.raises(ValueError, match="Minimum 1 data points required for day aggregation"):
        AnalyticsModel.validate_aggregation_period('day', [])
    
    # Test weekly aggregation with insufficient data points
    with pytest.raises(ValueError, match="Minimum 3 data points required for week aggregation"):
        AnalyticsModel.validate_aggregation_period('week', [1, 2])
    
    # Test monthly aggregation with insufficient data points
    with pytest.raises(ValueError, match="Minimum 7 data points required for month aggregation"):
        AnalyticsModel.validate_aggregation_period('month', [1, 2, 3]) 