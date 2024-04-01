from redis.asyncio import Redis

from src import conf


redis_client = Redis.from_url(url=conf.redis_string)
MATCHES_TTL = 60 * 60 * 24  # 24 hours


class RedisRepository:
    async def save_match(self, match_id: str, nick_elo: dict[str, int]) -> None:
        r_key = f"matches:{match_id}"
        async with redis_client:
            await redis_client.hset(r_key, mapping=nick_elo)
            await redis_client.expire(r_key, MATCHES_TTL, nx=True)

    async def get_match_elo(self, match_id: str) -> dict[str, int]:
        r_key = f"matches:{match_id}"
        async with redis_client:
            redis_data: dict[bytes:bytes] = await redis_client.hgetall(r_key)
            return {str(k): int(v) for k, v in redis_data}


redis_repo = RedisRepository()
