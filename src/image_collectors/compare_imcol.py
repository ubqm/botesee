import asyncio
from io import BytesIO
from typing import Any, Literal

from aiohttp import ClientSession
from aiohttp_client_cache import CachedSession
from loguru import logger
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

from src import redis_cache
from src.clients.faceit import faceit_client
from src.clients.models.faceit.match_stats import Round
from src.clients.models.faceit.player_details import PlayerDetails
from src.clients.models.faceit.player_history import MatchHistory
from src.db.repositories.match import match_repo
from src.image_collectors import TEMPLATE_PATH
from src.image_collectors._exceptions import BadAPICallException
from src.image_collectors.models.last_stat import (
    FullPlayerStat,
    GameStatLast,
    GameStatLastStorage,
)
from src.utils.enums import ColorTuple, available_maps


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
        self.compared_nicknames: tuple[str, str] = (self.nickname1, self.nickname2)
        self.output_type: str = self.validate_output_type(output_type)
        self.amount: int = self.validate_amount(amount)
        self.image: Image = Image.new("RGBA", size=(960, 540))
        self.dark_bg: Image = Image.new("RGB", size=(960, 540), color="black")
        self.dark_middle: Image = Image.open(
            f"{TEMPLATE_PATH}/background_features/dark-middle-compare.png"
        )
        self.font: FreeTypeFont = ImageFont.truetype(
            f"{TEMPLATE_PATH}/fonts/Outfit/Outfit-Bold.ttf", 26
        )
        self.font_name: FreeTypeFont = ImageFont.truetype(
            f"{TEMPLATE_PATH}/fonts/Outfit/Outfit-Bold.ttf", 36
        )

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
        async with CachedSession(cache=redis_cache) as session:
            try:
                player1_stats, player2_stats = await asyncio.gather(
                    self.collect_stat(session, self.nickname1),
                    self.collect_stat(session, self.nickname2),
                )
            except BadAPICallException as e:
                logger.warning(e)
            else:
                if player1_stats and player2_stats:
                    self.draw_image(player1_stats, player2_stats)
                    return self.image

    async def _collect_user_info(self, session: ClientSession, nickname: str) -> None:
        player_details = await faceit_client.player_details(nickname)
        player_history = await faceit_client.player_history(
            player_details.player_id, offset=0, limit=self.amount
        )
        player_region_stats = await faceit_client.region_stats(
            player_id=player_details.player_id,
            region=player_details.games.cs2.region,
        )
        player_country_stats = await faceit_client.region_stats(
            player_id=player_details.player_id,
            region=player_details.games.cs2.region,
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

    async def _set_avatar(
        self, session: ClientSession, player_details: PlayerDetails
    ) -> Image:
        if player_details.avatar:
            async with session.get(player_details.avatar) as response:
                image_avatar = Image.open(BytesIO(await response.read()))
                image_avatar = image_avatar.convert("RGB")
                image_avatar = image_avatar.resize((130, 130))
        else:
            image_avatar = Image.open(f"{TEMPLATE_PATH}/question-mark-icon.jpg")
            image_avatar = image_avatar.resize((130, 130))
        return image_avatar

    async def _set_background(
        self, session: ClientSession, player_details: PlayerDetails
    ) -> Image:
        if player_details.cover_image:
            async with session.get(player_details.cover_image) as response:
                background = Image.open(BytesIO(await response.read()))
        else:
            background = Image.new(mode="RGBA", size=(960, 540), color="black")
        return background

    async def collect_stat(
        self, session: ClientSession, nickname: str
    ) -> GameStatLastStorage:
        games: list[GameStatLast] = []
        await self._collect_user_info(session, nickname)

        match_ids = [match_history.match_id for match_history in self.player_stat[nickname].player_history.items]
        results = await match_repo.get_stats(match_ids=match_ids)

        for idx, match_stats in enumerate(results):
            if not match_stats:
                continue
            for match_round in match_stats.rounds[::-1]:
                if game := self.compile_game(
                    match_round,
                    self.player_stat[nickname].player_history.items[idx],
                    nickname,
                ):
                    games.append(game)
        return GameStatLastStorage(games=games)

    def compile_game(
        self, match_round: Round, match_h: MatchHistory, nickname: str
    ) -> GameStatLast | None:
        player_stats = match_round.get_player_stats(
            self.player_stat[nickname].player_details.player_id
        )

        # if player wasn't in the match (leaver)
        if not player_stats:
            return None

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
    ) -> tuple[ColorTuple, ColorTuple]:
        white = ColorTuple.WHITE
        green = ColorTuple.GREEN
        red = ColorTuple.RED

        values_dict = {
            "1f": {
                0: {"1.4": (green, red), "1.2": (green, white), "1": (white, white)},
                1: {"1.4": (red, green), "1.2": (white, green), "1": (white, white)},
            },
            "2f": {
                0: {"1.4": (green, red), "1.2": (green, white), "1": (white, white)},
                1: {"1.4": (red, green), "1.2": (white, green), "1": (white, white)},
            },
            "%": {
                0: {"1.4": (green, red), "1.2": (green, white), "1": (white, white)},
                1: {"1.4": (red, green), "1.2": (white, green), "1": (white, white)},
            },
            "reverse": {
                0: {"1.4": (red, green), "1.2": (green, white), "1": (white, white)},
                1: {"1.4": (green, red), "1.2": (white, green), "1": (white, white)},
            },
            "total": {
                0: {"1.4": (white, white), "1.2": (white, white), "1": (white, white)},
                1: {"1.4": (white, white), "1.2": (white, white), "1": (white, white)},
            },
        }

        if not isinstance(value, tuple) or len(value) != 2:
            return (white, white)
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
        w = canvas.textlength(left_line, font=self.font)
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

    def get_player_background(
        self, nickname: str, output_width: int = 480, output_height: int = 540
    ) -> Image:
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
        w = canvas.textlength("ELO", font=self.font)
        canvas.text(((960 - w) / 2, 220), "ELO", font=self.font)
        w = canvas.textlength("avgK", font=self.font)
        canvas.text(((960 - w) / 2, 250), "avgK", font=self.font)
        w = canvas.textlength("avgD", font=self.font)
        canvas.text(((960 - w) / 2, 280), "avgD", font=self.font)
        w = canvas.textlength("K/D", font=self.font)
        canvas.text(((960 - w) / 2, 310), "K/D", font=self.font)
        w = canvas.textlength("K/R", font=self.font)
        canvas.text(((960 - w) / 2, 340), "K/R", font=self.font)
        w = canvas.textlength("HS", font=self.font)
        canvas.text(((960 - w) / 2, 370), "HS", font=self.font)
        w = canvas.textlength("W/L", font=self.font)
        canvas.text(((960 - w) / 2, 400), "W/L", font=self.font)
        w = canvas.textlength("4K", font=self.font)
        canvas.text(((960 - w) / 2, 430), "4K", font=self.font)
        w = canvas.textlength("5K", font=self.font)
        canvas.text(((960 - w) / 2, 460), "5K", font=self.font)
        w = canvas.textlength("MVP", font=self.font)
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
            w = canvas.textlength(
                self.player_stat[nickname].player_details.nickname, font=self.font_name
            )
            pos = (810 - w, 20) if idx else (160, 20)
            canvas.text(
                pos,
                self.player_stat[nickname].player_details.nickname,
                font=self.font_name,
            )

    def _draw_region_stats(self, canvas: ImageDraw) -> None:
        for idx, nickname in enumerate(self.compared_nicknames):
            region_str = (
                f"{self.player_stat[nickname].player_details.games.cs2.region}: "
                f"{self.player_stat[nickname].player_region_stats.position:,}".replace(
                    ",", "."
                )
            )
            w = canvas.textlength(region_str, font=self.font)
            canvas.text(
                (160, 70) if idx == 0 else (810 - w, 70), region_str, font=self.font
            )

            country_str = (
                f"{self.player_stat[nickname].player_details.country}: "
                f"{self.player_stat[nickname].player_country_stats.position:,}".replace(
                    ",", "."
                )
            )
            w = canvas.textlength(country_str, font=self.font)
            canvas.text(
                (160, 100) if idx == 0 else (810 - w, 100), country_str, font=self.font
            )

    def _draw_compare_period(self, canvas: ImageDraw) -> None:
        w = canvas.textlength(f"{self.amount} {self.output_type}", font=self.font)
        canvas.text(
            ((960 - w) / 2, 100), f"{self.amount} {self.output_type}", font=self.font
        )

    def _draw_compare_stats(
        self,
        canvas: ImageDraw,
        player1_stats: GameStatLastStorage,
        player2_stats: GameStatLastStorage,
    ) -> None:
        ds: dict[str, dict[str, Any]] = {
            "elo": {
                "value": (
                    self.player_stat[
                        self.nickname1
                    ].player_details.games.cs2.faceit_elo,
                    self.player_stat[
                        self.nickname2
                    ].player_details.games.cs2.faceit_elo,
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
                "format": "{value:.1f}",
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
                "format": "{value:.1f}%",
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
            color_left, color_right = self.compare_stats(
                ds[stat_str]["value"], ds[stat_str]["type"]
            )
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

        for idx, available_map in enumerate(available_maps.values):
            p1_won, p1_lost, p1_percentage = player1_stats.map_stats(
                available_map, self.amount
            )
            left_line = f"{p1_won} - {p1_lost} | {p1_percentage}%"
            p2_won, p2_lost, p2_percentage = player2_stats.map_stats(
                available_map, self.amount
            )
            right_line = f"{p2_won} - {p2_lost} | {p2_percentage}%"

            p1_color = p2_color = ColorTuple.WHITE
            if (p1_won or p1_lost) and (p2_won or p2_lost):
                p1_color, p2_color = self.compare_stats(
                    (p1_percentage, p2_percentage), "%"
                )

            canvas.text(
                (left_stat_x, map_h * idx + map_y_start + 10),
                left_line,
                font=self.font,
                fill=p1_color,
            )
            w = canvas.textlength(right_line, font=self.font)
            canvas.text(
                (right_stat_x - w, map_h * idx + map_y_start + 10),
                right_line,
                font=self.font,
                fill=p2_color,
            )

            current_map = Image.open(f"{TEMPLATE_PATH}/maps/cs2_{available_map}.jpg")
            current_map = current_map.resize((map_w, map_h))
            self.image.paste(current_map, (10, map_h * idx + map_y_start))
            self.image.paste(current_map, (860, map_h * idx + map_y_start))

    def draw_image(
        self, player1_stats: GameStatLastStorage, player2_stats: GameStatLastStorage
    ) -> None:
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
        imgcmp = CompareImCol("-NAPAD", "T1A-", amount=10)
        img = await imgcmp.collect_image()
        img.show()

    asyncio.run(main())
