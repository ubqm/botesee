from enum import StrEnum

from pydantic import BaseSettings


class EnvType(StrEnum):
    DEV: str = "dev"
    PROD: str = "prod"


class Settings(BaseSettings):
    ENV: EnvType
    DISCORD_TOKEN: str = ""
    STEAM_TOKEN: str = ""
    FACEIT_TOKEN: str = ""
    FACEIT_HEADERS: dict[str, str] | None = None
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = ""
    DB_PORT: int = 5432
    DB_NAME: str = ""
    RABBIT_HOST: str = ""
    RABBIT_PORT: int = 5672
    RABBIT_USER: str = ""
    RABBIT_PASSWORD: str = ""

    @property
    def pg_string(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


conf = Settings()
conf.FACEIT_HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {conf.FACEIT_TOKEN}",
}

if __name__ == "__main__":
    print(conf)
