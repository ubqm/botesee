import random
import re
from datetime import timedelta
from io import BytesIO
from typing import Any, Sequence

import discord
from discord import (
    Color,
    Intents,
    Interaction,
    Member,
    RawReactionActionEvent,
    TextChannel,
    app_commands, SelectOption,
)
from loguru import logger

from src.clients.faceit import faceit_client
from src.clients.models.faceit.match_details import MatchDetails
from src.clients.models.faceit.match_stats import Round
from src.clients.redis_repo import redis_repo
from src.db import session_maker
from src.db.models.gambling import BetCoefficient, BetMatch, BetType
from src.db.repositories.gambling import gambling_repo
from src.db.repositories.match import match_repo
from src.discord_bot.models.embed import NickEloStorage, PlayerStorage
from src.image_collectors.compare_imcol import CompareImCol
from src.image_collectors.last_stat_imcol import LastStatsImCol
from src.image_collectors.match_finished import MatchFinishedImCol
from src.utils.enums import subscribers
from src.web.models.base import Player
from src.web.models.events import MatchAborted, MatchFinished, MatchReady

MINUTES_TILL_EXPIRE = 4


def get_match_finished_message_color(round: Round) -> int:
    black, green, red, gray = 1, 2067276, 10038562, 9936031
    teams_subscribers_found = [False, False]  # Team1 and Team2 boolean
    for idx_team, team in enumerate(round.teams):
        for player in team.players:
            if player.player_id in subscribers:
                teams_subscribers_found[idx_team] = True
    if all(teams_subscribers_found):
        return gray
    if not any(teams_subscribers_found):
        return black
    if (teams_subscribers_found[0] and round.teams[0].team_stats.team_win) or (
        teams_subscribers_found[1] and round.teams[1].team_stats.team_win
    ):
        return green
    return red


def get_description_for_match_finish(
    match_round: Round, coefs: Sequence[BetCoefficient]
) -> str:
    nicknames_1 = [
        f"[{player.nickname}](https://www.faceit.com/en/players/{player.nickname})"
        for player in match_round.teams[0].players
    ]
    nicknames_2 = [
        f"[{player.nickname}](https://www.faceit.com/en/players/{player.nickname})"
        for player in match_round.teams[1].players
    ]
    str_nick_1 = ", ".join(nicknames_1)
    str_nick_2 = ", ".join(nicknames_2)

    return f"[{str(coefs[0].coefficient)}] {str_nick_1}\n[{str(coefs[1].coefficient)}] {str_nick_2}"


async def get_nicks_and_elo(roster: list[Player], game: str = "cs2") -> NickEloStorage:
    players_storage: list[PlayerStorage] = []
    for player in roster:
        elo = await faceit_client.get_player_elo_by_player_id(player.id, game)
        players_storage.append(PlayerStorage(nickname=player.nickname, elo=elo))
    return NickEloStorage(players=players_storage)


def form_ready_embed_message(
    match: MatchReady,
    nick_elo_1: NickEloStorage,
    nick_elo_2: NickEloStorage,
    coefs: Sequence[BetCoefficient],
) -> discord.Embed:
    my_color = 9936031  # gray
    description = (
        f"[{match.payload.id}](https://www.faceit.com/en/cs2/room/{match.payload.id})"
    )
    embed_msg = discord.Embed(
        title=f"[{match.payload.game}] Ongoing Match",
        type="rich",
        description=description,
        color=my_color,
    )
    embed_msg.add_field(
        name=f"{match.payload.teams[0].name}[{str(coefs[0].coefficient)}]",
        value=nick_elo_1.get_discord_nicknames(),
        inline=True,
    )
    embed_msg.add_field(
        name=f"ELO[{nick_elo_1.get_avg_elo()}]",
        value=nick_elo_1.get_discord_elos(),
        inline=True,
    )
    embed_msg.add_field(name="\u200b", value="\u200b")
    embed_msg.add_field(
        name=f"{match.payload.teams[1].name}[{str(coefs[1].coefficient)}]",
        value=nick_elo_2.get_discord_nicknames(),
        inline=True,
    )
    embed_msg.add_field(
        name=f"ELO[{nick_elo_2.get_avg_elo()}]",
        value=nick_elo_2.get_discord_elos(),
        inline=True,
    )
    embed_msg.add_field(name="\u200b", value="\u200b")
    return embed_msg


class DiscordClient(discord.Client):
    def __init__(self, faceit_channel_id: int, intents: Intents, **options: Any):
        super().__init__(intents=intents, options=options)
        self.faceit_channel_id: int = faceit_channel_id
        self.faceit_channel: discord.TextChannel | None = None

    async def on_ready(self):
        await self.wait_until_ready()
        for guild in self.guilds:
            logger.info(f"Logged in as {self.user}, {guild.name=}, {guild.id=}")
        await tree.sync()
        logger.info("Commands synced")
        self.faceit_channel = self.get_channel(self.faceit_channel_id)

    @staticmethod
    def compile_binary_image(image):
        if image is not None:
            with BytesIO() as image_binary:
                image.save(image_binary, "PNG")
                image_binary.seek(0)
                binary_image = discord.File(fp=image_binary, filename="image.png")
                return binary_image

    @staticmethod
    def is_contains_media(message: discord.Message) -> bool:
        return any(
            (
                "http://" in message.content,
                message.attachments,
                "https://" in message.content,
                message.embeds,
            )
        )

    @staticmethod
    def is_stats_request(content: list) -> bool:
        return bool(re.search("^[.]stats?$", content[0]) and len(content) == 2)

    @staticmethod
    def is_compare_request(content: list) -> bool:
        return bool(re.search(r"^[.]compare$", content[0])) and (len(content) in (3, 5))

    async def on_message(self, message) -> None:
        if not self.faceit_channel:
            raise ConnectionError("Discord is not initialized yet")
        logger.info(f"New message from {message.author}: {message.content}")
        _content: list = message.content.split()
        if self.user and message.author.id != self.user.id:  # 825393722186924112
            if self.is_contains_media(message):
                await message.add_reaction("👍")
                await message.add_reaction("👎")

            if not _content:
                return

            elif bool(re.search(r"^[.]$", _content[0])):
                pass

    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        await self._handle_reaction_event(payload)

    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent) -> None:
        await self._handle_reaction_event(payload)

    async def _handle_reaction_event(self, payload: RawReactionActionEvent):
        upvotes = downvotes = 0
        if payload.emoji.name not in ("👍", "👎"):
            return

        channel = discord.Client.get_channel(self, payload.channel_id)
        if not channel:
            return

        if not isinstance(channel, TextChannel):
            return

        message = await channel.fetch_message(payload.message_id)
        for reaction in message.reactions:
            if reaction.emoji == "👍":
                upvotes = len(
                    [
                        user
                        async for user in reaction.users()
                        if isinstance(user, Member) and len(user.roles) > 1
                    ]
                )
            elif reaction.emoji == "👎":
                downvotes = len(
                    [
                        user
                        async for user in reaction.users()
                        if isinstance(user, Member) and len(user.roles) > 1
                    ]
                )

        logger.info(
            f"[{upvotes}/{downvotes}] {payload.emoji} {payload.event_type} by {payload.member} | "
            f"Message by {message.author}: {message.content}"
        )
        if upvotes < downvotes - 2:
            await message.delete()
            logger.info(
                f'Message "{message.content}" '
                f"deleted with {upvotes} Upvotes, "
                f"{downvotes} Downvotes\n"
            )

    async def post_faceit_message_ready(self, match: MatchReady) -> None:
        if not self.faceit_channel:
            raise ConnectionError("Discord is not initialized yet")
        nick_elo_1 = await get_nicks_and_elo(
            match.payload.teams[0].roster, game=match.payload.game
        )
        nick_elo_2 = await get_nicks_and_elo(
            match.payload.teams[1].roster, game=match.payload.game
        )
        nicks_elo_dict = nick_elo_1.get_dict() | nick_elo_2.get_dict()
        await redis_repo.save_match(match.payload.id, nicks_elo_dict)

        async with session_maker() as session:
            bet_match = await gambling_repo.new_match(
                session=session,
                match_id=match.payload.id,
                avg_elo_1=nick_elo_1.get_avg_elo(),
                avg_elo_2=nick_elo_2.get_avg_elo(),
            )
            coefs = await gambling_repo.get_match_coefficients(
                session=session, match_id=match.payload.id
            )

        embed_msg = form_ready_embed_message(match, nick_elo_1, nick_elo_2, coefs)
        await self.faceit_channel.send(embed=embed_msg)
        await self.gambling_message(match=match, bet_match=bet_match, coefs=coefs)

    async def gambling_message(
        self, match: MatchReady, bet_match: BetMatch, coefs: Sequence[BetCoefficient]
    ) -> None:
        description = (
            "To make a bet write command /bet. Choose a match and bet type with desired amount of points.\n"
            f"Example: /bet m{bet_match.id} {random.choice([BetType.T1_WIN.value, BetType.T2_WIN.value])} "
            f"{random.choice([10, 20, 30, 50])}\n"
            f"Bet is available for {MINUTES_TILL_EXPIRE} minutes.\n"
        )
        for coef in coefs:
            description += f"{coef.bet_type} - {coef.coefficient}\n"

        embed_msg = discord.Embed(
            title=f"Bets for match [m{bet_match.id}] {match.payload.id}",
            description=description,
            color=1752220,  # Aqua #1ABC9C
        )
        await self.faceit_channel.send(
            embed=embed_msg, delete_after=MINUTES_TILL_EXPIRE * 60
        )

    async def post_faceit_message_finished(self, match: MatchFinished) -> None:
        if not self.faceit_channel:
            raise ConnectionError("Discord is not initialized yet")

        statistics = (await match_repo.get_stats(match_ids=[match.payload.id]))[0]
        async with session_maker() as session:
            coefs = await gambling_repo.get_match_coefficients(
                session, match.payload.id
            )

        for match_round in statistics.rounds:
            str_nick = get_description_for_match_finish(match_round, coefs)
            my_color = get_match_finished_message_color(match_round)
            embed_msg = discord.Embed(
                description=str_nick,
                type="rich",
                title=f"{match_round.round_stats.map} [{match.payload.game}] - {match.payload.entity.name}",
                color=my_color,
                url=f"https://www.faceit.com/en/cs2/room/{match.payload.id}",
            )
            await self.delete_message_by_faceit_match_id(match.payload.id)
            redis_nick_elo = await redis_repo.get_match_elo(match.payload.id)
            nick_elo = (
                NickEloStorage(
                    players=[
                        PlayerStorage(nickname=nick, elo=elo)
                        for nick, elo in redis_nick_elo.items()
                    ]
                )
                if redis_nick_elo
                else None
            )

            img_collector = MatchFinishedImCol(match, match_round, nick_elo)
            image = await img_collector.collect_image()
            embed_msg.set_image(url="attachment://image.png")
            await self.faceit_channel.send(
                embed=embed_msg, file=self.compile_binary_image(image)
            )

    async def post_faceit_message_aborted(self, match: MatchAborted) -> None:
        async with session_maker() as session:
            await gambling_repo.cancel_bets(session=session, match=match)
        await self.delete_message_by_faceit_match_id(match.payload.id)

    async def delete_message_by_faceit_match_id(self, match_id: str) -> None:
        if not self.faceit_channel:
            raise ConnectionError("Discord is not initialized yet")

        async for message in self.faceit_channel.history(
            limit=40
        ):  # type: discord.Message
            if not message.embeds:
                continue

            if message_description := message.embeds[0].description:
                if match_id not in message_description:
                    continue
                if message.embeds[0].color == Color(1752220):
                    await message.delete()

            if not message.embeds or not message.embeds[0].fields:
                return None

            await message.delete()
        return None

    async def update_score_for_match(
        self, match_details: MatchDetails, match_ready: MatchReady
    ) -> None:
        if not self.faceit_channel:
            raise ConnectionError("Discord is not initialized yet")

        async for message in self.faceit_channel.history(limit=40):
            if not message.embeds:
                continue
            if match_details.match_id not in str(message.embeds[0].description):
                continue

            new_embed = message.embeds[0]
            new_embed.title = (
                f"[{match_details.game}] Ongoing Match [{match_details.current_score}]"
            )
            if match_details.voting:
                location = match_details.voting.location
                new_embed.description = (
                    f"[{match_details.voting.map.pick[0]}]"
                    f"(https://www.faceit.com/en/cs2/room/{match_details.match_id})"
                    f"{' - ' + location.pick[0] if location else ''}"
                    f" - {match_ready.payload.entity.name}"
                )
            await message.edit(embeds=message.embeds)
            break


discord_client = DiscordClient(
    faceit_channel_id=828940900033626113, intents=discord.Intents.all()
)
tree = app_commands.CommandTree(discord_client)


@tree.command(name="stats", description="Show last 10 matches stats from a player")
async def stats(ctx: Interaction, player: str) -> None:
    await ctx.response.send_message(
        "Retrieving stats...", ephemeral=True, delete_after=5.0
    )
    imgclst = LastStatsImCol(player)
    image = await imgclst.collect_image()
    await discord_client.faceit_channel.send(
        file=discord_client.compile_binary_image(image)
    )


@tree.command(name="compare", description="Compare 2 players")
async def compare(ctx: Interaction, player_1: str, player_2: str, amount: int) -> None:
    await ctx.response.send_message(
        "Retrieving stats...", ephemeral=True, delete_after=5.0
    )
    imgcmpr = CompareImCol(
        nickname1=player_1,
        nickname2=player_2,
        amount=amount,
        output_type="games",
    )
    image = await imgcmpr.collect_image()
    await discord_client.faceit_channel.send(
        file=discord_client.compile_binary_image(image)
    )


@tree.command(name="bet", description="Bet points for match results")
async def bet(ctx: Interaction, match: str, bet_type: BetType, amount: int) -> None:
    logger.info(f"Bet from ({ctx.user.name}: {ctx.user.id})")
    logger.info(f"{match=}, {bet_type=}, {amount=}")
    if not match.startswith("m") or len(match) < 2 or not match[1:].isdigit():
        await ctx.response.send_message(
            "Please, input appropriate match id. It should be in format like 'm1'",
            ephemeral=True,
            delete_after=5.0,
        )
        return None
    bet_match_id = int(match[1:])

    async with session_maker() as session:
        bet_match = await gambling_repo.get_bet_match_by_id(
            session=session, bet_match_id=bet_match_id
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
        if current_balance - amount < 0:
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
            bet_type=bet_type,
            amount=amount,
        )
        await session.commit()
        logger.info("Bet accepted")

    await ctx.response.send_message(
        f"Your bet is accepted. {amount} points on {bet_type}. Match id [{match}]",
        ephemeral=True,
    )


@tree.command(name="balance", description="Display current amount of points")
async def balance(ctx: Interaction) -> None:
    async with session_maker() as session:
        current_balance = await gambling_repo.get_balance(
            session=session, member_id=str(ctx.user.id)
        )
        await ctx.response.send_message(
            f"Your current balance is {current_balance}",
            ephemeral=True,
        )


class MyView(discord.ui.View):
    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="😎", row=0)
    async def button_callback(self, button, interaction):
        logger.info(f"{type(button), button}")
        logger.info(f"{type(interaction), interaction}")

        await interaction.response.send_message("You clicked the button!", ephemeral=True)

    @discord.ui.select(options=[SelectOption(label="Team 1", value=BetType.T1_WIN), SelectOption(label="Team 2", value=BetType.T2_WIN)])
    async def bet_type_select(self, *args, **kwargs):
        logger.info(f"{args, kwargs = }")

    @discord.ui.button(label="R1-1", style=discord.ButtonStyle.primary, emoji="😎", row=1)
    async def b1(self, button, interaction):
        pass

    @discord.ui.button(label="R1-2", style=discord.ButtonStyle.primary, emoji="😎", row=1)
    async def b2(self, button, interaction):
        pass

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.primary, emoji="😎", row=1)
    async def b3(self, button, interaction):
        pass


@tree.command(name="buttons", description="Command to test view with buttons")
async def buttons(ctx: Interaction) -> None:
    logger.info(f"{type(ctx) = }")
    await ctx.response.send_message(view=MyView())
