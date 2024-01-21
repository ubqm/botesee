from datetime import datetime
from typing import Annotated, Literal, Union

from pydantic import Field

from src.web.models.base import BaseMatch, BasePayload, EventEnum


class PayloadCancelled(BasePayload):
    reason: str


class PayloadFinished(BasePayload):
    started_at: datetime
    finished_at: datetime


class MatchAborted(BaseMatch):
    payload: PayloadCancelled
    event: Literal[EventEnum.ABORTED]


class MatchCancelled(BaseMatch):
    event: Literal[EventEnum.CANCELLED]
    payload: PayloadCancelled


class MatchFinished(BaseMatch):
    event: Literal[EventEnum.FINISHED]
    payload: PayloadFinished


class MatchReady(BaseMatch):
    event: Literal[EventEnum.READY, EventEnum.CONFIGURING]
    payload: BasePayload


WebhookMatch = Annotated[
    Union[MatchAborted, MatchCancelled, MatchFinished, MatchReady],
    Field(discriminator="event"),
]
