import logging
from datetime import datetime, timedelta

import discord
from discord import ButtonStyle, Interaction, Button, SelectOption
from discord.ui import View, Select

from src.db import session_maker
from src.db.models.gambling import BetType
from src.db.repositories.gambling import gambling_repo


logger = logging.getLogger(__name__)


MINUTES_TILL_EXPIRE = 4


class PreBetView(View):
    def __init__(self, bet_match_id: int, live_until: datetime):
        self._bet_match_id = bet_match_id
        self._live_until = live_until
        super().__init__()

    @discord.ui.button(label="Balance", style=ButtonStyle.blurple, emoji="💸", row=0)
    async def get_current_balance(self, ctx: Interaction, button: Button):
        async with session_maker() as session:
            current_balance = await gambling_repo.get_balance(
                session=session, member_id=str(ctx.user.id)
            )
            await ctx.response.send_message(
                f"Your current balance is {current_balance}",
                ephemeral=True,
            )

    @discord.ui.button(label="Bet Menu", style=ButtonStyle.gray, emoji="🗒️", row=0)
    async def bet_menu(self, ctx: Interaction, button: Button):
        await ctx.response.send_message(
            "Bet Menu",
            ephemeral=True,
            view=MatchBetView(bet_match_id=self._bet_match_id),
            delete_after=(self._live_until - datetime.now()).seconds,
        )


class MatchBetView(View):
    def __init__(self, bet_match_id: int):
        self._bet_type: BetType | None = None
        self._amount: int | None = None
        self.bet_match_id: int = bet_match_id
        super().__init__()

    @discord.ui.select(
        options=[
            SelectOption(label="Team 1 win", value=BetType.T1_WIN),
            SelectOption(label="Team 2 win", value=BetType.T2_WIN),
        ],
        placeholder="Please choose bet type",
        row=1,
    )
    async def select_bet_type(self, ctx: Interaction, selected: Select):
        self._bet_type = selected.values[0]
        await ctx.response.defer()

    @discord.ui.select(
        options=[
            SelectOption(label="1"),
            SelectOption(label="5"),
            SelectOption(label="10"),
            SelectOption(label="20"),
            SelectOption(label="30"),
            SelectOption(label="40"),
            SelectOption(label="50"),
            SelectOption(label="75"),
            SelectOption(label="100"),
            SelectOption(label="150"),
            SelectOption(label="200"),
            SelectOption(label="500"),
        ],
        placeholder="Please choose amount",
        max_values=12,
        row=2,
    )
    async def select_amount(self, ctx: Interaction, selected: Select):
        self._amount = sum([int(v) for v in selected.values])
        await ctx.response.defer()

    @discord.ui.button(label="Confirm", style=ButtonStyle.green, emoji="😎", row=3)
    async def confirm_bet(self, ctx: Interaction, button: Button):
        async with session_maker() as session:
            bet_match = await gambling_repo.get_bet_match_by_id(
                session=session, bet_match_id=self.bet_match_id
            )
            logger.info(f"time_between = {ctx.created_at - bet_match.created_at}")
            if ctx.created_at - bet_match.created_at > timedelta(
                minutes=MINUTES_TILL_EXPIRE
            ):
                await ctx.response.send_message(
                    f"Bets are closed: {MINUTES_TILL_EXPIRE} minutes expired",
                    ephemeral=True,
                    delete_after=5.0,
                )
                return None

            current_balance = await gambling_repo.get_balance(
                session=session, member_id=str(ctx.user.id)
            )
            if current_balance - self._amount < 0:
                await ctx.response.send_message(
                    f"Not enough points. Current balance: {current_balance}",
                    ephemeral=True,
                    delete_after=5.0,
                )
                return None

            await gambling_repo.create_event(
                session=session,
                bet_match_id=bet_match.id,
                member_id=str(ctx.user.id),
                bet_type=self._bet_type,
                amount=self._amount,
            )
            await session.commit()

        await ctx.response.send_message(
            f"Your bet is accepted. {self._amount} points on {self._bet_type}. Match id [{self.bet_match_id}]",
            ephemeral=True,
        )
        button.disabled = True
        self.stop()
