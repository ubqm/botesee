from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.models.base import Base

if TYPE_CHECKING:
    from bot.db.models import Elo, Player


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(String(length=255), primary_key=True)
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(tz=UTC), server_default=func.now()
    )

    elos: Mapped[list["Elo"]] = relationship("Elo", back_populates="match")
    players: Mapped[list["Player"]] = relationship("Player", secondary="elos", back_populates="matches", viewonly=True)

    def __str__(self) -> str:
        return f"<Match {str(self.id)}>"
