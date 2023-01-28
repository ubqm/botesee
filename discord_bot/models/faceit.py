from datetime import datetime
from typing import Literal, Union
from uuid import UUID

from pydantic import BaseModel, HttpUrl, Extra, Field

class Platforms(BaseModel):
    steam: str | None

    class Config:
        extra = Extra.allow


class Game(BaseModel):
    region: str
    game_player_id: str
    skill_level: int
    faceit_elo: int
    game_player_name: str
    skill_level_label: str
    regions: dict
    game_profile_id: str


class Games(BaseModel):
    csgo: Game
    valorant: Game

    class Config:
        extra = Extra.allow


class Settings(BaseModel):
    language: str


class PlayerDetails(BaseModel):
    player_id: UUID
    nickname: str
    avatar: HttpUrl | None
    country: str
    cover_image: HttpUrl | None
    platforms: Platforms
    games: Games
    settings: Settings
    friends_ids: list[UUID]
    new_steam_id: str
    steam_id_64: int
    steam_nickname: str
    memberships: list[str]
    faceit_url: HttpUrl
    membership_type: str
    cover_featured_image: HttpUrl | str | None
    infractions: dict


class Score(BaseModel):
    faction1: bool
    faction2: bool

class ResultsHistory(BaseModel):
    score: Score
    winner: Union[Literal["faction1", "faction2"]]


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

