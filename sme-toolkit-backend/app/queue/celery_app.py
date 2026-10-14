"""
Celery configuration for async task processing
"""

from celery import Celery
from celery.schedules import crontab
from kombu import Queue, Exchange
import os

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery_app = Celery(
    "sme_toolkit",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    broker_connection_retry_on_startup=True,
)

default_exchange = Exchange("default", type="direct")

celery_app.conf.task_queues = [
    Queue("default", default_exchange, routing_key="task.default"),
    Queue("ai_llm", default_exchange, routing_key="task.ai.llm"),
    Queue("ai_image", default_exchange, routing_key="task.ai.image"),
    Queue("ai_video", default_exchange, routing_key="task.ai.video"),
    Queue("analytics", default_exchange, routing_key="task.analytics"),
    Queue("notifications", default_exchange, routing_key="task.notifications"),
    Queue("scheduled", default_exchange, routing_key="task.scheduled"),
    Queue("marketplace", default_exchange, routing_key="task.marketplace"),
]

celery_app.conf.task_routes = {
    "app.tasks.ai_tasks.generate_text": {"queue": "ai_llm"},
    "app.tasks.ai_tasks.generate_image": {"queue": "ai_image"},
    "app.tasks.ai_tasks.generate_video": {"queue": "ai_video"},
    "app.tasks.ai_tasks.execute_agent": {"queue": "ai_llm"},
    "app.tasks.analytics_tasks.*": {"queue": "analytics"},
    "app.tasks.notification_tasks.*": {"queue": "notifications"},
    "app.tasks.scheduled_tasks.*": {"queue": "scheduled"},
    "app.tasks.marketplace_tasks.*": {"queue": "marketplace"},
}

celery_app.conf.beat_schedule = {
    "reset-daily-quotas": {
        "task": "app.tasks.scheduled_tasks.reset_daily_quotas",
        "schedule": crontab(hour=0, minute=0),
    },
    "cleanup-expired-sessions": {
        "task": "app.tasks.scheduled_tasks.cleanup_sessions",
        "schedule": crontab(hour=3, minute=0),
    },
    "calculate-daily-metrics": {
        "task": "app.tasks.analytics_tasks.calculate_daily_metrics",
        "schedule": crontab(hour=1, minute=0),
    },
    "health-check-providers": {
        "task": "app.tasks.monitoring_tasks.check_provider_health",
        "schedule": 300.0,
    },
    "sync-marketplace-data": {
        "task": "app.tasks.marketplace_tasks.sync_all_connections",
        "schedule": 1800.0,
    },
    "refresh-cache-warmup": {
        "task": "app.tasks.cache_tasks.warmup_cache",
        "schedule": crontab(hour=6, minute=0),
    },
}

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=7200,
    task_soft_time_limit=6600,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=500,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,
    task_max_retries=3,
    result_expires=86400,
    worker_concurrency=4,
)

celery_app.autodiscover_tasks([
    "app.tasks.ai_tasks",
    "app.tasks.analytics_tasks",
    "app.tasks.notification_tasks",
    "app.tasks.scheduled_tasks",
    "app.tasks.marketplace_tasks",
    "app.tasks.monitoring_tasks",
    "app.tasks.cache_tasks",
])
