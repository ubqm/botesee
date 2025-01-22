from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import Elo, Match, Player, session_maker


class EloRepository:
    async def create(
        self, session: AsyncSession, player: Player, match: Match, elo: int
    ) -> Elo:
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


elo_repo = EloRepository()
