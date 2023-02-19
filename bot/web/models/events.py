from datetime import datetime
from typing import Annotated, Union, Literal

from pydantic import Field

from bot.web.models.base import BasePayload, BaseMatch


class PayloadCancelled(BasePayload):
    reason: str


class PayloadFinished(BasePayload):
    started_at: datetime
    finished_at: datetime


class MatchAborted(BaseMatch):
    payload: PayloadCancelled
    event: Literal["match_status_aborted"]


class MatchCancelled(BaseMatch):
    event: Literal["match_status_cancelled"]
    payload: PayloadCancelled


class MatchFinished(BaseMatch):
    event: Literal["match_status_finished"]
    payload: PayloadFinished


class MatchReady(BaseMatch):
    event: Literal["match_status_ready", "match_status_configuring"]
    payload: BasePayload


WebhookMatch = Annotated[Union[MatchAborted, MatchCancelled, MatchFinished, MatchReady],
                         Field(discriminator="event")]
