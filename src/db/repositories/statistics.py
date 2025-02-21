from datetime import UTC, datetime, timedelta
from typing import Iterable
from uuid import UUID

from pydantic import BaseModel

from src.clients.models.faceit.match_stats import (
    MatchStatistics,
    Player,
    PlayerStats,
    Round,
)
from src.db import Match
from src.db.repositories.elo import elo_repo
from src.db.repositories.match import match_repo
from src.utils.enums import subscribers


class AvgPeriodStat(BaseModel):
    adr: float
    kills: float
    deaths: float
    mvps: float
    headshots_p: float
    clutches_p: float
    enemy_elo: float
    matches_played: int


class WeeklyStats(BaseModel):
    latest_period_avg_stats: AvgPeriodStat
    prev_period_avg_stats: AvgPeriodStat
    elo_prev: float
    elo_current: float
    nickname: str


class WeeklyStatistics:
    async def get_weekly_stats(self) -> list[WeeklyStats]:
        weekly_stats_list: list[WeeklyStats] = []
        all_latest_week_matches = await self.get_matches(
            [uuid for name, uuid in subscribers],
            datetime.now(tz=UTC) - timedelta(days=7),
            datetime.now(tz=UTC),
        )
        all_prev_period_week_matches = await self.get_matches(
            [uuid for name, uuid in subscribers],
            datetime.now(tz=UTC) - timedelta(days=14),
            datetime.now(tz=UTC) - timedelta(days=7),
        )

        for player, matches in all_latest_week_matches.items():
            prev_period_last_match = (
                all_prev_period_week_matches[player][-1]
                if all_prev_period_week_matches.get(player)
                else all_latest_week_matches[player][0]
            )

            latest_period_stat = await match_repo.get_stats(
                [match.id for match in matches]
            )
            prev_period_stat = await match_repo.get_stats(
                [match.id for match in matches]
            )

            latest_elo = await elo_repo.get_player_elo_for_match(player, matches[0].id)
            prev_period_elo = await elo_repo.get_player_elo_for_match(
                player, prev_period_last_match.id
            )

            avg_stats_latest_period = self.get_avg_stats_for_period(
                player, latest_period_stat
            )
            avg_stats_prev_period = self.get_avg_stats_for_period(
                player, prev_period_stat
            )

            nickname = latest_period_stat[-1].rounds[0].get_nickname(player)
            weekly_stats_list.append(
                WeeklyStats(
                    latest_period_avg_stats=avg_stats_latest_period,
                    prev_period_avg_stats=avg_stats_prev_period,
                    elo_current=latest_elo,
                    elo_prev=prev_period_elo,
                    nickname=nickname,
                )
            )
        return weekly_stats_list

    async def get_matches(
        self,
        player_ids: Iterable[UUID],
        from_dt: datetime,
        to_dt: datetime,
    ) -> dict[UUID, list[Match]]:
        all_players_matches: dict[UUID, list[Match]] = {}
        for player_uuid in player_ids:
            matches = await match_repo.get_player_matches(
                player_id=player_uuid,
                from_dt=from_dt,
                to_dt=to_dt,
            )
            if len(matches) >= 5:  # min matches required for weekly stats
                all_players_matches[player_uuid] = matches

        return dict(
            sorted(
                all_players_matches.items(), key=lambda item: len(item[1]), reverse=True
            )
        )

    def get_avg_stats_for_period(
        self, player_id: UUID, period_stat: list[MatchStatistics]
    ) -> AvgPeriodStat:
        match_rounds: list[Round] = [
            match_round for match in period_stat for match_round in match.rounds
        ]
        stats_collection: list[PlayerStats] = [
            match.get_player_stats(player_id) for match in match_rounds
        ]
        match_amount = len(stats_collection)

        enemy_players_collection: list[list[Player]] = [
            match.get_enemy_players(player_id) for match in match_rounds
        ]
        avg_enemy_elo = (
            sum(
                [
                    elo_repo.get_avg_elo(match.match_id, enemy_players)
                    for match, enemy_players in zip(
                        match_rounds, enemy_players_collection
                    )
                ]
            )
            / match_amount
        )

        return AvgPeriodStat(
            adr=sum(stat.adr for stat in stats_collection) / match_amount,
            kills=sum(stat.kills for stat in stats_collection) / match_amount,
            deaths=sum(stat.deaths for stat in stats_collection) / match_amount,
            mvps=sum(stat.mvps for stat in stats_collection) / match_amount,
            headshots_p=sum(stat.headshots_p for stat in stats_collection)
            / match_amount,
            clutches_p=sum(stat.match_1v1_winrate for stat in stats_collection)
            / match_amount,
            enemy_elo=avg_enemy_elo,
            matches_played=match_amount,
        )
