import asyncio

from faststream import FastStream
from loguru import logger

from src import conf
from src.clients.faceit import faceit_client
from src.clients.models.rabbit.queues import QueueName
from src.clients.redis_broker import redis_broker
from src.db.repositories.statistics import WeeklyStatistics
from src.db.script import db_match_exists, db_match_finished
from src.discord_bot.discord_factory import discord_factory
from src.web.models.base import EventEnum
from src.web.models.events import MatchReady, WebhookMatch

faststream_app = FastStream(redis_broker)
discord_client = discord_factory(conf.ENV)


@faststream_app.on_startup
async def setup():
    sleep_time = 0
    while not discord_client.faceit_channel:
        sleep_time += 1
        logger.info(
            f"Waiting for discord bot to startup. Total sleep: {sleep_time} sec."
        )
        await asyncio.sleep(1)


@redis_broker.subscriber(QueueName.UPDATE_SCORE)
async def process_match_ready(match_ready: MatchReady) -> None:
    while True:
        await asyncio.sleep(20)
        match_details = await faceit_client.match_details(match_ready.payload.id)

        if match_details.finished_at:
            return

        await discord_client.update_score_for_match(
            match_details=match_details, match_ready=match_ready
        )


@redis_broker.subscriber(QueueName.WEEKLY_STATS)
async def process_weekly_stats() -> None:
    logger.info("Received message to process_weekly_stats")
    stats = await WeeklyStatistics().get_weekly_stats()
    await discord_client.post_weekly_stats(stats=stats)


@redis_broker.subscriber(QueueName.MATCHES)
async def process_match(match: WebhookMatch) -> None:
    match match.event:
        case EventEnum.READY | EventEnum.CONFIGURING:
            await discord_client.post_faceit_message_ready(match)
        case EventEnum.CANCELLED | EventEnum.ABORTED:
            await discord_client.post_faceit_message_aborted(match)
        case EventEnum.FINISHED:
            if await db_match_exists(match.payload.id):
                logger.info(
                    "Skipped processing of EventEnum.FINISHED "
                    "because Match is already in Database"
                )
                return None

            statistics = await faceit_client.match_stats(match.payload.id)
            await db_match_finished(match, statistics)
            await discord_client.post_faceit_message_finished(match)


async def main():
    await asyncio.gather(
        faststream_app.start(),
        discord_client.start(conf.DISCORD_TOKEN),
    )


if __name__ == "__main__":
    asyncio.run(main())
