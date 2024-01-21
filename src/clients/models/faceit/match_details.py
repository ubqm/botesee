from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class Score(BaseModel):
    faction1: int | None = None
    faction2: int | None = None


class Results(BaseModel):
    winner: str
    score: Score


class PlayerDetailsFromMatch(BaseModel):
    player_id: UUID
    nickname: str
    avatar: str
    membership: str
    game_player_id: str
    game_player_name: str
    game_skill_level: int
    anticheat_required: bool


class FactionTeamSkillLevelRange(BaseModel):
    min: int
    max: int


class FactionTeamSkillLevel(BaseModel):
    average: int
    range: FactionTeamSkillLevelRange


class FactionTeamStats(BaseModel):
    win_probabibility: float | None = None
    skill_level: FactionTeamSkillLevel | None = None
    rating: int


class TeamDetails(BaseModel):
    faction_id: UUID
    leader: UUID
    avatar: str
    roster: list[PlayerDetailsFromMatch]
    stats: FactionTeamStats | None = None
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
    image_lg: str
    image_sm: str


class MapVoting(BaseModel):
    entities: list[MapEntity]
    pick: list[str]


class LocationEntity(BaseModel):
    name: str
    class_name: str
    game_location_id: str
    guid: str
    image_lg: str
    image_sm: str


class LocationVoting(BaseModel):
    entities: list[LocationEntity]
    pick: list[str]


class Voting(BaseModel):
    map: MapVoting
    voted_entity_types: list[str]
    location: LocationVoting | None = None


class MatchDetails(BaseModel):
    match_id: str
    version: int
    game: str
    region: str
    competition_id: UUID
    competition_type: str
    organizer_id: str
    teams: TeamsFaction
    voting: Voting | None = None
    calculate_elo: bool
    configured_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    demo_url: list[str] | None = None
    chat_room_id: str
    best_of: int
    results: Results | None = None
    status: str
    faceit_url: HttpUrl

    @property
    def current_score(self) -> str:
        if not self.results:
            return "configuring"
        if not self.results.score:
            return "configuring"
        if not self.results.score.faction1 or not self.results.score.faction2:
            return "no results"
        return f"{self.results.score.faction1} - {self.results.score.faction2}"
