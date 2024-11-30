import asyncio
import json
import logging

import httpx
from celery import Celery
from loguru import logger

from src import conf
from src.clients.faceit import faceit_client
from src.clients.models.rabbit.queues import QueueName
from src.clients.rabbit import RabbitClient
from src.db.script import db_match_finished
from src.utils.shared_models import DetailsMatchDict
from src.web.dependencies import get_rabbit
from src.web.models.events import MatchFinished, MatchReady

app = Celery(broker=conf.redis_string)
event_loop = asyncio.new_event_loop()
logging.getLogger("httpx").propagate = True


async def _score_update(match_ready: MatchReady) -> None:
    rabbit = await get_rabbit()
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


@app.task
def match_score_update(match_ready_dict: dict) -> None:
    match_ready = MatchReady(**match_ready_dict)
    logger.info(f"Started score fetching for {match_ready.payload.id}")
    event_loop.run_until_complete(_score_update(match_ready))
    logger.info(f"Stopped score fetching for {match_ready.payload.id}")


async def _match_finished(match: MatchFinished) -> None:
    statistics = await faceit_client.match_stats(match.payload.id)
    await db_match_finished(match, statistics)
    rabbit: RabbitClient = await get_rabbit()
    async with rabbit:
        await rabbit.publish(
            message=match.model_dump_json(), routing_key=QueueName.MATCHES
        )


@app.task
def match_finished(match_finished_dict: dict) -> None:
    match = MatchFinished(**match_finished_dict)
    logger.info(f"Match finished {match.payload.id}")
    event_loop.run_until_complete(_match_finished(match))
