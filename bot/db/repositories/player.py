from uuid import UUID

from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import Player


class PlayerRepository:
    async def get_or_create(self, session: AsyncSession, player_uuid: str | UUID) -> Player:
        stmt = select(Player).where(Player.id == str(player_uuid))

        result: Result = await session.execute(stmt)
        player: Player | None = result.scalar_one_or_none()
        if not player:
            player = Player(id=str(player_uuid))
            session.add(player)
        return player
