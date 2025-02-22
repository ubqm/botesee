from decimal import Decimal
from io import BytesIO

from aiohttp_client_cache import CachedSession
from PIL import ImageFont
from PIL.Image import Image
from PIL.Image import new as PILImage
from PIL.Image import open as image_open
from PIL.ImageDraw import Draw
from PIL.ImageEnhance import Brightness

from src import redis_cache
from src.db.repositories.statistics import WeeklyStats
from src.image_collectors import TEMPLATE_PATH


class WeeklyStatsDesigner:
    font_folder = "phagspa"
    font_file = "phagspab_0.ttf"
    font = ImageFont.truetype(f"{TEMPLATE_PATH}/fonts/{font_folder}/{font_file}", 18)

    def __init__(self, stats: list[WeeklyStats]):
        self.stats = stats
        self.image = PILImage("RGB", size=(960, 540), color="black")

    async def collect_image(self) -> Image:
        await self._set_background()
        await self._set_header_text()
        await self._set_players_text()
        return self.image

    async def _set_background(self) -> None:
        self.image = image_open(
            f"{TEMPLATE_PATH}/background_features/background_weekly.jpg"
        ).convert("RGB")
        self.image = self.image.resize((960, 540))

        column_shadow = image_open(
            f"{TEMPLATE_PATH}/background_features/gradient_table_shadow.png"
        )
        self.image.paste(column_shadow, (160, 0), column_shadow)
        self.image.paste(column_shadow, (400, 0), column_shadow)
        self.image.paste(column_shadow, (620, 0), column_shadow)
        self.image.paste(column_shadow, (850, 0), column_shadow)

        im = Draw(self.image)
        for idx in range(8):
            im.line(
                ((0, 120 + 60 * idx), (960, 120 + 60 * idx)),
                fill=(100, 100, 100),
                width=2,
            )

    async def _set_header_text(self) -> None:
        im = Draw(self.image)
        w = im.textlength("ELO", font=self.font)
        im.text(
            (215 - w / 2, 28),
            "ELO",
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        w = im.textlength("K/D", font=self.font)
        im.text(
            (335 - w / 2, 28),
            "K/D",
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        w = im.textlength("ADR", font=self.font)
        im.text(
            (455 - w / 2, 28),
            "ADR",
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        w = im.textlength("HS %", font=self.font)
        im.text(
            (565 - w / 2, 28),
            "HS %",
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        w = im.textlength("1v1 %", font=self.font)
        im.text(
            (675 - w / 2, 28),
            "1v1 %",
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        w = im.textlength("Entry %", font=self.font)
        im.text(
            (790 - w / 2, 28),
            "Entry %",
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        w = im.textlength("Matches", font=self.font)
        im.text(
            (905 - w / 2, 28),
            "Matches",
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )

    async def _set_players_text(self) -> None:
        for idx, player_stat in enumerate(self.stats):
            await self._set_player_background(idx, player_stat)
            await self._set_player_stats(idx, player_stat)

    async def _set_player_stats(self, idx: int, player_stat: WeeklyStats) -> None:
        im = Draw(self.image)
        im.text(
            (10, 80 + idx * 60),
            player_stat.nickname,
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )

        elo_text = self._get_stat_text(player_stat.elo_current, player_stat.elo_prev)
        w = im.textlength(elo_text, font=self.font)
        im.text(
            (215 - w / 2, 80 + idx * 60),
            elo_text,
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )

        kd_ratio_text = self._get_stat_text(
            player_stat.get_kd_ratio("latest"), player_stat.get_kd_ratio("prev")
        )
        w = im.textlength(kd_ratio_text, font=self.font)
        im.text(
            (335 - w / 2, 80 + idx * 60),
            kd_ratio_text,
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )

        adr_text = self._get_stat_text(
            player_stat.get_adr("latest"), player_stat.get_adr("prev")
        )
        w = im.textlength(adr_text, font=self.font)
        im.text(
            (455 - w / 2, 80 + idx * 60),
            adr_text,
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )

        headshots_p_text = self._get_stat_text(
            player_stat.get_headshots_p("latest"), player_stat.get_headshots_p("prev")
        )
        w = im.textlength(headshots_p_text, font=self.font)
        im.text(
            (565 - w / 2, 80 + idx * 60),
            headshots_p_text,
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )

        clutches_p_text = self._get_stat_text(
            player_stat.get_clutches_p("latest"), player_stat.get_clutches_p("prev")
        )
        w = im.textlength(clutches_p_text, font=self.font)
        im.text(
            (675 - w / 2, 80 + idx * 60),
            clutches_p_text,
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )

        entry_p_text = self._get_stat_text(
            player_stat.get_entry_p("latest"), player_stat.get_entry_p("prev")
        )
        w = im.textlength(entry_p_text, font=self.font)
        im.text(
            (790 - w / 2, 80 + idx * 60),
            entry_p_text,
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )

        matches_played_text = self._get_stat_text(
            player_stat.get_amount_matches("latest"),
            player_stat.get_amount_matches("prev"),
        )
        w = im.textlength(matches_played_text, font=self.font)
        im.text(
            (905 - w / 2, 80 + idx * 60),
            matches_played_text,
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )

    async def _set_player_background(self, idx: int, player_stat: WeeklyStats) -> None:
        if not player_stat.cover_image:
            return

        async with CachedSession(cache=redis_cache) as session:
            response = await session.get(player_stat.cover_image)

        if response.status != 200:
            return

        cover_image = image_open(BytesIO(await response.read()))
        cover_image = cover_image.convert("RGB").resize((160, 60))
        enhancer = Brightness(cover_image)
        cover_image = enhancer.enhance(0.5)
        self.image.paste(cover_image, (0, 60 + idx * 60))

    def _get_stat_text(
        self, latest_period_stat: Decimal | int, prev_period_stat: Decimal | int | None
    ) -> str:
        if prev_period_stat is None:
            return f"{latest_period_stat}"

        delta_stat = latest_period_stat - prev_period_stat
        if delta_stat == 0:
            return f"{latest_period_stat}"
        elif delta_stat < 0:
            return f"{latest_period_stat}({delta_stat})"
        else:
            return f"{latest_period_stat}(+{delta_stat})"
