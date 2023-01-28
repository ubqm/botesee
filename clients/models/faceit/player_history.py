from datetime import datetime
from typing import Union, Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class PlayerInfo(BaseModel):
    avatar: HttpUrl | None
    faceit_url: HttpUrl | None
    game_player_id: str
    game_player_name: str
    nickname: str
    player_id: UUID
    skill_level: int


class TeamHistory(BaseModel):
    avatar: HttpUrl | None
    nickname: str
    players: list[PlayerInfo]
    team_id: UUID
    type: str


class TeamFactions(BaseModel):
    faction1: TeamHistory
    faction2: TeamHistory


class Score(BaseModel):
    faction1: bool
    faction2: bool


class ResultsHistory(BaseModel):
    score: Score
    winner: Union[Literal["faction1", "faction2"]]


class MatchHistory(BaseModel):
    competition_id: UUID
    competition_name: str
    competition_type: str
    faceit_url: HttpUrl | None
    finished_at: datetime
    game_id: str
    game_mode: str
    match_id: str
    match_type: str
    max_players: int
    organizer_id: str
    playing_players: list[UUID]
    region: str
    results: ResultsHistory
    started_at: datetime
    status: str
    teams: TeamFactions
    teams_size: int


class PlayerHistory(BaseModel):
    items: list[MatchHistory]
    end: int
    from_: int = Field(alias="from")
    start: int
    to: int
