import asyncio
import re
from collections import namedtuple
from io import BytesIO

import aiohttp
import discord
from aiohttp import ClientConnectorError
from discord import Message

from api_funcs.async_faceit_get_funcs import get_player_elo_by_nickname, match_stats
from database import db_match_finished
from env_variables import faceit_headers
from ImageCollectors.ImageCollectorCompare import ImageCollectorCompare
from ImageCollectors.ImageCollectorMatchFinished import ImageCollectorMatchFinished
from ImageCollectors.ImageCollectorStatLast import ImageCollectorStatLast

AYUDESEE = "ad42c90b-45a9-49b6-8ab0-9c8662330543"
NAPAD = "278790a2-1f08-4350-bd96-427f7dcc8722"
MORZY = "18e2a663-9e20-4db9-8b29-3c3cbdff30ac"
HAWK = "8cbb0b36-4c6b-4ebd-a92b-829234016626"
DELPIX = "e1cddcbb-afdc-4e8e-abf2-eea5638f0363"
SPARTACUS = "9da3572e-1960-4ba0-bd3c-d38ef34c1f1c"
DG = "b8e5cd07-1b43-4203-9173-465fddcd391f"
QZAC = "4e7d1f6c-9045-4800-8eda-23c892dcd814"
DANTIST = "24785d80-7265-4f50-970e-1c02666ede56"


class MyDiscordClient(discord.Client):
    sub_players = [AYUDESEE, NAPAD, MORZY, HAWK, DELPIX, SPARTACUS, DG, QZAC, DANTIST]

    async def on_ready(self):
        for guild in self.guilds:
            print(
                f"Logged on as {self.user}, "
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
    def is_contains_media(message: Message):
        return any(
            (
                message.attachments,
                message.embeds,
                message.content.find("https://") != -1,
                message.content.find("http://") != -1,
            )
        )

    @staticmethod
    def is_stats_request(content: list):
        return bool(re.search("^[.]stats?$", content[0]) and len(content) == 2)

    @staticmethod
    def is_compare_request(content: list):
        return bool(re.search(r"^[.]compare$", content[0])) and len(content) == 5

    async def on_message(self, message):
        print(f"New message from {message.author}: {message.content}")
        _content: list = message.content.split()
        if message.author.id != 825393722186924112:
            if self.is_contains_media(message):
                await message.add_reaction("👍")
                await message.add_reaction("👎")
            elif self.is_stats_request(_content):
                channel = self.get_channel(id=828940900033626113)
                imgclst = ImageCollectorStatLast(_content[1])
                image = await imgclst.collect_image()
                await channel.send(file=self.compile_binary_image(image))
            elif self.is_compare_request(_content):
                channel = self.get_channel(id=828940900033626113)
                imgcmpr = ImageCollectorCompare(*_content[1:])
                image = await imgcmpr.collect_image()
                await channel.send(file=self.compile_binary_image(image))
            elif bool(re.search(r"^[.]$", _content[0])):
                pass

    async def on_raw_reaction_add(self, payload):
        upvotes = 0
        downvotes = 0
        users_upvote = []
        users_downvote = []
        if payload.emoji.name == "👍" or payload.emoji.name == "👎":
            print(payload)
            channel = discord.Client.get_channel(self, payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            print(
                f"Emoji {payload.emoji} added by:{payload.member}, "
                f"Message by: {message.author}, Message: {message.content}"
            )

            for reaction in message.reactions:
                if reaction.emoji == "👍":
                    users_upvote = await reaction.users().flatten()
                elif reaction.emoji == "👎":
                    users_downvote = await reaction.users().flatten()
            for user in users_upvote:
                if len(user.roles) > 1:
                    upvotes += 1
            for user in users_downvote:
                if len(user.roles) > 1:
                    downvotes += 1

            print(f"Upvotes/Downvotes = {upvotes}/{downvotes}")
            if upvotes < downvotes - 2:
                await message.delete()
                print(
                    f'*** Message "{message.content}" '
                    f"deleted with {upvotes} Upvotes, "
                    f"{downvotes} Downvotes\n"
                )

    async def on_raw_reaction_remove(self, payload):
        upvotes = 0
        downvotes = 0
        users_upvote = []
        users_downvote = []
        if payload.emoji.name == "👍" or payload.emoji.name == "👎":
            print(payload)
            channel = discord.Client.get_channel(self, payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            print(
                f"Emoji {payload.emoji} removed by:{payload.member}, "
                f"Message by: {message.author}, Message: {message.content}"
            )

            for reaction in message.reactions:
                if reaction.emoji == "👍":
                    users_upvote = await reaction.users().flatten()
                elif reaction.emoji == "👎":
                    users_downvote = await reaction.users().flatten()
            for user in users_upvote:
                if len(user.roles) > 1:
                    upvotes += 1
            for user in users_downvote:
                if len(user.roles) > 1:
                    downvotes += 1

            print(f"Upvotes/Downvotes = {upvotes}/{downvotes}")
            if upvotes < downvotes - 2:
                await message.delete()
                print(
                    f'*** Message "{message.content}" '
                    f"deleted with {upvotes} Upvotes, "
                    f"{downvotes} Downvotes\n"
                )

    async def post_faceit_message_ready(self, channel_id, request_json):
        channel = self.get_channel(id=channel_id)
        my_color = 9936031
        embed_msg = discord.Embed(
            title="Match Ready",
            type="rich",
            description=f"[{request_json['payload']['id']}]"
            f"(https://www.faceit.com/en/csgo/room/"
            f"{request_json['payload']['id']})",
            color=my_color,
        )
        str_nick1 = ""
        str_nick2 = ""
        elo1 = ""
        elo2 = ""
        for i in range(12):
            try:
                async with aiohttp.ClientSession(headers=faceit_headers) as session:
                    for idx_team, team in enumerate(request_json["payload"]["teams"]):
                        for player in team["roster"]:
                            if idx_team == 0:
                                str_nick1 += (
                                    f"[{player['nickname']}](https://www.faceit.com/en/players/{player['nickname']})"
                                    + "\n"
                                )
                                player_elo = await get_player_elo_by_nickname(
                                    session, player["nickname"]
                                )
                                elo1 += player_elo + "\n"
                            else:
                                str_nick2 += (
                                    f"[{player['nickname']}](https://www.faceit.com/en/players/{player['nickname']})"
                                    + "\n"
                                )
                                player_elo = await get_player_elo_by_nickname(
                                    session, player["nickname"]
                                )
                                elo2 += player_elo + "\n"

                embed_msg.add_field(
                    name=request_json["payload"]["teams"][0]["name"],
                    value=str_nick1,
                    inline=True,
                )
                embed_msg.add_field(name="ELO", value=elo1, inline=True)
                embed_msg.add_field(name="\u200b", value="\u200b")
                embed_msg.add_field(
                    name=request_json["payload"]["teams"][1]["name"],
                    value=str_nick2,
                    inline=True,
                )
                embed_msg.add_field(name="ELO", value=elo2, inline=True)
                embed_msg.add_field(name="\u200b", value="\u200b")
                await channel.send(embed=embed_msg)
                break
            except ClientConnectorError as e:
                print(e)
                await asyncio.sleep(5)

    def get_strnick_embed_color(self, statistics):
        black, green, red, gray = 1, 2067276, 10038562, 9936031
        my_color = black

        # flag for situations where 2 of sub_players are in both teams
        is_found_in_first_team = False
        str_nick = ""
        for idx_team, team in enumerate(statistics["rounds"][0]["teams"]):
            if idx_team == 1:
                str_nick += "\n"
            for player in team["players"]:
                str_nick += f"[{player['nickname']}](https://www.faceit.com/en/players/{player['nickname']}), "
                if player["player_id"] in self.sub_players:
                    if idx_team == 0:
                        is_found_in_first_team = True
                    my_color = green if team["team_stats"]["Team Win"] == "1" else red
                    if idx_team == 1 and is_found_in_first_team:
                        my_color = gray
                        break
        str_nick = str_nick[:-2]  # last two symbols are ", "
        return str_nick, my_color

    async def post_faceit_message_finished(self, channel_id, request_json):
        channel = self.get_channel(id=channel_id)

        # loop to wait FaceIt API for 1 minute if we hadn't got response
        statistics = None
        async with aiohttp.ClientSession(headers=faceit_headers) as session:
            for _ in range(12):
                statistics = await match_stats(session, request_json["payload"]["id"])
                if statistics:
                    break
                await asyncio.sleep(5)

        await db_match_finished(request_json, statistics)

        str_nick, my_color = self.get_strnick_embed_color(statistics)
        embed_msg = discord.Embed(
            description=str_nick,
            type="rich",
            title=f"{statistics['rounds'][0]['round_stats']['Map']}",
            color=my_color,
            url=f"https://www.faceit.com/en/csgo/room/{request_json['payload']['id']}",
        )
        nick1, elo1, nick2, elo2 = await self.delete_message_by_faceit_match_id(
            match_id=request_json["payload"]["id"]
        )

        img_collector = ImageCollectorMatchFinished(
            request_json, statistics, nick1, elo1, nick2, elo2
        )
        image_list = await img_collector.collect_image()
        for image in image_list:
            embed_msg.set_image(url="attachment://image.png")
            await channel.send(embed=embed_msg, file=self.compile_binary_image(image))

    async def post_faceit_message_aborted(self, channel_id, request_json):
        await self.delete_message_by_faceit_match_id(
            channel_id, request_json["payload"]["id"]
        )

    async def delete_message_by_faceit_match_id(
        self, channel_id=828940900033626113, match_id=None
    ):
        channel = discord.Client.get_channel(self, channel_id)
        messages = await channel.history(limit=10).flatten()
        nick1, elo1, nick2, elo2 = "", "", "", ""
        for message in messages:
            if message.embeds and match_id in message.embeds[0].description:
                nick1 = "\n".join(
                    re.findall(
                        r"\[(?P<nickname>.*)]", message.embeds[0].fields[0].value
                    )
                )
                elo1 = message.embeds[0].fields[1].value
                nick2 = "\n".join(
                    re.findall(
                        r"\[(?P<nickname>.*)]", message.embeds[0].fields[3].value
                    )
                )
                elo2 = message.embeds[0].fields[4].value
                await message.delete()
        return nick1, elo1, nick2, elo2
