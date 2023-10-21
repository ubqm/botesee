from decimal import Decimal
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models.gambling import BetCoefficient, BetEvent, BetMatch, BetType


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
            bet_match_id=bet_match.id,
            bet_type=BetType.T1_WIN,
            coefficient=Decimal(2.0),
        )
        bet_coef_t2 = BetCoefficient(
            bet_match_id=bet_match.id,
            bet_type=BetType.T2_WIN,
            coefficient=Decimal(2.0),
        )
        session.add_all((bet_match, bet_coef_t1, bet_coef_t2))
        await session.commit()
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

    async def create_event(self, session: AsyncSession, member_id: int, amount: int, bet_type: BetType, match_id: str):
        bet_match: BetMatch = await session.scalar(select(BetMatch).where(BetMatch.match_id == match_id))
        bet_coef = await self.get_coefficients_by_type(session=session, bet_match_id=bet_match.id, bet_type=bet_type)
        bet_event = BetEvent(
            bet_type=bet_type, bet_match_id=bet_match.id, member_id=member_id, amount=amount, bet_coef_id=bet_coef.id
        )
        session.add(bet_event)
        await session.commit()


gambling_repo = GamblingRepository()
