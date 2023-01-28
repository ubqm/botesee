from typing import Optional
from uuid import UUID

from pydantic import AnyUrl, BaseModel


class Player(BaseModel):
    id: UUID
    nickname: str
    avatar: Optional[AnyUrl]
    game_id: str
    game_name: Optional[str]
    game_skill_level: int
    membership: Optional[str]
    anticheat_required: bool


class Team(BaseModel):
    id: UUID
    name: str
    type: Optional[UUID]
    avatar: Optional[AnyUrl]
    leader_id: UUID
    co_leader_id: Optional[UUID]
    roster: list[Player]
    substitutions: int
    substitutes: Optional[list[Player]]
