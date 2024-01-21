from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class PlayerInfo(BaseModel):
    avatar: str
    faceit_url: str
    game_player_id: str
    game_player_name: str
    nickname: str
    player_id: UUID
    skill_level: int


class TeamHistory(BaseModel):
    avatar: str
    nickname: str
    players: list[PlayerInfo]
    team_id: str = ""
    type: str


class TeamFactions(BaseModel):
    faction1: TeamHistory
    faction2: TeamHistory


class Score(BaseModel):
    faction1: bool | str | None = None
    faction2: bool | str | None = None


class ResultsHistory(BaseModel):
    score: Score
    winner: Literal["faction1", "faction2"]


class MatchHistory(BaseModel):
    competition_id: UUID | str | None = None
    competition_name: str
    competition_type: str
    faceit_url: HttpUrl
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
