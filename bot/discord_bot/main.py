import asyncio

from bot.clients.rabbit import RabbitWorker
from bot.discord_bot import conf
from bot.discord_bot.client import discord_client


async def main():
    rabbit = RabbitWorker(
        conf.RABBIT_HOST,
        conf.RABBIT_PORT,
        conf.RABBIT_USER,
        conf.RABBIT_PASSWORD,
        discord_client,
        asyncio.get_event_loop(),
    )

    await asyncio.gather(
        rabbit.consume(),
        discord_client.start(conf.DISCORD_TOKEN),
    )


if __name__ == "__main__":
    asyncio.run(main())
