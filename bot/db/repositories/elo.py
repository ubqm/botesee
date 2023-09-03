from sqlalchemy.orm import SessionTransaction

from bot.db import Elo, Match, Player


class EloRepository:
    def create(self, session: SessionTransaction, player: Player, match: Match, elo: int) -> Elo:
        elo_obj: Elo = Elo(match=match, player=player, elo=elo)
        session.session.add(elo)
        return elo_obj
