from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM as DB_ENUM
from sqlalchemy.dialects.postgresql import UUID as DB_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DECIMAL

from bot.db.models.base import Base

if TYPE_CHECKING:
    from bot.db.models.match import Match


class TransactionEvent(StrEnum):
    DIRECT: str = "direct"
    PAYOUT: str = "payout"


class BetType(StrEnum):
    T1_WIN: str = "t1_win"
    T2_WIN: str = "t2_win"


class BetState(StrEnum):
    OPEN: str = "open"
    CLOSED: str = "closed"


class BetMatch(Base):
    __tablename__ = "bet_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.id"))

    coefficients: Mapped[list["BetCoefficient"]] = relationship("BetCoefficient", back_populates="bet_match")
    match: Mapped["Match"] = relationship("Match", back_populates="bet_match")
    events: Mapped[list["BetEvent"]] = relationship("BetEvent", back_populates="bet_match")


class BetEvent(Base):
    __tablename__ = "bet_events"

    id: Mapped[UUID] = mapped_column(DB_UUID(as_uuid=True), primary_key=True)
    state: Mapped[BetState] = mapped_column(DB_ENUM(BetState), default=BetState.OPEN)
    reason: Mapped[str] = mapped_column(String(length=128), nullable=True)
    bet_type: Mapped[BetType] = mapped_column(DB_ENUM(BetType))
    bet_match_id: Mapped[str] = mapped_column(ForeignKey("bet_matches.id"))
    member_id: Mapped[int] = mapped_column(Integer)
    amount: Mapped[int] = mapped_column(Integer)
    bet_coef_id: Mapped[UUID] = mapped_column(ForeignKey("bet_coefficients.id"))

    bet_match: Mapped["BetMatch"] = relationship("BetMatch", back_populates="events")
    coefficient: Mapped["BetCoefficient"] = relationship("BetCoefficient", back_populates="bet_event")


class BetTransactions(Base):
    __tablename__ = "bet_transactions"

    id: Mapped[UUID] = mapped_column(DB_UUID(as_uuid=True), primary_key=True)
    event: Mapped[TransactionEvent] = mapped_column(DB_ENUM(TransactionEvent), nullable=False)
    member_id: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    bet_event_id: Mapped[UUID] = mapped_column(ForeignKey("bet_events.id"), nullable=True)


class BetCoefficient(Base):
    __tablename__ = "bet_coefficients"

    id: Mapped[UUID] = mapped_column(DB_UUID(as_uuid=True), primary_key=True)
    bet_match_id: Mapped[str] = mapped_column(ForeignKey("bet_matches.id"))
    bet_type: Mapped[BetType] = mapped_column(DB_ENUM(BetType), nullable=False)
    coefficient: Mapped[Decimal] = mapped_column(DECIMAL(5, 2, asdecimal=True))

    bet_match: Mapped["BetMatch"] = relationship("BetMatch", back_populates="coefficients")
    bet_event: Mapped["BetEvent"] = relationship("BetEvent", back_populates="coefficient")
