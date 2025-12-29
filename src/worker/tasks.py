import asyncio
import json

import httpx
from httpx import ReadTimeout
from loguru import logger
from pydantic import TypeAdapter
from taskiq import TaskiqScheduler
from taskiq.middlewares import SmartRetryMiddleware
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import RedisStreamBroker

from src import conf
from src.clients.faceit import faceit_client
from src.clients.models.rabbit.queues import QueueName
from src.clients.rabbit import RabbitClient
from src.db.repositories.statistics import WeeklyStatistics, WeeklyStats
from src.db.script import db_match_finished
from src.utils.shared_models import DetailsMatchDict
from src.web.dependencies import get_rabbit
from src.web.models.events import MatchFinished, MatchReady

broker = RedisStreamBroker(
    url=conf.redis_string,
).with_middlewares(
    SmartRetryMiddleware(
        default_retry_count=5,
        default_delay=5,
        use_jitter=True,
        use_delay_exponent=True,
        max_delay_exponent=60,
        types_of_exceptions=(ReadTimeout,),
    ),
)
scheduler = TaskiqScheduler(broker, sources=[LabelScheduleSource(broker)])


@broker.task()
async def match_score_update(match_ready: MatchReady) -> None:
    rabbit: RabbitClient = await get_rabbit()
    async with rabbit:
        while True:
            await asyncio.sleep(20)
            try:
                match_details = await faceit_client.match_details(
                    match_ready.payload.id
                )
            except httpx.PoolTimeout as e:
                logger.exception(f"{e}", exc_info=e)
            else:
                if match_details.finished_at:
                    break

                details_match_dict: DetailsMatchDict = DetailsMatchDict(
                    match_details=match_details, match_ready=match_ready
                )
                await rabbit.publish(
                    json.dumps(details_match_dict.model_dump_json()),
                    routing_key=QueueName.UPDATE_SCORE,
                )


@broker.task()
async def match_finished(match: MatchFinished) -> None:
    statistics = await faceit_client.match_stats(match.payload.id)
    await db_match_finished(match, statistics)
    rabbit: RabbitClient = await get_rabbit()
    async with rabbit:
        await rabbit.publish(
            message=match.model_dump_json(), routing_key=QueueName.MATCHES
        )


@broker.task(schedule=[{"cron": "59 23 * * sun", "cron_offset": "Europe/Minsk"}])
async def _weekly_stats() -> None:
    rabbit: RabbitClient = await get_rabbit()

    info = await WeeklyStatistics().get_weekly_stats()
    async with rabbit:
        await rabbit.publish(
            message=TypeAdapter(list[WeeklyStats]).dump_json(info).decode(),
            routing_key=QueueName.WEEKLY_STATS,
        )
