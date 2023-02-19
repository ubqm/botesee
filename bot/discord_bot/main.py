import asyncio
import sys
import time
from threading import Thread
import discord
from loguru import logger
#
from bot.clients.rabbit import RabbitWorker
from bot.discord_bot import conf
from bot.discord_bot.client import DiscordClient


async def main():
    intents = discord.Intents.all()
    discord_bot = DiscordClient(faceit_channel_id=828940900033626113, intents=intents)
    rabbit = RabbitWorker(conf.RABBIT_HOST, conf.RABBIT_PORT, conf.RABBIT_USER, conf.RABBIT_PASSWORD, discord_bot)

    await asyncio.gather(
        rabbit.consume(),
        discord_bot.start(conf.DISCORD_TOKEN),
    )


if __name__ == '__main__':
    asyncio.run(main())
