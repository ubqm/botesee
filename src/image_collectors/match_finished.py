import asyncio
from asyncio import Task
from typing import Literal

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

from src.clients.faceit import faceit_client
from src.clients.models.faceit.match_stats import Player, Round
from src.discord_bot.models.embed import NickEloStorage
from src.image_collectors import TEMPLATE_PATH
from src.image_collectors.avatar_designer import AvatarDesigner
from src.utils.enums import ColorTuple, available_maps, subscribers
from src.web.models.events import MatchFinished


class MatchFinishedImCol:
    font_folder = "phagspa"
    font_file = "phagspab_0.ttf"
    font_file_mainscore = "phagspab_0.ttf"
    fonts: dict[str, FreeTypeFont] = {
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
    fade_for_top_pfp = Image.open(
        f"{TEMPLATE_PATH}/background_features/fade_for_top_pfp.png"
    )
    fade_for_bottom_pfp = Image.open(
        f"{TEMPLATE_PATH}/background_features/fade_for_bottom_pfp.png"
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

    async def collect_image(self) -> Image.Image:
        return await self._draw_image()

    async def _draw_image(self) -> Image.Image:
        canvas: Image.Image = await self._get_map_image(self.match_round)
        canvas = await self._draw_players(self.match_round, canvas)
        return canvas

    async def _get_map_image(self, round_: Round) -> Image.Image:
        canvas: Image.Image = await self._get_background(round_)
        canvas = await self._draw_win_features(round_, canvas)
        await self._draw_game_score(round_, canvas)
        return canvas

    async def _draw_players(self, round_: Round, canvas: Image.Image) -> Image.Image:
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
        canvas: Image.Image,
        player: Player,
        idx_team: int,
        idx_player: int,
    ) -> Image.Image:
        canvas = await self._draw_player_avatar(canvas, player, idx_team, idx_player)
        await self._draw_player_stats(player, canvas, idx_team, idx_player)
        return canvas

    @staticmethod
    def _get_color_for_stat(
        player: Player, stat: Literal["kad", "mvp", "adr", "kd"]
    ) -> ColorTuple:
        # TODO: refactor
        match stat:
            case "kd":
                match player.player_stats.kd_ratio:
                    case kd if kd >= 1.5:
                        return ColorTuple.GREEN
                    case kd if 0.6 <= kd < 0.8:
                        return ColorTuple.ORANGE
                    case kd if kd < 0.6:
                        return ColorTuple.RED
                    case _:
                        return ColorTuple.WHITE
            case "adr":
                match player.player_stats.adr:
                    case adr if adr >= 100:
                        return ColorTuple.GREEN
                    case adr if 50 <= adr < 60:
                        return ColorTuple.ORANGE
                    case adr if adr < 50:
                        return ColorTuple.RED
                    case _:
                        return ColorTuple.WHITE
            case _:
                return ColorTuple.WHITE

    def _draw_player_stat(
        self,
        stat: Literal["kad", "mvp", "adr", "kd"],
        player: Player,
        canvas: Image.Image,
        idx_team: int,
        idx_player: int,
    ) -> None:
        image_draw = ImageDraw.Draw(canvas)
        stat_dict = {
            "kad": f"{player.player_stats.kills}/"
            f"{player.player_stats.assists}/"
            f"{player.player_stats.deaths}",
            "mvp": f"MVP: {player.player_stats.mvps}",
            "adr": f"ADR: {player.player_stats.adr:.1f}",
            "kd": f"K/D: {player.player_stats.kd_ratio:.2f}",
        }
        text = stat_dict[stat]
        w = image_draw.textlength(
            text,
            font=self._get_font_for_stat(stat),
        )
        stat_pos_dict: dict[Literal["kad", "mvp", "adr", "kd"], tuple[int, int]] = {
            "kad": (130 + (162 - w) / 2 + idx_player * 162, 150 + 200 * idx_team),
            "mvp": (156 + idx_player * 162, 240 + 36 * idx_team),
            "adr": (156 + idx_player * 162, 220 + 76 * idx_team),
            "kd": (156 + idx_player * 162, 200 + 116 * idx_team),
        }
        stat_color = self._get_color_for_stat(player, stat)
        stat_font = self._get_font_for_stat(stat)
        image_draw.text(
            stat_pos_dict[stat],
            text,
            font=stat_font,
            fill=stat_color,
            stroke_width=1,
            stroke_fill="black",
        )

    def _get_font_for_stat(
        self, stat: Literal["kad", "mvp", "adr", "kd"]
    ) -> FreeTypeFont:
        return (
            self.fonts["player_score"] if stat == "kad" else self.fonts["player_stats"]
        )

    async def _draw_player_stats(
        self, player: Player, canvas: Image.Image, idx_team: int, idx_player: int
    ) -> None:
        kad: Literal["kad"] = "kad"
        mvp: Literal["mvp"] = "mvp"
        adr: Literal["adr"] = "adr"
        kd: Literal["kd"] = "kd"
        for stat in (kad, mvp, adr, kd):
            self._draw_player_stat(stat, player, canvas, idx_team, idx_player)

    async def _draw_player_avatar(
        self,
        canvas: Image.Image,
        player: Player,
        idx_team: int,
        idx_player: int,
    ) -> Image.Image:
        player_elo = await faceit_client.get_player_elo_by_player_id(
            player.player_id, self.match.payload.game
        )
        elo_diff = await self.calculate_elo_change(player, player_elo)
        req_player = self.match.payload.teams[idx_team].get_player_by_nickname(
            player.nickname
        )

        avatar_designer = AvatarDesigner(req_player, player_elo, elo_diff)
        image_avatar = await avatar_designer.get_avatar(req_player, idx_team)

        if player.player_id in subscribers:
            fade_image = self.fade_for_bottom_pfp if idx_team else self.fade_for_top_pfp
            fade_pos = (
                (146 + idx_player * 162, 390 - self.fade_for_bottom_pfp.height)
                if idx_team
                else (146 + idx_player * 162, 150)
            )
            canvas.paste(fade_image, fade_pos, fade_image)

        canvas.paste(image_avatar, (146 + idx_player * 162, 20 + 370 * idx_team))
        return canvas

    async def calculate_elo_change(self, player: Player, player_elo: int) -> str:
        elo_change = (
            player_elo - self.prev_nick_elo[player.nickname].elo
            if self.prev_nick_elo
            else 0
        )

        match elo_change:
            case elo_change if elo_change > 0:
                return f"(+{elo_change})"
            case elo_change if elo_change < 0:
                return f"({elo_change})"
            case _:
                return ""

    async def _draw_game_score(self, round_: Round, canvas: Image.Image) -> None:
        await self._draw_final_score(round_, canvas)
        await self._draw_halftime_score(round_, canvas)

    async def _draw_halftime_score(self, round_: Round, canvas: Image.Image) -> None:
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

    async def _draw_final_score(self, round_: Round, canvas: Image.Image) -> None:
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

    async def _draw_win_features(
        self, round_: Round, canvas: Image.Image
    ) -> Image.Image:
        top_image, bot_image = await self._get_win_feature_images(round_)
        dark_middle = Image.open(
            f"{TEMPLATE_PATH}/background_features/dark-middle2.png"
        )
        canvas.paste(top_image, (0, 0), top_image)
        canvas.paste(bot_image, (0, 0), bot_image)
        canvas.paste(dark_middle, (0, 0), dark_middle)
        return canvas

    async def _get_win_feature_images(
        self, match_round: Round
    ) -> tuple[Image.Image, Image.Image]:
        """Return green and red background features(First team is on top)"""
        first_team_win_values = "Win", "Lose"
        second_team_win_values = "Lose", "Win"

        actual_values = (
            first_team_win_values
            if match_round.teams[0].team_stats.team_win
            else second_team_win_values
        )
        image_topcolor = Image.open(
            f"{TEMPLATE_PATH}/background_features/{actual_values[0]}-topleft.png"
        )
        image_botcolor = Image.open(
            f"{TEMPLATE_PATH}/background_features/{actual_values[1]}-botleft.png"
        )
        return image_topcolor, image_botcolor

    async def _get_background(self, round_: Round) -> Image.Image:
        if round_.round_stats.map not in available_maps.values:
            image_map = Image.open(f"{TEMPLATE_PATH}/maps/cs2_undefined_map.jpg")
            image_map = image_map.resize((960, 540))
            return image_map

        image_map = Image.open(f"{TEMPLATE_PATH}/maps/cs2_{round_.round_stats.map}.jpg")
        image_map = image_map.resize((960, 540))
        return image_map
