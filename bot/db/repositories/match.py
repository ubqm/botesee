from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import SessionTransaction

from bot.db import Match


class MatchRepository:
    def get_or_create(
        self, session: SessionTransaction, match_uuid: str | UUID, date: datetime | None = None
    ) -> Match:
        stmt = select(Match).where(Match.id == str(match_uuid))

        match: Match = session.session.scalars(stmt).one_or_none()
        if not match:
            match = Match(id=str(match_uuid), date=date)
            session.session.add(match)
        return match
