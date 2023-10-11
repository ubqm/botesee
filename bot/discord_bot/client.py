import asyncio
import re
from io import BytesIO
from typing import Any

import aiohttp
import discord
from discord import Intents, Interaction, Member, RawReactionActionEvent, TextChannel, app_commands
from loguru import logger

from bot import conf
from bot.clients.faceit import FaceitClient
from bot.clients.models.faceit.match_details import MatchDetails
from bot.clients.models.faceit.match_stats import MatchStatistics
from bot.db.script import db_match_finished
from bot.discord_bot.models.embed import NickEloStorage, PlayerStorage
from bot.image_collectors._exceptions import BadAPICallException
from bot.image_collectors.compare_imcol import CompareImCol
from bot.image_collectors.last_stat_imcol import LastStatsImCol
from bot.image_collectors.match_finished import MatchFinishedImCol
from bot.utils.enums import subscribers
from bot.web.models.base import Player
from bot.web.models.events import MatchAborted, MatchFinished, MatchReady


@logger.catch()
def get_match_finished_message_color(statistics: MatchStatistics) -> int:
    black, green, red, gray = 1, 2067276, 10038562, 9936031
    teams_subscribers_found = [False, False]  # Team1 and Team2 boolean
    for idx_team, team in enumerate(statistics.rounds[0].teams):
        for player in team.players:
            if player.player_id in subscribers:
                teams_subscribers_found[idx_team] = True
    if all(teams_subscribers_found):
        return gray
    if not any(teams_subscribers_found):
        return black
    if (teams_subscribers_found[0] and statistics.rounds[0].teams[0].team_stats.team_win) or (
        teams_subscribers_found[1] and statistics.rounds[0].teams[1].team_stats.team_win
    ):
        return green
    return red


@logger.catch()
def get_strnick_embed_color(statistics: MatchStatistics) -> tuple[str, int]:
    color = get_match_finished_message_color(statistics)

    nicknames_1 = [
        f"[{player.nickname}](https://www.faceit.com/en/players/{player.nickname})"
        for player in statistics.rounds[0].teams[0].players
    ]
    nicknames_2 = [
        f"[{player.nickname}](https://www.faceit.com/en/players/{player.nickname})"
        for player in statistics.rounds[0].teams[1].players
    ]
    str_nick_1 = ", ".join(nicknames_1)
    str_nick_2 = ", ".join(nicknames_2)

    return str_nick_1 + "\n" + str_nick_2, color


async def get_nicks_and_elo(session, roster: list[Player], game: str = "cs2") -> NickEloStorage:
    players_storage: list[PlayerStorage] = []
    for player in roster:
        elo = await FaceitClient.get_player_elo_by_nickname(session, player.nickname, game)
        players_storage.append(PlayerStorage(nickname=player.nickname, elo=elo))
    return NickEloStorage(players=players_storage)


@logger.catch
def form_ready_embed_message(
    match: MatchReady, nick_elo_1: NickEloStorage, nick_elo_2: NickEloStorage
) -> discord.Embed:
    my_color = 9936031  # gray
    description = f"[{match.payload.id}](https://www.faceit.com/en/cs2/room/{match.payload.id})"
    embed_msg = discord.Embed(
        title=f"[{match.payload.game}] Ongoing Match", type="rich", description=description, color=my_color
    )
    embed_msg.add_field(
        name=match.payload.teams[0].name,
        value=nick_elo_1.get_discord_nicknames(),
        inline=True,
    )
    embed_msg.add_field(name="ELO", value=nick_elo_1.get_discord_elos(), inline=True)
    embed_msg.add_field(name="\u200b", value="\u200b")
    embed_msg.add_field(
        name=match.payload.teams[1].name,
        value=nick_elo_2.get_discord_nicknames(),
        inline=True,
    )
    embed_msg.add_field(name="ELO", value=nick_elo_2.get_discord_elos(), inline=True)
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
    @logger.catch()
    def compile_binary_image(image):
        if image is not None:
            with BytesIO() as image_binary:
                image.save(image_binary, "PNG")
                image_binary.seek(0)
                binary_image = discord.File(fp=image_binary, filename="image.png")
                return binary_image

    @staticmethod
    @logger.catch()
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
    @logger.catch()
    def is_stats_request(content: list) -> bool:
        return bool(re.search("^[.]stats?$", content[0]) and len(content) == 2)

    @staticmethod
    @logger.catch()
    def is_compare_request(content: list) -> bool:
        return bool(re.search(r"^[.]compare$", content[0])) and (len(content) in (3, 5))

    @logger.catch()
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

    @logger.catch()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        await self._handle_reaction_event(payload)

    @logger.catch()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent) -> None:
        await self._handle_reaction_event(payload)

    @logger.catch()
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
                    [user async for user in reaction.users() if isinstance(user, Member) and len(user.roles) > 1]
                )
            elif reaction.emoji == "👎":
                downvotes = len(
                    [user async for user in reaction.users() if isinstance(user, Member) and len(user.roles) > 1]
                )

        logger.info(
            f"[{upvotes}/{downvotes}] {payload.emoji} {payload.event_type} by {payload.member} | "
            f"Message by {message.author}: {message.content}"
        )
        if upvotes < downvotes - 2:
            await message.delete()
            logger.info(f'Message "{message.content}" ' f"deleted with {upvotes} Upvotes, " f"{downvotes} Downvotes\n")

    @logger.catch
    async def post_faceit_message_ready(self, match: MatchReady) -> None:
        if not self.faceit_channel:
            raise ConnectionError("Discord is not initialized yet")
        async with aiohttp.ClientSession(headers=conf.FACEIT_HEADERS) as session:
            nick_elo_1 = await get_nicks_and_elo(session, match.payload.teams[0].roster, game=match.payload.game)
            nick_elo_2 = await get_nicks_and_elo(session, match.payload.teams[1].roster, game=match.payload.game)
        embed_msg = form_ready_embed_message(match, nick_elo_1, nick_elo_2)
        await self.faceit_channel.send(embed=embed_msg)

    @logger.catch
    async def post_faceit_message_finished(self, match: MatchFinished) -> None:
        if not self.faceit_channel:
            raise ConnectionError("Discord is not initialized yet")
        async with aiohttp.ClientSession(headers=conf.FACEIT_HEADERS) as session:
            retry_count = 1
            while retry_count < 10:
                try:
                    statistics = await FaceitClient.match_stats(session, match.payload.id)
                except BadAPICallException as e:
                    logger.warning(e)
                    retry_count += 1
                    if retry_count == 10:
                        raise Exception(f"could not get statistics from Finished match {match.payload.id}")
                    await asyncio.sleep(retry_count**2)
                else:
                    break

        await db_match_finished(match, statistics)

        # TODO: for round in statistics.rounds
        str_nick, my_color = get_strnick_embed_color(statistics)
        embed_msg = discord.Embed(
            description=str_nick,
            type="rich",
            title=f"{statistics.rounds[0].round_stats.map} [{match.payload.game}]",
            color=my_color,
            url=f"https://www.faceit.com/en/cs2/room/{match.payload.id}",
        )
        nick_elo = await self.delete_message_by_faceit_match_id(match.payload.id)
        if not nick_elo:
            return

        img_collector = MatchFinishedImCol(match, statistics, nick_elo)
        image_list = await img_collector.collect_images()
        for image in image_list:
            embed_msg.set_image(url="attachment://image.png")
            await self.faceit_channel.send(embed=embed_msg, file=self.compile_binary_image(image))

    @logger.catch
    async def post_faceit_message_aborted(self, match: MatchAborted) -> None:
        await self.delete_message_by_faceit_match_id(match.payload.id)

    @logger.catch
    async def delete_message_by_faceit_match_id(self, match_id: str) -> NickEloStorage | None:
        if not self.faceit_channel:
            raise ConnectionError("Discord is not initialized yet")

        async for message in self.faceit_channel.history(limit=40):  # type: discord.Message
            if not message.embeds:
                continue

            if message_description := message.embeds[0].description:
                if match_id not in message_description:
                    continue

            # get nicknames from URL-embed discord format [nickname](URL)
            if not message.embeds or not message.embeds[0].fields:
                return None

            nick1 = re.findall(r"\[(?P<nickname>.*?)]", str(message.embeds[0].fields[0].value))
            elo1_temp = str(message.embeds[0].fields[1].value).split("\n")  # type: list[str]
            elo1 = [int(item) for item in elo1_temp]  # type: list[int]
            st1 = [PlayerStorage(nickname=nickname, elo=elo) for nickname, elo in zip(nick1, elo1)]

            nick2 = re.findall(r"\[(?P<nickname>.*?)]", str(message.embeds[0].fields[3].value))
            elo2_temp = str(message.embeds[0].fields[4].value).split("\n")  # type: list[str]
            elo2 = [int(item) for item in elo2_temp]  # type: list[int]
            st2 = [PlayerStorage(nickname=nickname, elo=elo) for nickname, elo in zip(nick2, elo2)]

            await message.delete()
            return NickEloStorage(players=st1 + st2)
        return None

    @logger.catch
    async def update_score_for_match(self, match_details: MatchDetails) -> None:
        if not self.faceit_channel:
            raise ConnectionError("Discord is not initialized yet")

        async for message in self.faceit_channel.history(limit=40):
            if not message.embeds:
                continue
            if match_details.match_id not in str(message.embeds[0].description):
                continue

            new_embed = message.embeds[0]
            new_embed.title = f"[{match_details.game}] Ongoing Match [{match_details.current_score}]"
            if match_details.voting:
                location = match_details.voting.location
                new_embed.description = (
                    f"[{match_details.voting.map.pick[0]}]"
                    f"(https://www.faceit.com/en/cs2/room/{match_details.match_id})"
                    f"{' - ' + location.pick[0] if location else ''}"
                )
            await message.edit(embeds=message.embeds)
            break


discord_client = DiscordClient(faceit_channel_id=828940900033626113, intents=discord.Intents.all())
tree = app_commands.CommandTree(discord_client)


@logger.catch
@tree.command(name="stats", description="Show last 10 matches stats from a player")
async def stats(ctx: Interaction, player: str) -> None:
    await ctx.response.send_message("Retrieving stats...", ephemeral=True, delete_after=5.0)
    imgclst = LastStatsImCol(player)
    image = await imgclst.collect_image()
    await discord_client.faceit_channel.send(file=discord_client.compile_binary_image(image))


@logger.catch
@tree.command(name="compare", description="Compare 2 players")
async def compare(ctx: Interaction, player_1: str, player_2: str, amount: int) -> None:
    await ctx.response.send_message("Retrieving stats...", ephemeral=True, delete_after=5.0)
    imgcmpr = CompareImCol(
        nickname1=player_1,
        nickname2=player_2,
        amount=amount,
        output_type="games",
    )
    image = await imgcmpr.collect_image()
    await discord_client.faceit_channel.send(file=discord_client.compile_binary_image(image))
