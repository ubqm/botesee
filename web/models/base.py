from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from models.entities import Team


class EventEnum(str, Enum):
    ABORTED = "match_status_aborted"
    CANCELLED = "match_status_cancelled"
    FINISHED = "match_status_finished"
    READY = "match_status_configuring"


class Entity(BaseModel):
    id: UUID
    name: str
    type: str


class BasePayload(BaseModel):
    id: str
    organizer_id: str
    region: str
    game: str
    version: int
    entity: Entity
    teams: list[Team, Team]


class BaseMatch(BaseModel):
    transaction_id: UUID
    event: EventEnum
    event_id: UUID
    third_party_id: UUID
    app_id: UUID
    timestamp: datetime
    retry_count: int
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        use_enum_values = True
