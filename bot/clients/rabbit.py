import asyncio
import json

import aio_pika
from loguru import logger
from pydantic import parse_obj_as

from bot.discord_bot.client import DiscordClient
from bot.web.models.base import EventEnum
from bot.web.models.events import WebhookMatch


class RabbitClient:
    def __init__(self, host: str, port: int, user: str, password: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    async def publish(self, message: str, routing_key: str = "matches") -> None:
        connection = await aio_pika.connect_robust(
            host=self.host,
            port=self.port,
            login=self.user,
            password=self.password,
        )

        async with connection:
            channel = await connection.channel()
            await channel.declare_queue(routing_key, durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(body=message.encode()),
                routing_key=routing_key,
            )


class RabbitWorker:
    # Step #1
    def __init__(self, host: str, port: int, user: str, password: str, discord: DiscordClient):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.discord = discord

    async def _process_match(self, match: WebhookMatch) -> None:
        match match.event:
            case EventEnum.READY | EventEnum.CONFIGURING:
                await self.discord.post_faceit_message_ready(match)
            case EventEnum.CANCELLED | EventEnum.ABORTED:
                await self.discord.post_faceit_message_aborted(match)
            case EventEnum.FINISHED:
                await self.discord.post_faceit_message_finished(match)

    async def consume(self, queue_name: str = "matches"):
        logger.info("Start consuming from rabbit...")
        sleep_time: int = 0
        while not self.discord.faceit_channel:
            sleep_time += 1
            logger.info(f"Waiting for discord bot to startup. Total sleep: {sleep_time} sec.")
            await asyncio.sleep(1)
        connection = await aio_pika.connect_robust(
            host=self.host,
            port=self.port,
            login=self.user,
            password=self.password,
        )

        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(queue_name, durable=True)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    message: aio_pika.IncomingMessage  # type: ignore
                    match = parse_obj_as(WebhookMatch, json.loads(message.body.decode()))
                    try:
                        await self._process_match(match)
                    except Exception as ex:
                        logger.error(ex)
                    else:
                        await message.ack()
