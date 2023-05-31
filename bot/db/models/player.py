from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.models.base import Base

if TYPE_CHECKING:
    from bot.db.models import Elo, Match


class Player(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(String(length=255), primary_key=True)

    elos: Mapped[list["Elo"]] = relationship("Elo", back_populates="player")
    matches: Mapped[list["Match"]] = relationship("Match", secondary="elos", back_populates="players", viewonly=True)

    def __str__(self) -> str:
        return f"<Player {str(self.id)}>"
