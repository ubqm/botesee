import asyncio
import re
from io import BytesIO
from typing import Any

import aiohttp
import discord
import httpx
from aiohttp import ClientConnectorError
from discord import Intents, RawReactionActionEvent

from api_funcs.async_faceit_get_funcs import (get_player_elo_by_nickname,
                                              match_stats)
from database import db_match_finished
from discord_bot._exceptions import StartMessageNotFoundException
from discord_bot.models.embed import NickEloStorage
from discord_bot.models.match_stats import MatchStatistics
from env_variables import faceit_headers

from image_collectors.compare_collector import ImageCollectorCompare
from image_collectors.finished_collector import \
    ImageCollectorMatchFinished
from image_collectors.stats_collector import ImageCollectorStatLast
from models.entities import Player
from models.events import MatchReady, MatchFinished, MatchAborted
from utils.enums import subscribers


def get_strnick_embed_color(statistics: MatchStatistics):
    black, green, red, gray = 1, 2067276, 10038562, 9936031
    my_color = black

    # flag for situations where 2 of sub_players are in both teams
    is_found_in_first_team = False
    str_nick = ""
    for idx_team, team in enumerate(statistics.rounds[0].teams):
        if idx_team == 1:
            str_nick += "\n"
        for player in team.players:
            str_nick += (f"[{player.nickname}]"
                         f"(https://www.faceit.com/en/players/{player.nickname}), ")
            if player.player_id in subscribers:
                if idx_team == 0:
                    is_found_in_first_team = True
                my_color = green if team.team_stats.team_win else red
                if idx_team == 1 and is_found_in_first_team:
                    my_color = gray
                    break
    str_nick = str_nick[:-2]  # last two symbols are ", "
    return str_nick, my_color


async def get_nicks_and_elo(session, roster: list[Player]) -> NickEloStorage:
    nicknames: str = ""
    elos: str = ""
    for player in roster:
        nicknames += (f"[{player.nickname}]"
                      f"(https://www.faceit.com/en/players/{player.nickname})\n")
        elos += str(await get_player_elo_by_nickname(session, player.nickname)) + "\n"
    return NickEloStorage(nicknames=nicknames, elos=elos)


def form_ready_embed_message(
        match: MatchReady, nick_elo_1: NickEloStorage, nick_elo_2: NickEloStorage
) -> discord.Embed:
    my_color = 9936031
    description = f"[{match.payload.id}](https://www.faceit.com/en/csgo/room/{match.payload.id})"
    embed_msg = discord.Embed(title="Match Ready", type="rich", description=description, color=my_color)
    embed_msg.add_field(name=match.payload.teams[0].name,
                        value=nick_elo_1.nicknames,
                        inline=True)
    embed_msg.add_field(name="ELO", value=nick_elo_1.elos, inline=True)
    embed_msg.add_field(name="\u200b", value="\u200b")
    embed_msg.add_field(name=match.payload.teams[1].name,
                        value=nick_elo_2.nicknames,
                        inline=True)
    embed_msg.add_field(name="ELO", value=nick_elo_2.elos, inline=True)
    embed_msg.add_field(name="\u200b", value="\u200b")
    return embed_msg


class DiscordClient(discord.Client):

    def __init__(self, faceit_channel_id: int, intents: Intents, **options: Any):
        super().__init__(intents=intents, options=options)
        self.faceit_channel = self.get_channel(faceit_channel_id)

    async def on_ready(self):
        for guild in self.guilds:
            print(
                f"Logged in as {self.user}, "
                f"server: {guild.name}, "
                f"guild_id:{guild.id}"
            )

    @staticmethod
    def compile_binary_image(image):
        if image is not None:
            with BytesIO() as image_binary:
                image.save(image_binary, "PNG")
                image_binary.seek(0)
                binary_image = discord.File(fp=image_binary, filename="image.png")
                return binary_image

    @staticmethod
    def is_contains_media(message: discord.Message):
        return any(("http://" in message.content, message.attachments,
                    "https://" in message.content, message.embeds))

    @staticmethod
    def is_stats_request(content: list):
        return bool(re.search("^[.]stats?$", content[0]) and len(content) == 2)

    @staticmethod
    def is_compare_request(content: list):
        return bool(re.search(r"^[.]compare$", content[0])) and len(content) == 5

    async def on_message(self, message):
        print(f"New message from {message.author}: {message.content}")
        _content: list = message.content.split()
        if message.author.id != self.user.id:  # 825393722186924112
            if self.is_contains_media(message):
                await message.add_reaction("👍")
                await message.add_reaction("👎")
            elif self.is_stats_request(_content):
                imgclst = ImageCollectorStatLast(_content[1])
                image = await imgclst.collect_image()
                await self.faceit_channel.send(file=self.compile_binary_image(image))
            elif self.is_compare_request(_content):
                imgcmpr = ImageCollectorCompare(*_content[1:])
                image = await imgcmpr.collect_image()
                await self.faceit_channel.send(file=self.compile_binary_image(image))
            elif bool(re.search(r"^[.]$", _content[0])):
                pass

    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        await self._handle_reaction_event(payload)

    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent) -> None:
        await self._handle_reaction_event(payload)

    async def _handle_reaction_event(self, payload: RawReactionActionEvent):
        upvotes = downvotes = 0
        print(payload)
        if payload.emoji.name not in ("👍", "👎"):
            return

        channel = discord.Client.get_channel(self, payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        print(
            f"Emoji {payload.emoji} {payload.event_type} by:{payload.member}, "
            f"Message by: {message.author}, Message: {message.content}"
        )

        for reaction in message.reactions:
            if reaction.emoji == "👍":
                upvotes = len([user async for user in reaction.users() if len(user.roles) > 1])
            elif reaction.emoji == "👎":
                downvotes = len([user async for user in reaction.users() if len(user.roles) > 1])

        print(f"Upvotes/Downvotes = {upvotes}/{downvotes}")
        if upvotes < downvotes - 2:
            await message.delete()
            print(
                f'*** Message "{message.content}" '
                f"deleted with {upvotes} Upvotes, "
                f"{downvotes} Downvotes\n"
            )

    async def post_faceit_message_ready(self, channel_id: int, match: MatchReady) -> None:
        channel = self.get_channel(channel_id)
        async with aiohttp.ClientSession(headers=faceit_headers) as session:
            nick_elo_1 = await get_nicks_and_elo(session, match.payload.teams[0].roster)
            nick_elo_2 = await get_nicks_and_elo(session, match.payload.teams[1].roster)
        embed_msg = form_ready_embed_message(match, nick_elo_1, nick_elo_2)
        await channel.send(embed=embed_msg)

    async def post_faceit_message_finished(self, channel_id, match: MatchFinished):
        channel = self.get_channel(channel_id)

        async with aiohttp.ClientSession(headers=faceit_headers) as session:
            statistics = await match_stats(session, match.payload.id)

        await db_match_finished(match, statistics)

        # TODO: for round in statistics.rounds
        str_nick, my_color = get_strnick_embed_color(statistics)
        embed_msg = discord.Embed(
            description=str_nick,
            type="rich",
            title=f"{statistics.rounds[0].round_stats.map}",
            color=my_color,
            url=f"https://www.faceit.com/en/csgo/room/{match.payload.id}",
        )
        nick_elo_1, nick_elo_2 = await self.delete_message_by_faceit_match_id(channel_id, match.payload.id)

        # TODO:
        img_collector = ImageCollectorMatchFinished(
            request_json, statistics, nick1, elo1, nick2, elo2
        )
        image_list = await img_collector.collect_image()
        for image in image_list:
            embed_msg.set_image(url="attachment://image.png")
            await channel.send(embed=embed_msg, file=self.compile_binary_image(image))

    async def post_faceit_message_aborted(self, channel_id, match: MatchAborted):
        await self.delete_message_by_faceit_match_id(channel_id, match.payload.id)

    async def delete_message_by_faceit_match_id(
            self, channel_id: int, match_id: str
    ) -> tuple[NickEloStorage, NickEloStorage]:
        channel = discord.Client.get_channel(self, channel_id)
        messages = [message async for message in channel.history(limit=20)]
        for message in messages:
            if not message.embeds:
                continue
            if not (match_id in message.embeds[0].description):
                continue
            # get nicknames from URL-embed discord format [nickname](URL)
            nick1 = "\n".join(re.findall(r"\[(?P<nickname>.*)]", message.embeds[0].fields[0].value))
            elo1 = message.embeds[0].fields[1].value
            nick2 = "\n".join(re.findall(r"\[(?P<nickname>.*)]", message.embeds[0].fields[3].value))
            elo2 = message.embeds[0].fields[4].value
            await message.delete()
            return NickEloStorage(nicknames=nick1, elos=elo1), NickEloStorage(nicknames=nick2, elos=elo2)
        raise StartMessageNotFoundException
