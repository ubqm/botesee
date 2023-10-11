from uuid import UUID

from pydantic import BaseModel


class PlayerRegionStat(BaseModel):
    player_id: UUID
    nickname: str
    country: str
    position: int
    faceit_elo: int
    game_skill_level: int


class RegionStatistics(BaseModel):
    position: int
    items: list[PlayerRegionStat]
    start: str
    end: str
