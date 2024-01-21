from pydantic import BaseModel, Field


class AchievementEntity(BaseModel):
    name: str
    achieved: bool


class GameStatEntity(BaseModel):
    name: str
    value: int


class PlayerStatistics(BaseModel):
    steam_id: str = Field(alias="steamID")
    game: str = Field(alias="gameName")
    stats: list[GameStatEntity]
    achievements: list[AchievementEntity]


class UserAppStatistics(BaseModel):
    playerstats: PlayerStatistics | None = None

    def __bool__(self) -> bool:
        return bool(self.playerstats)
