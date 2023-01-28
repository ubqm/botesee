from uuid import UUID

from pydantic import BaseModel, HttpUrl, Extra


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
    valorant: Game | None

    class Config:
        extra = Extra.allow


class Settings(BaseModel):
    language: str


class PlayerDetails(BaseModel):
    player_id: UUID
    nickname: str
    avatar: str
    country: str
    cover_image: str
    platforms: Platforms
    games: Games
    settings: Settings
    friends_ids: list[UUID] | None
    new_steam_id: str
    steam_id_64: int
    steam_nickname: str
    memberships: list[str]
    faceit_url: HttpUrl
    membership_type: str
    cover_featured_image: str | None
    infractions: dict | None
