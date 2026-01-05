from faststream.redis import RedisBroker

from src.clients.redis_broker import redis_broker


async def get_broker() -> RedisBroker:
    return redis_broker
