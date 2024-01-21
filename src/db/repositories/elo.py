from sqlalchemy.ext.asyncio import AsyncSession

from src.db import Elo, Match, Player


class EloRepository:
    async def create(self, session: AsyncSession, player: Player, match: Match, elo: int) -> Elo:
        elo_obj: Elo = Elo(match=match, player=player, elo=elo)
        session.add(elo_obj)
        return elo_obj


elo_repo = EloRepository()
