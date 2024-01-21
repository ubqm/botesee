from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import UUID as UUID_SA
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base

if TYPE_CHECKING:
    from src.db.models.elo import Elo
    from src.db.models.match import Match


class Player(Base):
    __tablename__ = "players"

    id: Mapped[UUID] = mapped_column(UUID_SA(as_uuid=True), primary_key=True)

    elos: Mapped[list["Elo"]] = relationship("Elo", back_populates="player")
    matches: Mapped[list["Match"]] = relationship("Match", secondary="elos", back_populates="players", viewonly=True)

    def __str__(self) -> str:
        return f"<Player {str(self.id)}>"

    def __repr__(self) -> str:
        return f"<Player {str(self.id)}>"
