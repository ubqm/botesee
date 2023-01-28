from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class Score(BaseModel):
    faction1: int
    faction2: int


class Results(BaseModel):
    winner: str
    score: Score


class PlayerDetails(BaseModel):
    player_id: UUID
    nickname: str
    avatar: HttpUrl | None
    membership: str
    game_player_id: str
    game_player_name: str
    game_skill_level: int
    anticheat_required: bool


class TeamDetails(BaseModel):
    faction_id: UUID
    leader: UUID
    avatar: HttpUrl | None
    roster: list[PlayerDetails]
    substituted: bool
    name: str
    type: str


class TeamsFaction(BaseModel):
    faction1: TeamDetails
    faction2: TeamDetails


class MapEntity(BaseModel):
    name: str
    class_name: str
    game_map_id: str
    guid: str
    image_lg: HttpUrl | None
    image_sm: HttpUrl | None


class MapVoting(BaseModel):
    entities: list[MapEntity]
    pick: list[str]


class LocationEntity(BaseModel):
    name: str
    class_name: str
    game_location_id: str
    guid: str
    image_lg: HttpUrl | None
    image_sm: HttpUrl | None


class LocationVoting(BaseModel):
    entities: list[LocationEntity]
    pick: list[str]


class Voting(BaseModel):
    map: MapVoting
    voted_entity_types: list[str]
    location: LocationVoting


class MatchDetails(BaseModel):
    match_id: str
    version: int
    game: str
    region: str
    competition_id: UUID
    competition_type: str
    organizer_id: str
    teams: TeamsFaction
    voting: Voting
    calculate_elo: bool
    configured_at: datetime
    started_at: datetime
    finished_at: datetime
    demo_url: list[HttpUrl] | None
    chat_room_id: str
    best_of: int
    results: Results
    status: str
    faceit_url: HttpUrl
