from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Iterable, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from src.clients.faceit import faceit_client
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
    adr: Decimal = Field(decimal_places=1)
    kills: Decimal = Field(decimal_places=1)
    deaths: Decimal = Field(decimal_places=1)
    mvps: Decimal = Field(decimal_places=1)
    headshots_p: Decimal = Field(decimal_places=1)
    clutches_p: Decimal = Field(decimal_places=1)
    enemy_elo: Decimal = Field(decimal_places=1)
    kd_ratio: Decimal = Field(decimal_places=2)
    entry_success_rate: Decimal = Field(decimal_places=1)
    matches_played: int


class WeeklyStats(BaseModel):
    latest_period_avg_stats: AvgPeriodStat
    prev_period_avg_stats: AvgPeriodStat | None
    elo_prev: int
    elo_current: int
    nickname: str
    avatar: str
    cover_image: str

    def get_kd_ratio(self, mode: Literal["latest", "prev"]) -> Decimal | None:
        if mode == "latest":
            return self.latest_period_avg_stats.kd_ratio

        if self.prev_period_avg_stats:
            return self.prev_period_avg_stats.kd_ratio

        return None

    def get_amount_matches(self, mode: Literal["latest", "prev"]) -> int | None:
        if mode == "latest":
            return self.latest_period_avg_stats.matches_played

        if self.prev_period_avg_stats:
            return self.prev_period_avg_stats.matches_played

        return None

    def get_adr(self, mode: Literal["latest", "prev"]) -> Decimal | None:
        if mode == "latest":
            return self.latest_period_avg_stats.adr

        if self.prev_period_avg_stats:
            return self.prev_period_avg_stats.adr

        return None

    def get_headshots_p(self, mode: Literal["latest", "prev"]) -> Decimal | None:
        if mode == "latest":
            return self.latest_period_avg_stats.headshots_p

        if self.prev_period_avg_stats:
            return self.prev_period_avg_stats.headshots_p

        return None

    def get_entry_p(self, mode: Literal["latest", "prev"]) -> Decimal | None:
        if mode == "latest":
            return self.latest_period_avg_stats.entry_success_rate

        if self.prev_period_avg_stats:
            return self.prev_period_avg_stats.entry_success_rate

        return None

    def get_clutches_p(self, mode: Literal["latest", "prev"]) -> Decimal | None:
        if mode == "latest":
            return self.latest_period_avg_stats.clutches_p

        if self.prev_period_avg_stats:
            return self.prev_period_avg_stats.clutches_p

        return None


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
            # Stats for both periods
            avg_stats_latest_period = await self._get_latest_period_avg_stats(
                player, matches
            )
            avg_stats_prev_period = await self._get_prev_period_avg_stats(
                player, all_prev_period_week_matches.get(player, [])
            )

            # Calculate elo change
            prev_period_last_match = (
                all_prev_period_week_matches[player][-1]
                if all_prev_period_week_matches.get(player)
                else all_latest_week_matches[player][0]
            )
            latest_elo = await elo_repo.get_player_elo_for_match(player, matches[0].id)
            prev_period_elo = await elo_repo.get_player_elo_for_match(
                player, prev_period_last_match.id
            )

            # player info for nickname, avatar and cover_image
            player_info = await faceit_client.player_details_by_id(player)
            weekly_stats_list.append(
                WeeklyStats(
                    latest_period_avg_stats=avg_stats_latest_period,
                    prev_period_avg_stats=avg_stats_prev_period,
                    elo_current=latest_elo,
                    elo_prev=prev_period_elo,
                    nickname=player_info.nickname,
                    avatar=player_info.avatar,
                    cover_image=player_info.cover_image,
                )
            )
        return weekly_stats_list

    async def _get_latest_period_avg_stats(
        self, player: UUID, matches: list[Match]
    ) -> AvgPeriodStat:
        latest_period_stat = await match_repo.get_stats([match.id for match in matches])
        avg_stats_latest_period = await self.get_avg_stats_for_period(
            player, latest_period_stat
        )
        return avg_stats_latest_period

    async def _get_prev_period_avg_stats(
        self, player: UUID, matches: list[Match]
    ) -> AvgPeriodStat | None:
        if not matches:
            return None

        prev_period_stat = await match_repo.get_stats([match.id for match in matches])
        avg_stats_prev_period = await self.get_avg_stats_for_period(
            player, prev_period_stat
        )
        return avg_stats_prev_period

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

    async def get_avg_stats_for_period(
        self, player_id: UUID, period_stat: list[MatchStatistics]
    ) -> AvgPeriodStat | None:
        match_rounds: list[Round] = [
            match_round for match in period_stat for match_round in match.rounds
        ]
        if not match_rounds:
            return None

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
                    await elo_repo.get_avg_elo(match.match_id, enemy_players)
                    for match, enemy_players in zip(
                        match_rounds, enemy_players_collection
                    )
                ]
            )
            / match_amount
        )

        return AvgPeriodStat(
            adr=Decimal(
                f"{sum(stat.adr for stat in stats_collection) / match_amount:.1f}"
            ),
            kills=Decimal(
                f"{sum(stat.kills for stat in stats_collection) / match_amount:.1f}"
            ),
            deaths=Decimal(
                f"{sum(stat.deaths for stat in stats_collection) / match_amount:.1f}"
            ),
            mvps=Decimal(
                f"{sum(stat.mvps for stat in stats_collection) / match_amount:.1f}"
            ),
            headshots_p=Decimal(
                f"{sum(stat.headshots_p for stat in stats_collection) * 100
            / match_amount:.1f}"
            ),
            clutches_p=Decimal(
                f"{sum(stat.match_1v1_winrate for stat in stats_collection) * 100
            / match_amount:.1f}"
            ),
            enemy_elo=Decimal(f"{avg_enemy_elo:.1f}"),
            matches_played=match_amount,
            kd_ratio=Decimal(
                f"{sum(stat.kd_ratio for stat in stats_collection) / match_amount:.2f}"
            ),
            entry_success_rate=Decimal(
                f"{sum(stat.match_entry_success_rate for stat in stats_collection) * 100
            / match_amount:.1f}"
            ),
        )
