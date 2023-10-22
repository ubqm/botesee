from decimal import Decimal
from math import ceil
from typing import Sequence

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from bot import conf
from bot.clients.models.faceit.match_stats import MatchStatistics
from bot.db.models.gambling import (
    BetCoefficient,
    BetEvent,
    BetMatch,
    BetState,
    BetTransactions,
    BetType,
    TransactionEvent,
)
from bot.web.models.events import MatchAborted, MatchFinished


class GamblingRepository:
    async def new_match(
        self,
        session: AsyncSession,
        match_id: str,
    ) -> BetMatch:
        bet_match = BetMatch(
            match_id=match_id,
        )
        bet_coef_t1 = BetCoefficient(
            bet_match=bet_match,
            bet_type=BetType.T1_WIN,
            coefficient=Decimal(2.0),
        )
        bet_coef_t2 = BetCoefficient(
            bet_match=bet_match,
            bet_type=BetType.T2_WIN,
            coefficient=Decimal(2.0),
        )
        session.add_all((bet_match, bet_coef_t1, bet_coef_t2))
        await session.commit()
        logger.info(f"BEFORE select {bet_match = }")
        bet_match = await self.get_bet_match(session, match_id)
        return bet_match

    async def get_bet_match(self, session: AsyncSession, match_id: str) -> BetMatch:
        stmt = select(BetMatch).where(BetMatch.match_id == match_id)
        return await session.scalar(stmt)

    async def get_match_coefficients(self, session: AsyncSession, match_id: str) -> Sequence[BetCoefficient]:
        stmt = select(BetCoefficient).join(BetCoefficient.bet_match).where(BetMatch.match_id == match_id)
        coefs: Sequence[BetCoefficient] = (await session.scalars(stmt)).all()
        return coefs

    async def get_coefficients_by_type(self, session: AsyncSession, bet_match_id: str, bet_type: BetType):
        stmt = select(BetCoefficient).where(
            (BetCoefficient.bet_match_id == bet_match_id) & (BetCoefficient.bet_type == bet_type)
        )
        bet_coef: BetCoefficient = await session.scalar(stmt)
        return bet_coef

    async def create_event(
        self,
        session: AsyncSession,
        match_id: str,
        member_id: int,
        bet_type: BetType,
        amount: int,
    ) -> None:
        bet_match: BetMatch = await session.scalar(select(BetMatch).where(BetMatch.match_id == match_id))
        bet_coef = await self.get_coefficients_by_type(session=session, bet_match_id=bet_match.id, bet_type=bet_type)
        bet_event = BetEvent(
            bet_type=bet_type, bet_match_id=bet_match.id, member_id=member_id, amount=amount, bet_coef_id=bet_coef.id
        )
        session.add(bet_event)
        await session.commit()

    async def get_balance(self, session: AsyncSession, member_id: int) -> int:
        stmt = select(func.sum(BetTransactions.amount.label("balance_change"))).where(
            BetTransactions.member_id == member_id
        )
        balance_tr = await session.scalar(stmt) or 0

        stmt = select(func.sum(BetEvent.amount.label("balance_on_hold"))).where(
            (BetEvent.member_id == member_id) & (BetEvent.state == BetState.OPEN)
        )
        balance_on_hold = await session.scalar(stmt) or 0
        live_balance = conf.START_BALANCE + balance_tr - balance_on_hold

        return live_balance

    async def make_payout(self, session: AsyncSession, match: MatchFinished, statistics: MatchStatistics) -> None:
        bet_match = await self.get_bet_match(session=session, match_id=match.payload.id)
        stmt = (
            select(BetEvent)
            .where((BetEvent.state == BetState.OPEN) & (BetEvent.bet_match == bet_match))
            .options(joinedload(BetEvent.coefficient))
        )
        events: Sequence[BetEvent] = (await session.scalars(stmt)).all()
        for event in events:
            if (statistics.rounds[0].teams[0].team_stats.team_win and event.bet_type == BetType.T1_WIN) or (
                statistics.rounds[0].teams[1].team_stats.team_win and event.bet_type == BetType.T2_WIN
            ):
                amount = ceil(event.amount * event.coefficient.coefficient)
            else:
                amount = -event.amount

            transaction = BetTransactions(
                event=TransactionEvent.PAYOUT,
                member_id=event.member_id,
                amount=amount,
                bet_event_id=event.id,
            )
            event.state = BetState.CLOSED
            event.reason = "Event Finished"
            session.add(event)
            session.add(transaction)

    async def cancel_bets(self, session: AsyncSession, match: MatchAborted) -> None:
        bet_match = await self.get_bet_match(session=session, match_id=match.payload.id)
        stmt = select(BetEvent).where((BetEvent.state == BetState.OPEN) & (BetEvent.bet_match == bet_match))
        events: Sequence[BetEvent] = (await session.scalars(stmt)).all()
        for event in events:
            transaction = BetTransactions(
                event=TransactionEvent.CANCEL,
                member_id=event.member_id,
                amount=event.amount,
                bet_event_id=event.id,
            )
            event.state = BetState.CLOSED
            event.reason = "Event Canceled"
            session.add(event)
            session.add(transaction)
        await session.commit()


gambling_repo = GamblingRepository()
