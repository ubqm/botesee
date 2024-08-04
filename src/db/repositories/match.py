from datetime import datetime
from uuid import UUID

from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.models.faceit.match_stats import MatchStatistics
from src.db import Match, session_maker


class MatchRepository:
    async def get_or_create(
        self,
        session: AsyncSession,
        match_uuid: str | UUID,
        stats: MatchStatistics | None = None,
        date: datetime | None = None,
        game: str = "cs2",
    ) -> Match:
        stmt = select(Match).where(Match.id == str(match_uuid))

        result: Result = await session.execute(stmt)
        match: Match | None = result.scalar_one_or_none()

        stats_json = stats.model_dump(mode="json", by_alias=True) if stats else None
        if not match:
            match = Match(id=str(match_uuid), date=date, game=game, stats=stats_json)
            session.add(match)
        return match

    async def get_stats(self, match_ids: list[UUID]) -> list[MatchStatistics]:
        stmt = (
            select(Match.stats)
            .where(Match.id.in_(match_ids))
            .order_by(Match.date.desc())
        )
        async with session_maker() as session:
            match_stats = (await session.scalars(stmt)).all()
            return [MatchStatistics(**stat) for stat in match_stats]


match_repo = MatchRepository()
