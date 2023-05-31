import asyncio

from tortoise import run_async

from models import Player, Match, Elo
from init import init


async def get_players():
    await Player.all()


if __name__ == '__main__':
    run_async(init())
    res = run_async(get_players())
    print(res)
