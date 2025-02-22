from celery.schedules import crontab

celery_config = {
    "timezone": "Europe/Minsk",
    "beat_schedule": {
        "src.celery.tasks.weekly_stats": {
            "task": "src.celery.tasks.weekly_stats",
            "schedule": crontab(hour="6", day_of_week="1"),
        },
    },
}
