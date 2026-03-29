from typing import Any

from redis.asyncio import Redis

from src import conf


class RedisRepository:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.MATCHES_TTL = 60 * 60 * 24  # 24 hours

    async def save_match(self, match_id: str, nick_elo: dict[str, int]) -> None:
        r_key = f"matches:{match_id}"
        async with self.redis_client as rc:
            await rc.hset(r_key, mapping=nick_elo)
            await rc.expire(r_key, self.MATCHES_TTL, nx=True)

    async def get_match_elo(self, match_id: str) -> dict[str, int]:
        r_key = f"matches:{match_id}"
        async with self.redis_client as rc:
            redis_data: dict[bytes:bytes] = await rc.hgetall(r_key)
            return {k.decode(): int(v) for k, v in redis_data.items()}

    async def match_exists(self, match_id: str) -> Any | None:
        r_key = f"matches:{match_id}"
        async with self.redis_client as rc:
            return await rc.exists(r_key)


redis_repo = RedisRepository(redis_client=Redis.from_url(url=conf.redis_string))
