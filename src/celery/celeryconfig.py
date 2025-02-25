from celery.schedules import crontab

celery_config = {
    "timezone": "Europe/Minsk",
    "beat_schedule": {
        "src.celery.tasks.weekly_stats": {
            "task": "src.celery.tasks.weekly_stats",
            "schedule": crontab(hour="23", minute="59", day_of_week="sun"),
        },
    },
    "task_reject_on_worker_lost": True,
    "task_acks_late": True,
    "broker_connection_retry_on_startup": True,
}
