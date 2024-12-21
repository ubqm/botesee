from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class Platforms(BaseModel):
    steam: str | None = None

    model_config = ConfigDict(extra="allow")


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
    csgo: Game | None = None
    valorant: Game | None = None
    cs2: Game | None = None

    model_config = ConfigDict(extra="allow")


class Settings(BaseModel):
    language: str


class PlayerDetails(BaseModel):
    player_id: UUID
    nickname: str
    avatar: str
    country: str
    cover_image: str
    platforms: Platforms | None = None
    games: Games
    settings: Settings
    friends_ids: list[UUID] | list[str] | None = None
    new_steam_id: str
    steam_id_64: str
    steam_nickname: str
    memberships: list[str]
    faceit_url: HttpUrl
    membership_type: str
    cover_featured_image: str | None = None
    infractions: dict | None = None
