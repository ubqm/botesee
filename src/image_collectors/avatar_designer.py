from io import BytesIO

from aiohttp_client_cache import CachedSession
from PIL import Image, ImageDraw, ImageFont

from src import redis_cache
from src.image_collectors import TEMPLATE_PATH
from src.web.models.base import Player


class AvatarDesigner:
    font_folder = "jetbrains_mono"
    font_file = "JetBrainsMono-ExtraBold.ttf"
    image_dark_avatar_bot = Image.open(
        f"{TEMPLATE_PATH}/background_features/for_avatar_bot.png"
    )
    image_dark_avatar_top = Image.open(
        f"{TEMPLATE_PATH}/background_features/for_avatar_top.png"
    )
    font = ImageFont.truetype(f"{TEMPLATE_PATH}/fonts/{font_folder}/{font_file}", 18)

    def __init__(self, player: Player, player_elo: int, elo_diff: str):
        self.player = player
        self.player_elo = player_elo
        self.elo_diff = elo_diff

    async def get_avatar(self, player: Player, idx_team: int) -> Image.Image:
        image_avatar = await self._download_player_avatar(player)
        self._apply_background_features(image_avatar)
        self._apply_faceit_level_icon(image_avatar, player, idx_team)
        self._write_nickname(image_avatar, player, idx_team)
        return image_avatar

    @staticmethod
    async def _download_player_avatar(req_player: Player) -> Image.Image:
        avatar_size = (130, 130)
        unknown_avatar = Image.open(f"{TEMPLATE_PATH}/question-mark-icon.jpg")
        unknown_avatar = unknown_avatar.resize(avatar_size)
        if not req_player.avatar:
            return unknown_avatar

        async with CachedSession(cache=redis_cache) as session:
            response = await session.get(req_player.avatar)

        if response.status != 200:
            return unknown_avatar

        try:
            actual_avatar = Image.open(BytesIO(await response.read()))
        except Exception:
            return unknown_avatar

        actual_avatar = actual_avatar.convert("RGB")
        actual_avatar = actual_avatar.resize(avatar_size)
        return actual_avatar

    def _apply_background_features(self, image_avatar: Image.Image) -> None:
        image_avatar.paste(
            self.image_dark_avatar_top, (0, 0), self.image_dark_avatar_top
        )
        image_avatar.paste(
            self.image_dark_avatar_bot, (0, 0), self.image_dark_avatar_bot
        )

    def _write_nickname(
        self, image_avatar: Image.Image, player: Player, idx_team: int
    ) -> None:
        draw_image_avatar = ImageDraw.Draw(image_avatar)
        w = draw_image_avatar.textlength(player.nickname, font=self.font)

        nickname_text_height = 107 - idx_team * 107
        nickname_text_width = 0 if w > 130 else (130 - w) / 2
        nickname_text_pos = (nickname_text_width, nickname_text_height)

        draw_image_avatar.text(nickname_text_pos, player.nickname, font=self.font)

    def _apply_faceit_level_icon(
        self, image_avatar: Image.Image, player: Player, idx_team: int
    ) -> None:
        draw_image_avatar = ImageDraw.Draw(image_avatar)

        faceit_lvl = player.game_skill_level
        faceit_lvl_icon = Image.open(
            f"{TEMPLATE_PATH}/faceit_icons/faceit{faceit_lvl}.png"
        ).convert("RGBA")
        faceit_lvl_icon_pos = (0, 0 + 106 * idx_team)
        image_avatar.paste(faceit_lvl_icon, faceit_lvl_icon_pos, faceit_lvl_icon)

        w = draw_image_avatar.textlength(self.elo_diff, font=self.font)
        elo_diff_text_pos = (127 - w, 0 + 107 * idx_team)
        draw_image_avatar.text(elo_diff_text_pos, self.elo_diff, font=self.font)

        player_elo_text_pos = (26, 0 + 107 * idx_team)
        draw_image_avatar.text(
            player_elo_text_pos, str(self.player_elo), font=self.font
        )
