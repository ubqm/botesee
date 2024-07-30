import asyncio
from asyncio import Task
from io import BytesIO
from typing import Literal

from aiohttp_client_cache import CachedSession
from PIL import Image, ImageDraw, ImageFont

from src import redis_cache
from src.clients.faceit import faceit_client
from src.clients.models.faceit.match_stats import Player, Round
from src.discord_bot.models.embed import NickEloStorage, PlayerStorage
from src.image_collectors import TEMPLATE_PATH
from src.utils.enums import ColorTuple, available_maps, subscribers
from src.web.models.base import Player as webPlayer
from src.web.models.events import MatchFinished


class MatchFinishedImCol:
    font_folder = "Outfit"
    font_file = "Outfit-Bold.ttf"
    font_file_mainscore = "Outfit-ExtraBold.ttf"
    fonts = {
        "mainscore": ImageFont.truetype(
            f"{TEMPLATE_PATH}/fonts/{font_folder}/{font_file_mainscore}", 50
        ),
        "avatar": ImageFont.truetype(
            f"{TEMPLATE_PATH}/fonts/{font_folder}/{font_file}", 18
        ),
        "player_score": ImageFont.truetype(
            f"{TEMPLATE_PATH}/fonts/{font_folder}/{font_file}", 32
        ),
        "player_stats": ImageFont.truetype(
            f"{TEMPLATE_PATH}/fonts/{font_folder}/{font_file}", 22
        ),
        "halftime": ImageFont.truetype(
            f"{TEMPLATE_PATH}/fonts/{font_folder}/{font_file}", 22
        ),
    }
    image_dark_avatar_bot = Image.open(
        f"{TEMPLATE_PATH}/background_features/for_avatar_bot.png"
    )
    image_dark_avatar_top = Image.open(
        f"{TEMPLATE_PATH}/background_features/for_avatar_top.png"
    )
    image_avatar_top_border = Image.open(
        f"{TEMPLATE_PATH}/background_features/avatar_top_border.png"
    )
    image_avatar_bottom_border = Image.open(
        f"{TEMPLATE_PATH}/background_features/avatar_bottom_border.png"
    )

    def __init__(
        self,
        match: MatchFinished,
        match_round: Round,
        nick_elo: NickEloStorage | None = None,
    ):
        self.match = match
        self.match_round = match_round
        self.prev_nick_elo = nick_elo

    async def collect_image(self) -> Image:
        return await self._draw_image(self.match_round)

    async def _draw_image(self, round_: Round) -> Image:
        canvas: Image = await self._get_map_image(round_)
        canvas = await self._draw_players(round_, canvas)
        return canvas

    async def _get_map_image(self, round_: Round) -> Image:
        canvas: Image = await self._get_background(round_)
        canvas = await self._draw_win_features(round_, canvas)
        await self._draw_game_score(round_, canvas)
        return canvas

    async def _draw_players(self, round_: Round, canvas: Image) -> Image:
        tasks: list[Task] = []
        for idx_team, team in enumerate(round_.teams):
            for idx_player, player in enumerate(team.players):
                task = asyncio.create_task(
                    self._draw_player(canvas, player, idx_team, idx_player)
                )
                tasks.append(task)
        await asyncio.gather(*tasks)
        return canvas

    async def _draw_player(
        self,
        canvas: Image,
        player: Player,
        idx_team: int,
        idx_player: int,
    ) -> Image:
        canvas = await self._draw_player_avatar(canvas, player, idx_team, idx_player)
        await self._draw_player_stats(player, canvas, idx_team, idx_player)
        return canvas

    @staticmethod
    def _get_kd_color(player: Player) -> ColorTuple:
        if player.player_stats.kd_ratio >= 1.3:
            return ColorTuple.GREEN
        elif player.player_stats.kd_ratio < 0.6:
            return ColorTuple.RED
        elif 0.8 > player.player_stats.kd_ratio >= 0.6:
            return ColorTuple.ORANGE
        else:
            return ColorTuple.WHITE

    def _draw_player_stat(
        self,
        stat: Literal["kad", "mvp", "kr", "kd"],
        player: Player,
        canvas: Image,
        idx_team: int,
        idx_player: int,
        kd_color: ColorTuple,
    ):
        image_draw = ImageDraw.Draw(canvas)
        stat_dict = {
            "kad": f"{player.player_stats.kills}/"
            f"{player.player_stats.assists}/"
            f"{player.player_stats.deaths}",
            "mvp": f"MVP: {player.player_stats.mvps}",
            "kr": f"K/R: {player.player_stats.kr_ratio}",
            "kd": f"K/D: {player.player_stats.kd_ratio}",
        }
        text = stat_dict[stat]
        w = image_draw.textlength(
            text,
            font=self.fonts["player_score"]
            if stat == "kad"
            else self.fonts["player_stats"],
        )
        stat_pos_dict = {
            "kad": (130 + (162 - w) / 2 + idx_player * 162, 155 + 195 * idx_team),
            "mvp": (156 + idx_player * 162, 240 + 36 * idx_team),
            "kr": (156 + idx_player * 162, 220 + 76 * idx_team),
            "kd": (156 + idx_player * 162, 200 + 116 * idx_team),
        }
        image_draw.text(
            stat_pos_dict[stat],
            text,
            font=self.fonts["player_score"]
            if stat == "kad"
            else self.fonts["player_stats"],
            fill=kd_color if stat == "kd" else ColorTuple.WHITE,
        )

    async def _draw_player_stats(
        self, player: Player, canvas: Image, idx_team: int, idx_player: int
    ) -> None:
        kd_color = self._get_kd_color(player)
        kad: Literal["kad"] = "kad"
        mvp: Literal["mvp"] = "mvp"
        kr: Literal["kr"] = "kr"
        kd: Literal["kd"] = "kd"
        vals: tuple[Literal["kad", "mvp", "kr", "kd"], ...] = (kad, mvp, kr, kd)
        for stat in vals:
            self._draw_player_stat(stat, player, canvas, idx_team, idx_player, kd_color)

    async def _download_player_avatar(self, req_player: webPlayer) -> Image:
        avatar_size = (130, 130)
        unknown_avatar = Image.open(f"{TEMPLATE_PATH}/question-mark-icon.jpg")
        unknown_avatar = unknown_avatar.resize(avatar_size)
        if not req_player.avatar:
            return unknown_avatar

        async with CachedSession(cache=redis_cache) as session:
            response = await session.get(req_player.avatar)

        if response.status != 200:
            return unknown_avatar

        actual_avatar = Image.open(BytesIO(await response.read()))
        actual_avatar = actual_avatar.convert("RGB")
        actual_avatar = actual_avatar.resize(avatar_size)
        return actual_avatar

    async def _draw_player_avatar(
        self,
        canvas: Image,
        player: Player,
        idx_team: int,
        idx_player: int,
    ) -> Image:
        draw_image = ImageDraw.Draw(canvas)
        player_elo = await faceit_client.get_player_elo_by_nickname(
            player.nickname, self.match.payload.game
        )
        elo_diff = await self.calculate_elo_change(player, player_elo)

        for idx_req_player, req_player in enumerate(
            self.match.payload.teams[idx_team].roster
        ):
            if player.nickname == req_player.nickname:
                image_avatar = await self._download_player_avatar(req_player)
                draw_image_avatar = ImageDraw.Draw(image_avatar)
                faceitlvl = req_player.game_skill_level

                image_avatar.paste(
                    self.image_dark_avatar_top, (0, 0), self.image_dark_avatar_top
                )
                image_avatar.paste(
                    self.image_dark_avatar_bot, (0, 0), self.image_dark_avatar_bot
                )
                if idx_team == 0:
                    image_avatar.paste(
                        Image.open(
                            f"{TEMPLATE_PATH}/faceit_icons/faceit{faceitlvl}.png"
                        ).convert("RGBA"),
                        (0, 0),
                        Image.open(
                            f"{TEMPLATE_PATH}/faceit_icons/faceit{faceitlvl}.png"
                        ).convert("RGBA"),
                    )

                    w = draw_image.textlength(elo_diff, font=self.fonts["avatar"])
                    draw_image_avatar.text(
                        (127 - w, 0), elo_diff, font=self.fonts["avatar"]
                    )
                    # w = self.draw_image_map.textlength(player_elo, font=self._fonts['avatar'])
                    draw_image_avatar.text(
                        (26, 0), str(player_elo), font=self.fonts["avatar"]
                    )
                    if player.player_id in subscribers:
                        canvas.paste(
                            self.image_avatar_top_border,
                            (146 + idx_player * 162, 0),
                            self.image_avatar_top_border,
                        )
                else:
                    image_avatar.paste(
                        Image.open(
                            f"{TEMPLATE_PATH}/faceit_icons/faceit{faceitlvl}.png"
                        ).convert("RGBA"),
                        (0, 106),
                        Image.open(
                            f"{TEMPLATE_PATH}/faceit_icons/faceit{faceitlvl}.png"
                        ).convert("RGBA"),
                    )

                    w = draw_image.textlength(elo_diff, font=self.fonts["avatar"])
                    draw_image_avatar.text(
                        (127 - w, 107), elo_diff, font=self.fonts["avatar"]
                    )
                    # w = self.draw_image_map.textlength(player_elo, font=self._fonts['avatar'])
                    draw_image_avatar.text(
                        (26, 107), str(player_elo), font=self.fonts["avatar"]
                    )
                    if player.player_id in subscribers:
                        canvas.paste(
                            self.image_avatar_bottom_border,
                            (146 + idx_player * 162, 520),
                            self.image_avatar_bottom_border,
                        )

                w = draw_image.textlength(
                    req_player.nickname, font=self.fonts["avatar"]
                )
                if w > 130:
                    draw_image_avatar.text(
                        (0, 107 - idx_team * 107),
                        req_player.nickname,
                        font=self.fonts["avatar"],
                    )
                else:
                    draw_image_avatar.text(
                        ((130 - w) / 2, 107 - idx_team * 107),
                        req_player.nickname,
                        font=self.fonts["avatar"],
                    )
                canvas.paste(
                    image_avatar, (146 + idx_player * 162, 20 + 370 * idx_team)
                )
        return canvas

    async def calculate_elo_change(self, player: Player, player_elo: int) -> str:
        if self.prev_nick_elo:
            elo_change = player_elo - self.prev_nick_elo[player.nickname].elo
        else:
            elo_change = 0
        return (
            f"(+{elo_change})"
            if elo_change > 0
            else f"({elo_change})"
            if elo_change < 0
            else ""
        )

    async def _draw_game_score(self, round_: Round, canvas: Image) -> None:
        await self._draw_final_score(round_, canvas)
        await self._draw_halftime_score(round_, canvas)

    async def _draw_halftime_score(self, round_: Round, canvas: Image) -> None:
        draw_image = ImageDraw.Draw(canvas)
        for idx_team, team in enumerate(round_.teams):
            halftimes = (
                f"{team.team_stats.first_half_score}—"
                f"{team.team_stats.second_half_score}"
            )
            if round_.has_overtime():
                halftimes += f"—{team.team_stats.overtime_score}"
            w = draw_image.textlength(halftimes, font=self.fonts["halftime"])
            draw_image.text(
                ((146 - w) / 2, 277 if idx_team else 235),
                halftimes,
                font=self.fonts["halftime"],
            )

    async def _draw_final_score(self, round_: Round, canvas: Image) -> None:
        draw_image = ImageDraw.Draw(canvas)
        for idx_team, team in enumerate(round_.teams):
            w = draw_image.textlength(
                str(team.team_stats.final_score),
                font=self.fonts["mainscore"],
            )
            draw_image.text(
                ((146 - w) / 2, 415 if idx_team else 65),
                str(team.team_stats.final_score),
                font=self.fonts["mainscore"],
            )

    async def _draw_win_features(self, round_: Round, canvas: Image) -> Image:
        top_image, bot_image = await self._get_win_feature_images(round_)
        dark_middle = Image.open(
            f"{TEMPLATE_PATH}/background_features/dark-middle2.png"
        )
        canvas.paste(top_image, (0, 0), top_image)
        canvas.paste(bot_image, (0, 0), bot_image)
        canvas.paste(dark_middle, (0, 0), dark_middle)
        return canvas

    async def _get_win_feature_images(self, round_: Round) -> tuple[Image, Image]:
        """Return green and red background features(First team is on top)"""
        if round_.teams[0].team_stats.team_win:
            image_topcolor = Image.open(
                f"{TEMPLATE_PATH}/background_features/Win-topleft.png"
            )
            image_botcolor = Image.open(
                f"{TEMPLATE_PATH}/background_features/Lose-botleft.png"
            )
            return image_topcolor, image_botcolor
        image_topcolor = Image.open(
            f"{TEMPLATE_PATH}/background_features/Lose-topleft.png"
        )
        image_botcolor = Image.open(
            f"{TEMPLATE_PATH}/background_features/Win-botleft.png"
        )
        return image_topcolor, image_botcolor

    async def _get_background(self, round_: Round) -> Image:
        if round_.round_stats.map not in available_maps.values:
            return Image.open(f"{TEMPLATE_PATH}/maps/black.png")

        image_map = Image.open(f"{TEMPLATE_PATH}/maps/cs2_{round_.round_stats.map}.jpg")
        image_map = image_map.resize((960, 540))
        return image_map


if __name__ == "__main__":

    def match_finished_():
        finished = {
            "transaction_id": "47c8ade3-db36-4c0a-8471-7c340e9d7ac8",
            "event": "match_status_finished",
            "event_id": "6db8bfa8-0bbc-4a19-88b1-ea93ae8e3005",
            "third_party_id": "ad42c90b-45a9-49b6-8ab0-9c8662330543",
            "app_id": "4ef06a92-08ba-425e-bf12-c49c17d5ec7e",
            "timestamp": "2022-01-10T20:29:35Z",
            "retry_count": 0,
            "version": 1,
            "payload": {
                "id": "1-37a40c85-82ae-436d-9f90-fb7db5484033",
                "organizer_id": "faceit",
                "region": "EU",
                "game": "csgo",
                "version": 43,
                "entity": {
                    "id": "a3c75828-7f0f-4940-adb9-994b4b389070",
                    "name": "CS:GO 5v5 PREMIUM",
                    "type": "matchmaking",
                },
                "teams": [
                    {
                        "id": "8d5ead5d-b1b6-458d-93d0-1a0548d2de3f",
                        "name": "team_CJ-2k",
                        "type": "",
                        "avatar": "https://distribution.faceit-cdn.net/images/3911c173-368e-4dbd-8b1f-b0d19ade695a.jpeg",
                        "leader_id": "8d5ead5d-b1b6-458d-93d0-1a0548d2de3f",
                        "co_leader_id": "",
                        "roster": [
                            {
                                "id": "278790a2-1f08-4350-bd96-427f7dcc8722",
                                "nickname": "-NAPAD",
                                "avatar": "https://assets.faceit-cdn.net/avatars/278790a2-1f08-4350-bd96-427f7dcc8722_1583523957971.jpg",
                                "game_id": "76561198061461007",
                                "game_name": "-NAPAD`11 #ACIDHOUZE",
                                "game_skill_level": 10,
                                "membership": "",
                                "anticheat_required": True,
                            },
                            {
                                "id": "d0b7218c-a540-423f-960e-f6e9a8b3b10a",
                                "nickname": "-EcoCobra-",
                                "avatar": "https://assets.faceit-cdn.net/avatars/d0b7218c-a540-423f-960e-f6e9a8b3b10a_1633631507859.jpg",
                                "game_id": "76561198391731293",
                                "game_name": "yowai mo",
                                "game_skill_level": 10,
                                "membership": "",
                                "anticheat_required": True,
                            },
                            {
                                "id": "6dc2d3a1-8653-4ce6-8a2c-cb30122361e8",
                                "nickname": "S1non--",
                                "avatar": "https://distribution.faceit-cdn.net/images/72491042-bdd6-4fc5-a8ba-e7fea300ac88.jpeg",
                                "game_id": "76561198251305342",
                                "game_name": "S1non",
                                "game_skill_level": 10,
                                "membership": "",
                                "anticheat_required": True,
                            },
                            {
                                "id": "131b67d6-3e3a-4a79-a4bc-7d73ea404c8e",
                                "nickname": "Deokishisu",
                                "avatar": "https://distribution.faceit-cdn.net/images/110c80b9-1f38-4426-9429-d6edeaa150c1.jpeg",
                                "game_id": "76561199174381757",
                                "game_name": "xGOD",
                                "game_skill_level": 10,
                                "membership": "",
                                "anticheat_required": True,
                            },
                            {
                                "id": "8d5ead5d-b1b6-458d-93d0-1a0548d2de3f",
                                "nickname": "CJ-2k",
                                "avatar": "https://distribution.faceit-cdn.net/images/3911c173-368e-4dbd-8b1f-b0d19ade695a.jpeg",
                                "game_id": "76561199006885634",
                                "game_name": "asd",
                                "game_skill_level": 10,
                                "membership": "",
                                "anticheat_required": True,
                            },
                        ],
                        "substitutions": 0,
                        "substitutes": None,
                    },
                    {
                        "id": "f8580374-5c09-43bc-bef2-463f1fde9aff",
                        "name": "team_sinnopsyy",
                        "type": "",
                        "avatar": "https://distribution.faceit-cdn.net/images/62a8416a-7cba-44b9-bab6-c5430f992eb9.jpeg",
                        "leader_id": "f8580374-5c09-43bc-bef2-463f1fde9aff",
                        "co_leader_id": "",
                        "roster": [
                            {
                                "id": "f8580374-5c09-43bc-bef2-463f1fde9aff",
                                "nickname": "sinnopsyy",
                                "avatar": "https://distribution.faceit-cdn.net/images/62a8416a-7cba-44b9-bab6-c5430f992eb9.jpeg",
                                "game_id": "76561198165327895",
                                "game_name": "sinnopsy=D",
                                "game_skill_level": 10,
                                "membership": "",
                                "anticheat_required": True,
                            },
                            {
                                "id": "440c0bf9-028a-4234-932c-3cb53e285851",
                                "nickname": "katNine",
                                "avatar": "https://distribution.faceit-cdn.net/images/c44d20cc-b2aa-4129-a9d4-5bbeb382d42e.jpeg",
                                "game_id": "76561198025532625",
                                "game_name": "k",
                                "game_skill_level": 10,
                                "membership": "",
                                "anticheat_required": True,
                            },
                            {
                                "id": "1b4e291a-c1c9-48c1-8738-5fda9a109151",
                                "nickname": "Coopah-iwnl-",
                                "avatar": "https://assets.faceit-cdn.net/avatars/1b4e291a-c1c9-48c1-8738-5fda9a109151_1626554809867.jpg",
                                "game_id": "76561198137616643",
                                "game_name": "I only frag when im on drugs❤",
                                "game_skill_level": 10,
                                "membership": "",
                                "anticheat_required": True,
                            },
                            {
                                "id": "e284326a-04c2-41b2-8e1b-851e9b5f9761",
                                "nickname": "-ReGnZ-",
                                "avatar": "https://assets.faceit-cdn.net/avatars/e284326a-04c2-41b2-8e1b-851e9b5f9761_1550964104764.jpg",
                                "game_id": "76561198070260050",
                                "game_name": "ReGnZ",
                                "game_skill_level": 10,
                                "membership": "",
                                "anticheat_required": True,
                            },
                            {
                                "id": "0b21055e-a2a6-4a4e-a1b8-3691352ce8f5",
                                "nickname": "faqazy",
                                "avatar": "https://distribution.faceit-cdn.net/images/49e275b8-c2e7-419b-a0dc-389dc21d7166.jpeg",
                                "game_id": "76561198799957222",
                                "game_name": "᠌ ᠌ ᠌᠌ ᠌ ᠌ ᠌ ᠌",
                                "game_skill_level": 10,
                                "membership": "",
                                "anticheat_required": True,
                            },
                        ],
                        "substitutions": 0,
                        "substitutes": None,
                    },
                ],
                "created_at": "2022-01-10T19:46:45Z",
                "updated_at": "2022-01-10T20:29:35Z",
                "started_at": "2022-01-10T19:51:43Z",
                "finished_at": "2022-01-10T20:29:35Z",
            },
        }
        return MatchFinished(**finished)

    async def main():
        # im = Image.new(mode="RGBA", size=(960, 540), color="white")
        #
        # def func(im):
        #     dark_middle = Image.open("{TEMPLATE_PATH}/background_features/dark-middle2.png")
        #     im.paste(dark_middle, (0, 0), dark_middle)
        # im.show()
        mf = match_finished_()
        print(f"{mf = }")
        statistics = await faceit_client.match_stats(mf.payload.id)
        mf_imcol = MatchFinishedImCol(
            mf,
            statistics,
            NickEloStorage(players=[PlayerStorage(nickname="Test", elo=1)]),
        )
        images_list = await mf_imcol.collect_images()
        images_list[0].show()

    asyncio.run(main())
