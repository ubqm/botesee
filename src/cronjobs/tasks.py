from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_faststream import BrokerWrapper

from src.clients.models.rabbit.queues import QueueName
from src.clients.redis_broker import redis_broker

taskiq_broker = BrokerWrapper(redis_broker)

taskiq_broker.task(
    message=None,
    channel=QueueName.WEEKLY_STATS,
    schedule=[
        {
            "cron": "59 23 * * sun",
        }
    ],
    task_name="weekly_stats_cron",
)

scheduler = TaskiqScheduler(taskiq_broker, sources=[LabelScheduleSource(taskiq_broker)])
