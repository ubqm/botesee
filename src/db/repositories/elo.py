from uuid import UUID

from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import Elo, Match, Player, session_maker


class EloRepository:
    async def get_or_create(
        self, session: AsyncSession, player: Player, match: Match, elo: int
    ) -> Elo:
        stmt = (
            select(Elo)
            .where(Elo.match_id == match.id)
            .where(Elo.player_id == player.id)
        )
        if db_elo := await session.scalar(stmt):
            return db_elo

        elo_obj: Elo = Elo(match=match, player=player, elo=elo)
        session.add(elo_obj)
        return elo_obj

    async def get_avg_elo(self, match_id: str, players: list[str] | None = None) -> int:
        async with session_maker() as session:
            stmt = select(
                func.cast(func.coalesce(func.avg(Elo.elo), 0), Integer)
            ).where(Elo.match_id == match_id)

            if players:
                stmt.where(Elo.player_id.in_(players))

            res = (await session.execute(stmt)).scalar_one()

        return res

    async def get_player_elo_for_match(
        self, player_id: UUID, match_id: str
    ) -> int | None:
        stmt = (
            select(Elo.elo)
            .where(Elo.player_id == player_id)
            .where(Elo.match_id == match_id)
        )
        async with session_maker() as session:
            return (await session.execute(stmt)).scalar_one()


elo_repo = EloRepository()
