"""
Celery application configuration.

This module configures Celery for background task processing with Redis
as the message broker and result backend.
"""

from celery import Celery
from config.settings import get_settings
import logging

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create Celery app
celery_app = Celery(
    "veriglow",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["tasks.analysis_tasks"]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },
    
    # Task execution settings
    task_track_started=True,
    task_time_limit=300,  # 5 minutes hard limit
    task_soft_time_limit=240,  # 4 minutes soft limit
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Task routing
    task_routes={
        "tasks.analysis_tasks.analyze_text_async": {"queue": "analysis"},
        "tasks.analysis_tasks.batch_analyze_async": {"queue": "batch"},
        "tasks.analysis_tasks.scrape_and_analyze_async": {"queue": "scraping"},
    },
    
    # Task priority
    task_default_priority=5,
    
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Task annotations for specific configurations
celery_app.conf.task_annotations = {
    "tasks.analysis_tasks.analyze_text_async": {
        "rate_limit": "100/m",  # 100 tasks per minute
    },
    "tasks.analysis_tasks.batch_analyze_async": {
        "rate_limit": "10/m",  # 10 batch tasks per minute
    },
    "tasks.analysis_tasks.scrape_and_analyze_async": {
        "rate_limit": "50/m",  # 50 scraping tasks per minute
    },
}

logger.info("Celery app configured successfully")


if __name__ == "__main__":
    celery_app.start()
