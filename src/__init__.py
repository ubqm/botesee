from datetime import timedelta
from enum import StrEnum

from aiohttp_client_cache import RedisBackend
from pydantic_settings import BaseSettings


class EnvType(StrEnum):
    DEV: str = "dev"
    PROD: str = "prod"


class Settings(BaseSettings):
    ENV: EnvType = EnvType.DEV
    DISCORD_TOKEN: str = ""
    STEAM_TOKEN: str = ""
    FACEIT_TOKEN: str = ""
    FACEIT_WEBHOOK_AUTH: str = ""
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "bot"
    RABBIT_HOST: str = ""
    RABBIT_PORT: int = 5672
    RABBIT_USER: str = ""
    RABBIT_PASSWORD: str = ""
    REDIS_HOST: str = ""
    REDIS_PORT: int = 6379
    START_BALANCE: int = 100

    @property
    def db_string(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def rmq_string(self) -> str:
        return f"amqp://{self.RABBIT_USER}:{self.RABBIT_PASSWORD}@{self.RABBIT_HOST}:{self.RABBIT_PORT}"

    @property
    def redis_string(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


conf = Settings()


redis_cache = RedisBackend(cache_name="aiohttp-cache", address=conf.redis_string, expire_after=timedelta(days=30))
