import asyncio
from asyncio import Task
from io import BytesIO
from typing import Any, Literal

import aiohttp
from aiohttp import ClientSession
from PIL import Image, ImageDraw, ImageFont

from bot import conf
from bot.clients.faceit import FaceitClient
from bot.clients.models.faceit.match_stats import MatchStatistics, Round
from bot.clients.models.faceit.player_details import PlayerDetails
from bot.clients.models.faceit.player_history import MatchHistory
from bot.image_collectors import TEMPLATE_PATH
from bot.image_collectors.models.last_stat import (
    FullPlayerStat,
    GameStatLast,
    GameStatLastStorage,
)
from bot.utils.enums import ColorTuple, available_maps, colors


class CompareImCol:
    def __init__(
        self,
        nickname1: str,
        nickname2: str,
        amount: int | str = 50,
        output_type: str = "games",
    ):
        self.player_stat: dict[str, FullPlayerStat] = {}
        self.nickname1: str = nickname1
        self.nickname2: str = nickname2
        self.compared_nicknames = (self.nickname1, self.nickname2)
        self.output_type: str = self.validate_output_type(output_type)
        self.amount: int = self.validate_amount(amount)
        self.image = Image.new("RGBA", size=(960, 540))
        self.dark_bg = Image.new("RGB", size=(960, 540), color="black")
        self.dark_middle = Image.open(f"{TEMPLATE_PATH}/background_features/dark-middle-compare.png")
        self.font = ImageFont.truetype(f"{TEMPLATE_PATH}/fonts/Outfit/Outfit-Bold.ttf", 26)
        self.font_name = ImageFont.truetype(f"{TEMPLATE_PATH}/fonts/Outfit/Outfit-Bold.ttf", 36)

    @staticmethod
    def validate_output_type(output_type: str) -> str:
        if output_type in [
            "game",
            "games",
            "month",
            "months",
            "week",
            "weeks",
            "days",
            "day",
        ]:
            return output_type
        else:
            return "games"

    def validate_amount(self, amount: int | str) -> int:
        if self.output_type in ["game", "games"]:
            if isinstance(amount, int):
                return amount
            return int(amount) if amount.isdigit() and 5 <= int(amount) <= 100 else 20
        return 20

    async def collect_image(self) -> Image:
        async with aiohttp.ClientSession(headers=conf.FACEIT_HEADERS) as session:
            player1_stats, player2_stats = await asyncio.gather(
                self.collect_stat(session, self.nickname1),
                self.collect_stat(session, self.nickname2),
            )

            if player1_stats and player2_stats:
                self.draw_image(player1_stats, player2_stats)
                return self.image

    async def _collect_user_info(self, session: ClientSession, nickname: str) -> None:
        player_details = await FaceitClient.player_details(session, nickname)
        player_history = await FaceitClient.player_history(
            session, player_details.player_id, offset=0, limit=self.amount
        )
        player_region_stats = await FaceitClient.region_stats(
            session=session,
            player_id=player_details.player_id,
            region=player_details.games.csgo.region,
        )
        player_country_stats = await FaceitClient.region_stats(
            session=session,
            player_id=player_details.player_id,
            region=player_details.games.csgo.region,
            country=player_details.country,
        )
        avatar = await self._set_avatar(session, player_details)
        background = await self._set_background(session, player_details)

        self.player_stat[nickname] = FullPlayerStat(
            player_details=player_details,
            player_history=player_history,
            player_region_stats=player_region_stats,
            player_country_stats=player_country_stats,
            avatar=avatar,
            background=background,
        )

    async def _set_avatar(self, session: ClientSession, player_details: PlayerDetails) -> Image:
        if player_details.avatar:
            async with session.get(player_details.avatar) as response:
                image_avatar = Image.open(BytesIO(await response.read()))
                image_avatar = image_avatar.convert("RGB")
                image_avatar = image_avatar.resize((130, 130))
        else:
            image_avatar = Image.open(f"{TEMPLATE_PATH}/question-mark-icon.jpg")
            image_avatar = image_avatar.resize((130, 130))
        return image_avatar

    async def _set_background(self, session: ClientSession, player_details: PlayerDetails) -> Image:
        if player_details.cover_image:
            async with session.get(player_details.cover_image) as response:
                background = Image.open(BytesIO(await response.read()))
        else:
            background = Image.new(mode="RGBA", size=(960, 540), color="black")
        return background

    async def collect_stat(self, session: ClientSession, nickname: str) -> GameStatLastStorage:
        games: list[GameStatLast] = []
        await self._collect_user_info(session, nickname)
        tasks: list[Task] = []
        for match_history in self.player_stat[nickname].player_history.items:
            task2 = asyncio.create_task(FaceitClient.match_stats(session, match_history.match_id))
            tasks.append(task2)
        results: list[MatchStatistics] = await asyncio.gather(*tasks)
        for idx, match_stats in enumerate(results):
            if not match_stats:
                continue
            for match_round in match_stats.rounds[::-1]:
                game = self.compile_game(
                    match_round,
                    self.player_stat[nickname].player_history.items[idx],
                    nickname,
                )
                games.append(game)
        return GameStatLastStorage(games=games)

    def compile_game(self, match_round: Round, match_h: MatchHistory, nickname: str) -> GameStatLast:
        player_stats = match_round.get_player_stats(self.player_stat[nickname].player_details.player_id)
        return GameStatLast(
            result=player_stats.result,
            kills=player_stats.kills,
            assists=player_stats.assists,
            deaths=player_stats.deaths,
            kd_ratio=player_stats.kd_ratio,
            kr_ratio=player_stats.kr_ratio,
            mvps=player_stats.mvps,
            headshots_p=player_stats.headshots_p,
            quadro=player_stats.quadro,
            ace=player_stats.ace,
            map_score=match_round.round_stats.score,
            map_name=match_round.round_stats.map,
            started_at=match_h.started_at,
        )

    @staticmethod
    def compare_stats(
        value: tuple, category: Literal["1f", "2f", "%", "reverse", "total"]
    ) -> list[ColorTuple, ColorTuple]:
        white = colors.WHITE
        green = colors.GREEN
        red = colors.RED

        values_dict = {
            "1f": {
                0: {"1.4": [green, red], "1.2": [green, white], "1": [white, white]},
                1: {"1.4": [red, green], "1.2": [white, green], "1": [white, white]},
            },
            "2f": {
                0: {"1.4": [green, red], "1.2": [green, white], "1": [white, white]},
                1: {"1.4": [red, green], "1.2": [white, green], "1": [white, white]},
            },
            "%": {
                0: {"1.4": [green, red], "1.2": [green, white], "1": [white, white]},
                1: {"1.4": [red, green], "1.2": [white, green], "1": [white, white]},
            },
            "reverse": {
                0: {"1.4": [red, green], "1.2": [green, white], "1": [white, white]},
                1: {"1.4": [green, red], "1.2": [white, green], "1": [white, white]},
            },
            "total": {
                0: {"1.4": [white, white], "1.2": [white, white], "1": [white, white]},
                1: {"1.4": [white, white], "1.2": [white, white], "1": [white, white]},
            },
        }

        if not isinstance(value, tuple) or len(value) != 2:
            return [white, white]
        if value[0] == value[1] == 0:
            return values_dict[category][value.index(max(value))]["1"]
        rating = (max(value) / min(value)) if min(value) != 0 else 100
        if rating >= 1.4:
            rating_s = "1.4"
        elif rating >= 1.2:
            rating_s = "1.2"
        else:
            rating_s = "1"
        return values_dict[category][value.index(max(value))][rating_s]

    def _draw_stat(
        self,
        canvas: ImageDraw,
        left_line: str,
        right_line: str,
        color_left: ColorTuple,
        color_right: ColorTuple,
        idx: int,
    ) -> None:
        left_stat_x = 410
        right_stat_x = 550
        start_y = 220
        step = 30
        w, h = canvas.textsize(left_line, font=self.font)
        canvas.text(
            (left_stat_x - w, start_y + step * idx),
            left_line,
            font=self.font,
            fill=color_left,
        )
        canvas.text(
            (right_stat_x, start_y + step * idx),
            right_line,
            font=self.font,
            fill=color_right,
        )

    def get_player_background(self, nickname: str, output_width: int = 480, output_height: int = 540) -> Image:
        background = self.player_stat[nickname].background
        width, height = self.player_stat[nickname].background.size
        if height != output_height:
            aspect_ratio = output_height / height
            background = background.resize((int(width * aspect_ratio), output_height))
        width, height = background.size
        if width >= output_width:
            left = int((width - output_width) / 2)
            top = 0
            right = int((width - output_width) / 2 + output_width)
            bottom = height
            background = background.crop((left, top, right, bottom))
            background.resize((output_width, output_height))
        return background

    def _draw_mid_text(self, canvas: ImageDraw) -> None:
        w, h = canvas.textsize("ELO", font=self.font)
        canvas.text(((960 - w) / 2, 220), "ELO", font=self.font)
        w, h = canvas.textsize("avgK", font=self.font)
        canvas.text(((960 - w) / 2, 250), "avgK", font=self.font)
        w, h = canvas.textsize("avgD", font=self.font)
        canvas.text(((960 - w) / 2, 280), "avgD", font=self.font)
        w, h = canvas.textsize("K/D", font=self.font)
        canvas.text(((960 - w) / 2, 310), "K/D", font=self.font)
        w, h = canvas.textsize("K/R", font=self.font)
        canvas.text(((960 - w) / 2, 340), "K/R", font=self.font)
        w, h = canvas.textsize("HS", font=self.font)
        canvas.text(((960 - w) / 2, 370), "HS", font=self.font)
        w, h = canvas.textsize("W/L", font=self.font)
        canvas.text(((960 - w) / 2, 400), "W/L", font=self.font)
        w, h = canvas.textsize("4K", font=self.font)
        canvas.text(((960 - w) / 2, 430), "4K", font=self.font)
        w, h = canvas.textsize("5K", font=self.font)
        canvas.text(((960 - w) / 2, 460), "5K", font=self.font)
        w, h = canvas.textsize("MVP", font=self.font)
        canvas.text(((960 - w) / 2, 490), "MVP", font=self.font)

    def _draw_background(self) -> None:
        for idx, nickname in enumerate(self.compared_nicknames):
            background = self.get_player_background(nickname, 480, 540)
            self.image.paste(background, (480 * idx, 0))
        self.image.paste(self.dark_middle, (0, 0), self.dark_middle)

    def _draw_avatars(self) -> None:
        for idx, nickname in enumerate(self.compared_nicknames):
            pos = (820, 10) if idx else (10, 10)
            self.image.paste(self.player_stat[nickname].avatar, pos)

    def _draw_nicknames(self, canvas: ImageDraw) -> None:
        for idx, nickname in enumerate(self.compared_nicknames):
            w, h = canvas.textsize(self.player_stat[nickname].player_details.nickname, font=self.font_name)
            pos = (810 - w, 20) if idx else (160, 20)
            canvas.text(
                pos,
                self.player_stat[nickname].player_details.nickname,
                font=self.font_name,
            )

    def _draw_region_stats(self, canvas: ImageDraw) -> None:
        for idx, nickname in enumerate(self.compared_nicknames):
            region_str = (
                f"{self.player_stat[nickname].player_details.games.csgo.region}: "
                f"{self.player_stat[nickname].player_region_stats.position}"
            )
            w, h = canvas.textsize(region_str, font=self.font)
            canvas.text((160, 70) if idx == 0 else (810 - w, 70), region_str, font=self.font)

            country_str = (
                f"{self.player_stat[nickname].player_details.country}: "
                f"{self.player_stat[nickname].player_country_stats.position}"
            )
            w, h = canvas.textsize(country_str, font=self.font)
            canvas.text((160, 100) if idx == 0 else (810 - w, 100), country_str, font=self.font)

    def _draw_compare_period(self, canvas: ImageDraw) -> None:
        w, h = canvas.textsize(f"{self.amount} {self.output_type}", font=self.font)
        canvas.text(((960 - w) / 2, 100), f"{self.amount} {self.output_type}", font=self.font)

    def _draw_compare_stats(
        self,
        canvas: ImageDraw,
        player1_stats: GameStatLastStorage,
        player2_stats: GameStatLastStorage,
    ) -> None:
        ds: dict[str, dict[str, Any]] = {
            "elo": {
                "value": (
                    self.player_stat[self.nickname1].player_details.games.csgo.faceit_elo,
                    self.player_stat[self.nickname2].player_details.games.csgo.faceit_elo,
                ),
                "type": "total",
                "format": "{value}",
            },
            "kills": {
                "value": (
                    player1_stats.mean_kills(self.amount),
                    player2_stats.mean_kills(self.amount),
                ),
                "type": "1f",
                "format": "{value:.1f}",
            },
            "deaths": {
                "value": (
                    player1_stats.mean_deaths(self.amount),
                    player2_stats.mean_deaths(self.amount),
                ),
                "type": "reverse",
                "format": "{value}",
            },
            "kd": {
                "value": (
                    player1_stats.mean_kd(self.amount),
                    player2_stats.mean_kd(self.amount),
                ),
                "type": "2f",
                "format": "{value:.2f}",
            },
            "kr": {
                "value": (
                    player1_stats.mean_kr(self.amount),
                    player2_stats.mean_kr(self.amount),
                ),
                "type": "2f",
                "format": "{value:.2f}",
            },
            "hs": {
                "value": (
                    player1_stats.mean_hs(self.amount),
                    player2_stats.mean_hs(self.amount),
                ),
                "type": "%",
                "format": "{value}%",
            },
            "winrate": {
                "value": (
                    player1_stats.total_winrate(self.amount),
                    player2_stats.total_winrate(self.amount),
                ),
                "type": "%",
                "format": "{value}%",
            },
            "quadro": {
                "value": (
                    player1_stats.total_quadro(self.amount),
                    player2_stats.total_quadro(self.amount),
                ),
                "type": "total",
                "format": "{value}",
            },
            "ace": {
                "value": (
                    player1_stats.total_ace(self.amount),
                    player2_stats.total_ace(self.amount),
                ),
                "type": "total",
                "format": "{value}",
            },
            "mvp": {
                "value": (
                    player1_stats.mean_mvp(self.amount),
                    player2_stats.mean_mvp(self.amount),
                ),
                "type": "1f",
                "format": "{value:.1f}",
            },
        }
        for idx, stat_str in enumerate(ds):
            left_line = ds[stat_str]["format"].format(value=ds[stat_str]["value"][0])
            right_line = ds[stat_str]["format"].format(value=ds[stat_str]["value"][1])
            color_left, color_right = self.compare_stats(ds[stat_str]["value"], ds[stat_str]["type"])
            self._draw_stat(canvas, left_line, right_line, color_left, color_right, idx)

    def _draw_map_stats(
        self,
        canvas: ImageDraw,
        player1_stats: GameStatLastStorage,
        player2_stats: GameStatLastStorage,
    ) -> None:
        map_w, map_h = 90, 50
        map_y_start = 140
        left_stat_x = 110
        right_stat_x = 850

        for idx, available_map in enumerate(available_maps):
            won, lost, percentage = player1_stats.map_stats(available_map)
            left_line = f"{won} - {lost} | {percentage}%"
            won, lost, percentage = player2_stats.map_stats(available_map)
            right_line = f"{won} - {lost} | {percentage}%"

            canvas.text((left_stat_x, map_h * idx + map_y_start + 10), left_line, font=self.font)
            w, h = canvas.textsize(right_line, font=self.font)
            canvas.text(
                (right_stat_x - w, map_h * idx + map_y_start + 10),
                right_line,
                font=self.font,
            )

            current_map = Image.open(f"{TEMPLATE_PATH}/maps/{available_map}.jpg")
            current_map = current_map.resize((map_w, map_h))
            self.image.paste(current_map, (10, map_h * idx + map_y_start))
            self.image.paste(current_map, (860, map_h * idx + map_y_start))

    def draw_image(self, player1_stats: GameStatLastStorage, player2_stats: GameStatLastStorage) -> None:
        canvas = ImageDraw.Draw(self.image)
        self._draw_background()
        self._draw_avatars()
        self._draw_nicknames(canvas)
        self._draw_mid_text(canvas)
        self._draw_region_stats(canvas)
        self._draw_compare_period(canvas)
        self._draw_map_stats(canvas, player1_stats, player2_stats)
        self._draw_compare_stats(canvas, player1_stats, player2_stats)


if __name__ == "__main__":

    async def main():
        imgcmp = CompareImCol("-MORZY", "Ayudesee", amount=10)
        img = await imgcmp.collect_image()
        img.show()

    asyncio.run(main())
