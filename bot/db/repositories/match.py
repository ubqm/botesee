from datetime import datetime
from uuid import UUID

from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import Match


class MatchRepository:
    async def get_or_create(
        self,
        session: AsyncSession,
        match_uuid: str | UUID,
        date: datetime | None = None,
        game: str = "cs2",
    ) -> Match:
        stmt = select(Match).where(Match.id == str(match_uuid))

        result: Result = await session.execute(stmt)
        match: Match | None = result.scalar_one_or_none()
        if not match:
            match = Match(id=str(match_uuid), date=date, game=game)
            session.add(match)
        return match


match_repo = MatchRepository()
