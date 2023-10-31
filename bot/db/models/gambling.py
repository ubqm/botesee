from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text
from sqlalchemy.dialects.postgresql import ENUM as DB_ENUM
from sqlalchemy.dialects.postgresql import UUID as DB_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DECIMAL

from bot.db.models.base import Base


class TransactionEvent(StrEnum):
    DIRECT: str = "direct"
    PAYOUT: str = "payout"
    CANCEL: str = "cancel"


class BetType(StrEnum):
    T1_WIN: str = "t1_win"
    T2_WIN: str = "t2_win"


class BetState(StrEnum):
    OPEN: str = "open"
    CLOSED: str = "closed"


class BetMatch(Base):
    __tablename__ = "bet_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[str] = mapped_column(String(length=128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now, server_default=func.now()
    )

    coefficients: Mapped[list["BetCoefficient"]] = relationship("BetCoefficient", back_populates="bet_match")
    # match: Mapped["Match"] = relationship("Match", back_populates="bet_match")
    events: Mapped[list["BetEvent"]] = relationship("BetEvent", back_populates="bet_match")

    def __repr__(self) -> str:
        return f"<BetMatch id={self.id}, faceit_match={self.match_id}>"


class BetEvent(Base):
    __tablename__ = "bet_events"

    id: Mapped[UUID] = mapped_column(
        DB_UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=text("gen_random_uuid()")
    )
    state: Mapped[BetState] = mapped_column(DB_ENUM(BetState), default=BetState.OPEN)
    reason: Mapped[str] = mapped_column(String(length=128), nullable=True)
    bet_type: Mapped[BetType] = mapped_column(DB_ENUM(BetType))
    bet_match_id: Mapped[str] = mapped_column(ForeignKey("bet_matches.id"))
    member_id: Mapped[str] = mapped_column(String(64))
    amount: Mapped[int] = mapped_column(Integer)
    bet_coef_id: Mapped[UUID] = mapped_column(ForeignKey("bet_coefficients.id"))

    bet_match: Mapped["BetMatch"] = relationship("BetMatch", back_populates="events")
    coefficient: Mapped["BetCoefficient"] = relationship("BetCoefficient", back_populates="bet_event")

    def __repr__(self) -> str:
        return f"<BetEvent state={self.state}, bet_type={self.bet_type}, member={self.member_id}>"


class BetTransactions(Base):
    __tablename__ = "bet_transactions"

    id: Mapped[UUID] = mapped_column(
        DB_UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=text("gen_random_uuid()")
    )
    event: Mapped[TransactionEvent] = mapped_column(DB_ENUM(TransactionEvent), nullable=False)
    member_id: Mapped[str] = mapped_column(String(64), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    bet_event_id: Mapped[UUID] = mapped_column(ForeignKey("bet_events.id"), nullable=True)

    def __repr__(self) -> str:
        return f"<BetTransaction id={self.id}, event={self.event}, member={self.member_id}, amount={self.amount}>"


class BetCoefficient(Base):
    __tablename__ = "bet_coefficients"

    id: Mapped[UUID] = mapped_column(
        DB_UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=text("gen_random_uuid()")
    )
    bet_match_id: Mapped[str] = mapped_column(ForeignKey("bet_matches.id"))
    bet_type: Mapped[BetType] = mapped_column(DB_ENUM(BetType), nullable=False)
    coefficient: Mapped[Decimal] = mapped_column(DECIMAL(5, 2, asdecimal=True))

    bet_match: Mapped["BetMatch"] = relationship("BetMatch", back_populates="coefficients")
    bet_event: Mapped["BetEvent"] = relationship("BetEvent", back_populates="coefficient")

    def __repr__(self) -> str:
        return f"<BetCoef match={self.bet_match_id}, type={self.bet_type}, ratio={self.coefficient}>"
