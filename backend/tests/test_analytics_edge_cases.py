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

class TestAnalyticsEdgeCases:
    def test_metrics_edge_cases(self):
        """Test edge cases for analytics metrics."""
        # Test maximum values
        metrics = AnalyticsMetrics(
            followers=2**31 - 1,  # Max 32-bit integer
            engagement_rate=100.0,  # Maximum allowed
            reach=2**31 - 1,
            impressions=2**31 - 1
        )
        assert metrics.followers == 2**31 - 1
        assert metrics.engagement_rate == 100.0

        # Test minimum values
        metrics = AnalyticsMetrics(
            followers=0,
            engagement_rate=0.0,
            reach=0,
            impressions=0
        )
        assert metrics.followers == 0
        assert metrics.engagement_rate == 0.0

        # Test floating point precision
        metrics = AnalyticsMetrics(
            followers=1000,
            engagement_rate=0.0001,  # Very small engagement rate
            reach=500,
            impressions=1000
        )
        assert metrics.engagement_rate == 0.0001

    def test_date_range_edge_cases(self):
        """Test edge cases for date ranges."""
        now = datetime.now()

        # Test single day range
        analytics = Analytics(
            date=now - timedelta(seconds=1),
            metrics=AnalyticsMetrics(
                followers=1000,
                engagement_rate=5.0,
                reach=500,
                impressions=1000
            )
        )
        assert analytics.date < now

        # Test exactly current time
        with pytest.raises(ValueError):
            Analytics(
                date=now + timedelta(microseconds=1),
                metrics=AnalyticsMetrics(
                    followers=1000,
                    engagement_rate=5.0,
                    reach=500,
                    impressions=1000
                )
            )

        # Test date at start of day
        start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        analytics = Analytics(
            date=start_of_day,
            metrics=AnalyticsMetrics(
                followers=1000,
                engagement_rate=5.0,
                reach=500,
                impressions=1000
            )
        )
        assert analytics.date.hour == 0
        assert analytics.date.minute == 0
        assert analytics.date.second == 0

    def test_post_metrics_edge_cases(self):
        """Test edge cases for post metrics."""
        # Test zero engagement
        metrics = PostMetrics(
            likes=0,
            comments=0,
            shares=0,
            reach=1
        )
        engagement = (metrics.likes + metrics.comments + metrics.shares) / metrics.reach * 100
        assert engagement == 0

        # Test 100% engagement (every user interacted in every way)
        metrics = PostMetrics(
            likes=1000,
            comments=1000,
            shares=1000,
            reach=1000
        )
        engagement = (metrics.likes + metrics.comments + metrics.shares) / metrics.reach * 100
        assert engagement == 300  # 100% for each interaction type

        # Test single user reach
        metrics = PostMetrics(
            likes=1,
            comments=1,
            shares=1,
            reach=1
        )
        assert metrics.reach == 1

    def test_dashboard_stats_edge_cases(self):
        """Test edge cases for dashboard statistics."""
        # Test empty project list
        stats = DashboardStats(
            total_projects=0,
            projects_by_status={status: 0 for status in ProjectStatus},
            projects_by_platform={platform: 0 for platform in Platform},
            recent_projects=[]
        )
        assert stats.total_projects == 0
        assert sum(stats.projects_by_status.values()) == 0
        assert sum(stats.projects_by_platform.values()) == 0

        # Test single platform dominance
        dominant_platform = Platform.INSTAGRAM
        stats = DashboardStats(
            total_projects=100,
            projects_by_status={
                ProjectStatus.DRAFT: 100,
                ProjectStatus.IN_PROGRESS: 0,
                ProjectStatus.COMPLETED: 0,
                ProjectStatus.ARCHIVED: 0
            },
            projects_by_platform={
                Platform.INSTAGRAM: 100,
                Platform.TWITTER: 0,
                Platform.FACEBOOK: 0,
                Platform.LINKEDIN: 0
            },
            recent_projects=["project1"]
        )
        assert stats.projects_by_platform[dominant_platform] == stats.total_projects

    def test_aggregation_edge_cases(self):
        """Test edge cases for data aggregation."""
        now = datetime.now()

        # Test minimum required points
        min_points = {
            "day": 24,
            "week": 7,
            "month": 1
        }

        for period, required_points in min_points.items():
            points = [
                Analytics(
                    date=now - timedelta(hours=i) if period == "day" else timedelta(days=i),
                    metrics=AnalyticsMetrics(
                        followers=1000,
                        engagement_rate=5.0,
                        reach=500,
                        impressions=1000
                    )
                )
                for i in range(required_points)
            ]

            if period in ["day", "week"]:
                # Test exact number of required points
                agg = AggregatedAnalytics(period=period, data_points=points)
                assert len(agg.data_points) == required_points

                # Test too few points
                with pytest.raises(ValueError):
                    AggregatedAnalytics(period=period, data_points=points[:-1])

            # Test maximum points for month
            if period == "month":
                # Test maximum points
                max_points = [
                    Analytics(
                        date=now - timedelta(days=i),
                        metrics=AnalyticsMetrics(
                            followers=1000,
                            engagement_rate=5.0,
                            reach=500,
                            impressions=1000
                        )
                    )
                    for i in range(31)
                ]
                agg = AggregatedAnalytics(period=period, data_points=max_points)
                assert len(agg.data_points) == 31

                # Test exceeding maximum points
                with pytest.raises(ValueError):
                    AggregatedAnalytics(
                        period=period,
                        data_points=max_points + [max_points[0]]
                    )

    def test_platform_metrics_edge_cases(self):
        """Test edge cases for platform-specific metrics."""
        # Test empty metrics set
        with pytest.raises(ValueError):
            PlatformMetrics(
                platform=Platform.INSTAGRAM,
                required_metrics=set()
            )

        # Test all possible metrics
        all_metrics = {
            "likes",
            "comments",
            "shares",
            "reach",
            "impressions",
            "saves",
            "clicks",
            "reactions"
        }
        metrics = PlatformMetrics(
            platform=Platform.INSTAGRAM,
            required_metrics=all_metrics
        )
        assert len(metrics.required_metrics) == len(all_metrics)

        # Test platform-specific required metrics
        platform_required = {
            Platform.INSTAGRAM: {"likes", "comments"},
            Platform.TWITTER: {"likes", "retweets"},
            Platform.FACEBOOK: {"likes", "reactions"},
            Platform.LINKEDIN: {"likes", "clicks"}
        }

        for platform, required in platform_required.items():
            metrics = PlatformMetrics(
                platform=platform,
                required_metrics=required
            )
            assert required.issubset(metrics.required_metrics) 