from uuid import UUID

from pydantic import BaseModel, Field


class Stats(BaseModel):
    rounds: int = Field(alias="Rounds")
    region: str = Field(alias="Region")
    first_half_score: int = Field(alias="First Half Score")
    result: bool = Field(alias="Result")
    assists: int = Field(alias="Assists")
    kd_ratio: float = Field(alias="K/D Ratio")
    player_id: UUID = Field(alias="Player Id")
    final_score: int = Field(alias="Final Score")
    hs: int = Field(alias="Headshots")
    ace: int = Field(alias="Penta Kills")
    match_id: str = Field(alias="Match Id")
    score: str = Field(alias="Score")
    second_half_score: int = Field(alias="Second Half Score")
    team_name: str = Field(alias="Team")
    triple: int = Field(alias="Triple Kills")
    kr_ratio: float = Field(alias="K/R Ratio")
    hs_p: int = Field(alias="Headshots %")
    winner: UUID | str = Field(alias="Winner")
    quadro: int = Field(alias="Quadro Kills")
    kills: int = Field(alias="Kills")
    deaths: int = Field(alias="Deaths")
    map_name: str = Field(alias="Map")
    mvps: int = Field(alias="MVPs")
    overtime_score: str = Field(alias="Overtime score")


class SingleGameStat(BaseModel):
    stats: Stats


class PlayerStatsCollection(BaseModel):
    items: list[SingleGameStat]
