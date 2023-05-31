from sqlalchemy.orm import SessionTransaction

from bot.db import Elo, Match, Player


class EloRepository:
    def create(self, session: SessionTransaction, player: Player, match: Match, elo: int) -> Elo:
        elo = Elo(match=match, player=player, elo=elo)
        session.session.add(elo)
        return elo
