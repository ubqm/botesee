from enum import StrEnum
from typing import Literal


class QueueName(StrEnum):
    MATCHES: Literal["matches"] = "matches"
    UPDATE_SCORE: Literal["update_score"] = "update_score"
    WEEKLY_STATS: Literal["weekly_stats"] = "weekly_stats"
