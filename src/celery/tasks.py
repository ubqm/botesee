import asyncio

import httpx
from celery import Celery
from loguru import logger

from src import conf
from src.clients.faceit import faceit_client
from src.clients.models.rabbit.queues import QueueName
from src.clients.rabbit import RabbitClient
from src.db.script import db_match_finished
from src.web.dependencies import get_rabbit
from src.web.models.events import MatchFinished

app = Celery(broker=conf.rmq_string)
event_loop = asyncio.new_event_loop()


async def _score_update(match_id: str) -> None:
    rabbit = RabbitClient(
        conf.RABBIT_HOST, conf.RABBIT_PORT, conf.RABBIT_USER, conf.RABBIT_PASSWORD
    )
    while True:
        await asyncio.sleep(20)
        try:
            match_details = await faceit_client.match_details(match_id)
        except httpx.PoolTimeout as e:
            logger.exception(f"{e}", exc_info=e)
        else:
            if match_details.finished_at:
                break

            await rabbit.publish(
                match_details.json(), routing_key=QueueName.UPDATE_SCORE
            )


@app.task
def match_score_update(match_id: str) -> None:
    logger.info(f"Started score fetching for {match_id}")
    event_loop.run_until_complete(_score_update(match_id))
    logger.info(f"Stopped score fetching for {match_id}")


async def _match_finished(match: MatchFinished) -> None:
    statistics = await faceit_client.match_stats(match.payload.id)
    await db_match_finished(match, statistics)
    rabbit: RabbitClient = await get_rabbit()
    await rabbit.publish(message=match.model_dump_json(), routing_key=QueueName.MATCHES)


@app.task
def match_finished(match_finished_dict: dict) -> None:
    match = MatchFinished(**match_finished_dict)
    logger.info(f"Match finished {match.payload.id}")
    event_loop.run_until_complete(_match_finished(match))
