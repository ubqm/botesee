from redis.asyncio import Redis

from src import conf


redis_client = Redis.from_url(url=conf.redis_string)
MATCHES_TTL = 60 * 60 * 24  # 24 hours


class RedisRepository:
    async def save_match(self, match_id: str, nick_elo: dict):
        r_key = f"matches:{match_id}"
        async with redis_client:
            await redis_client.hset(r_key, mapping=nick_elo)
            await redis_client.expire(r_key, MATCHES_TTL, nx=True)


redis_repo = RedisRepository()
