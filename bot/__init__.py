from pydantic import BaseSettings


class Settings(BaseSettings):
    DISCORD_TOKEN: str
    STEAM_TOKEN: str
    FACEIT_TOKEN: str
    FACEIT_HEADERS: dict[str, str] | None
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    RABBIT_HOST: str
    RABBIT_PORT: int
    RABBIT_USER: str
    RABBIT_PASSWORD: str

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


conf = Settings()
conf.FACEIT_HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {conf.FACEIT_TOKEN}",
}

if __name__ == "__main__":
    print(conf)
