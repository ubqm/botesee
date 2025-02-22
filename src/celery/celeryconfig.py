celery_config = {
    "timezone": "Europe/Minsk",
    "beat_schedule": {
        "weekly_stats": {
            "task": "tasks.weekly_stats",
            "schedule": 30,  # crontab(hour="6", day_of_week="1"),
        },
    },
}
