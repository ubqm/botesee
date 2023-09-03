from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import SessionTransaction

from bot.db import Player


class PlayerRepository:
    def get_or_create(self, session: SessionTransaction, player_uuid: str | UUID) -> Player:
        stmt = select(Player).where(Player.id == str(player_uuid))

        player: Player | None = session.session.scalars(stmt).one_or_none()
        if not player:
            player = Player(id=str(player_uuid))
            session.session.add(player)
        return player
