import asyncio

import aiohttp
from aiohttp.client_exceptions import ClientConnectorError
from celery import Celery
from loguru import logger

from bot import conf
from bot.clients.faceit import FaceitClient
from bot.clients.models.rabbit.queues import QueueName
from bot.clients.rabbit import RabbitClient

app = Celery(broker=conf.rmq_string)


async def _score_update(match_id: str) -> None:
    rabbit = RabbitClient(conf.RABBIT_HOST, conf.RABBIT_PORT, conf.RABBIT_USER, conf.RABBIT_PASSWORD)
    while True:
        await asyncio.sleep(20)
        async with aiohttp.ClientSession(headers=conf.FACEIT_HEADERS) as session:
            try:
                match_details = await FaceitClient.match_details(session, match_id)
            except ClientConnectorError as e:
                logger.error(e)
            else:
                if match_details.finished_at:
                    break

            await rabbit.publish(match_details.json(), routing_key=QueueName.UPDATE_SCORE)


@app.task
def match_score_update(match_id: str) -> None:
    logger.info(f"Started score fetching for {match_id}")
    asyncio.run(_score_update(match_id))
    logger.info(f"Stopped score fetching for {match_id}")
