"""Celery configuration module."""

from datetime import timedelta

# Broker settings
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'

# Task settings
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True

# Task execution settings
task_time_limit = 3600  # 1 hour
task_soft_time_limit = 3300  # 55 minutes
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 100

# Queue settings
task_default_queue = 'default'
task_queues = {
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
    'high_priority': {
        'exchange': 'high_priority',
        'routing_key': 'high_priority',
    },
    'low_priority': {
        'exchange': 'low_priority',
        'routing_key': 'low_priority',
    },
}

# Task routing
task_routes = {
    "app.tasks.generate_content": {"queue": "high_priority"},
    "app.tasks.schedule_posts": {"queue": "default"},
    "app.tasks.process_analytics": {"queue": "low_priority"},
    "app.tasks.process_bulk_operations": {"queue": "high_priority"},
}

# Result settings
result_expires = 3600  # Results expire after 1 hour
task_ignore_result = False  # Store task results

# Retry settings
task_publish_retry = True
task_publish_retry_policy = {
    "max_retries": 3,
    "interval_start": 0,
    "interval_step": 0.2,
    "interval_max": 0.5,
}

# Logging
worker_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
worker_task_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s"

# Security settings
security_key = "your-security-key"
task_track_started = True

# Rate limiting
task_default_rate_limit = "1000/m"  # Default rate limit
task_annotations = {
    "app.tasks.generate_content": {"rate_limit": "100/m"},
    "app.tasks.process_analytics": {"rate_limit": "50/m"},
}

# Error emails
send_task_error_emails = True
admins = (("Admin", "admin@example.com"),)

# Beat schedule settings
beat_schedule = {
    'cleanup-old-data': {
        'task': 'app.tasks.cleanup_old_data',
        'schedule': timedelta(days=1),
        'args': (30,),  # Keep last 30 days of data
    },
    'sync-external-data': {
        'task': 'app.tasks.sync_external_data',
        'schedule': timedelta(hours=1),
    },
    'generate-daily-report': {
        'task': 'app.tasks.generate_report',
        'schedule': timedelta(days=1),
    },
}
