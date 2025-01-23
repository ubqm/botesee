import asyncio
from io import BytesIO

import pytz
from aiohttp import ClientSession
from aiohttp_client_cache import CachedSession
from loguru import logger
from PIL import Image, ImageDraw, ImageFont

from src import redis_cache
from src.clients.faceit import faceit_client
from src.clients.models.faceit.match_stats import Round
from src.clients.models.faceit.player_history import MatchHistory
from src.clients.steam import steam_client
from src.db.repositories.elo import elo_repo
from src.db.repositories.match import match_repo
from src.image_collectors import TEMPLATE_PATH
from src.image_collectors.models.last_stat import (
    FullPlayerStat,
    GameStatLast,
    GameStatLastStorage,
    SteamStatLast,
)
from src.utils.enums import ColorTuple, available_maps


class LastStatsImCol:
    font = ImageFont.truetype(f"{TEMPLATE_PATH}/fonts/Outfit/Outfit-Bold.ttf", 26)
    font_name = ImageFont.truetype(f"{TEMPLATE_PATH}/fonts/Outfit/Outfit-Bold.ttf", 36)
    lose_bg = Image.open(f"{TEMPLATE_PATH}/background_features/right-side-lose.png")
    win_bg = Image.open(f"{TEMPLATE_PATH}/background_features/right-side-win.png")
    bg_dark_right = Image.open(
        f"{TEMPLATE_PATH}/background_features/dark-right-side-for-stat.png"
    )

    def __init__(self, nickname: str, use_faceit_api: bool = False):
        self.nickname: str = nickname
        self.use_faceit_api: bool = use_faceit_api
        self.player_stat: dict[str, FullPlayerStat] = {}
        self.avatar: Image = Image.new(mode="RGBA", size=(130, 130), color="black")
        self.image: Image = Image.new(mode="RGBA", size=(960, 540), color="black")

    async def collect_image(self) -> Image:
        games = await self.collect_stat()
        if not games:
            raise ValueError("No recent games found in DB")
        await self._draw_image(games)
        return self.image

    async def collect_stat(self) -> GameStatLastStorage:
        games: list[GameStatLast] = []
        await self._collect_user_info()

        match_ids = [
            match_history.match_id
            for match_history in self.player_stat[self.nickname].player_history.items
        ]
        if self.use_faceit_api:
            results = await asyncio.gather(
                *[faceit_client.match_stats(match_id) for match_id in match_ids]
            )
        else:
            results = await match_repo.get_stats(match_ids=match_ids)

        for idx, match_stats in enumerate(results):
            if not match_stats:
                continue
            for match_round in match_stats.rounds:
                game = await self.compile_game(
                    match_round,
                    self.player_stat[self.nickname].player_history.items[idx],
                )
                if not game:
                    continue
                games.append(game)

                if len(games) >= 10:
                    return GameStatLastStorage(games=games)

        return GameStatLastStorage(games=games)

    async def _draw_image(self, games_storage: GameStatLastStorage) -> None:
        draw_image_bg = ImageDraw.Draw(self.image)
        draw_image_bg.text(
            (160, 20),
            self.player_stat[self.nickname].player_details.nickname,
            font=self.font_name,
        )

        self._draw_avatar()
        self._draw_steam_stats(draw_image_bg)
        self._draw_faceit_elo(draw_image_bg)
        self._draw_region_stats(draw_image_bg)
        self._draw_player_last_10_stats(draw_image_bg, games_storage)

        for idx, game in enumerate(games_storage.games):
            self._draw_game(draw_image_bg, game, idx)
            if idx == 10:
                break

    async def compile_game(
        self, match_round: Round, match_h: MatchHistory
    ) -> GameStatLast | None:
        player_stats = match_round.get_player_stats(
            self.player_stat[self.nickname].player_details.player_id
        )
        if not player_stats:
            return None

        # logic to sort values for particular player in depends on winning/losing
        map_score: str = match_round.round_stats.score
        end_score_numbers: list[int] = [int(el.strip()) for el in map_score.split("/")]
        sorted_score: str = (
            f"{max(end_score_numbers)} / {min(end_score_numbers)}"
            if player_stats.result
            else f"{min(end_score_numbers)} / {max(end_score_numbers)}"
        )

        enemy_players = match_round.get_enemy_players(
            self.player_stat[self.nickname].player_details.player_id
        )
        enemy_players_uuids = [player.player_id for player in enemy_players]
        match_avg_elo = await elo_repo.get_avg_elo(
            match_round.match_id, enemy_players_uuids
        )

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
            map_score=sorted_score,
            map_name=match_round.round_stats.map,
            started_at=match_h.started_at,
            match_avg_elo=match_avg_elo,
        )

    async def _collect_user_info(self):
        player_details = await faceit_client.player_details(self.nickname)

        (
            player_history,
            player_region_stats,
            player_country_stats,
            steam_app_stat,
            steam_recently_stat,
        ) = await asyncio.gather(
            faceit_client.player_history(player_details.player_id),
            faceit_client.region_stats(
                player_id=player_details.player_id,
                region=player_details.games.cs2.region,
            ),
            faceit_client.region_stats(
                player_id=player_details.player_id,
                region=player_details.games.cs2.region,
                country=player_details.country,
            ),
            steam_client.user_app_stat(
                player_details.steam_id_64 or player_details.games.cs2.game_player_id,
            ),
            steam_client.user_rec_played_stat(
                player_details.steam_id_64 or player_details.games.cs2.game_player_id,
            ),
        )

        logger.info(f"{steam_app_stat=}")
        logger.info(f"{steam_recently_stat=}")
        self.player_stat[self.nickname] = FullPlayerStat(
            player_details=player_details,
            player_history=player_history,
            player_region_stats=player_region_stats,
            player_country_stats=player_country_stats,
            steam_app_stat=steam_app_stat if steam_app_stat.playerstats else None,
            steam_recently_stat=steam_recently_stat,
        )
        async with CachedSession(cache=redis_cache) as session:
            await self._set_avatar(session)
            await self._set_background(session)

    async def _set_avatar(self, session: ClientSession) -> None:
        if self.player_stat[self.nickname].player_details.avatar:
            async with session.get(
                self.player_stat[self.nickname].player_details.avatar
            ) as response:
                if response.status == 200:
                    self.image_avatar = Image.open(BytesIO(await response.read()))
                else:
                    self.image_avatar = Image.new("RGB", size=(130, 130), color="black")
            self.image_avatar = self.image_avatar.convert("RGB")
            self.image_avatar = self.image_avatar.resize((130, 130))
        else:
            self.image_avatar = Image.open(f"{TEMPLATE_PATH}/question-mark-icon.jpg")
            self.image_avatar = self.image_avatar.resize((130, 130))

    async def _set_background(self, session: ClientSession) -> None:
        if self.player_stat[self.nickname].player_details.cover_image:
            async with session.get(
                self.player_stat[self.nickname].player_details.cover_image
            ) as response:
                if response.status == 200:
                    self.image = Image.open(BytesIO(await response.read()))
                else:
                    self.image_avatar = Image.new("RGB", size=(960, 540), color="black")
        else:
            self.image = Image.new(mode="RGBA", size=(960, 540), color="black")
        self._resize_background()
        self.image.paste(self.bg_dark_right, (0, 0), self.bg_dark_right)

    def _resize_background(self) -> None:
        width, height = self.image.size
        if height != 540:
            aspect_ratio = 540 / height
            self.image = self.image.resize((int(width * aspect_ratio), 540))
        width, height = self.image.size
        if width >= 960:
            left = int((width - 960) / 2)
            top = 0
            right = int((width - 960) / 2 + 960)
            bottom = height
            self.image = self.image.crop((left, top, right, bottom))
            self.image.resize((960, 540))

    def _get_steam_stats_text(self) -> SteamStatLast:
        if not self.player_stat[self.nickname].steam_recently_stat:
            raise Exception(
                f"Steam recent stats not found for "
                f"{self.nickname} {self.player_stat[self.nickname]}"
            )
        cs2_stats = self.player_stat[self.nickname].steam_recently_stat.get_cs()
        logger.info(f"{cs2_stats=}")
        playtime_2weeks = "Last 2 weeks: Unknown"
        playtime_forever = "Summary in CS2: Unknown"
        percentage_played = "Activity: Unknown"
        cs2_time_played_hrs = "Played in CS2: Unknown"
        if cs2_stats:
            cs2_playtime_hours = cs2_stats.playtime_forever / 60
            playtime_2weeks = f"Last 2 weeks: {int(cs2_stats.playtime_2weeks / 60)} hrs"
            playtime_forever = f"Summary in CS2: {int(cs2_playtime_hours)} hrs"

            logger.info(f"{self.player_stat[self.nickname].steam_app_stat=}")
            if self.player_stat[self.nickname].steam_app_stat:
                cs2_playtime = (
                    self.player_stat[self.nickname]
                    .steam_app_stat.playerstats.stats[2]
                    .value
                    / 60
                    / 60
                )
                cs2_time_played_hrs = f"Played in CS2: {int(cs2_playtime)} hrs"
                percentage_played = (
                    f"Activity: {cs2_playtime / cs2_playtime_hours * 100:.1f}%"
                )
            else:
                cs2_time_played_hrs = "Played in CS2: Unknown"
                percentage_played = "Activity: Unknown"
        return SteamStatLast(
            playtime_2weeks=playtime_2weeks,
            playtime_forever=playtime_forever,
            percentage_played=percentage_played,
            cs2_time_played_hrs=cs2_time_played_hrs,
        )

    def _draw_steam_stats(self, canvas: ImageDraw.ImageDraw) -> None:
        steam_stats = self._get_steam_stats_text()
        logger.info(f"{steam_stats=}")
        canvas.text(
            (10, 150),
            steam_stats.playtime_2weeks,
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        canvas.text(
            (10, 180),
            steam_stats.cs2_time_played_hrs,
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        canvas.text(
            (10, 210),
            steam_stats.playtime_forever,
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        canvas.text(
            (10, 240),
            steam_stats.percentage_played,
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )

    def _draw_region_stats(self, canvas: ImageDraw) -> None:
        canvas.text(
            (270, 70),
            f"{self.player_stat[self.nickname].player_details.games.cs2.region}: "
            f"{self.player_stat[self.nickname].player_region_stats.position:,}".replace(
                ",", "."
            ),
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        canvas.text(
            (270, 100),
            f"{self.player_stat[self.nickname].player_details.country}: "
            f"{self.player_stat[self.nickname].player_country_stats.position:,}".replace(
                ",", "."
            ),
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )

    def _draw_faceit_elo(self, canvas: ImageDraw) -> None:
        faceit_lvl = self.player_stat[
            self.nickname
        ].player_details.games.cs2.skill_level
        image_lvl = Image.open(
            f"{TEMPLATE_PATH}/faceit_icons/faceit{faceit_lvl}.png"
        ).convert("RGBA")
        image_lvl = image_lvl.resize((24, 24))
        self.image.paste(image_lvl, (155, 74), image_lvl)
        canvas.text(
            (184, 70),
            str(self.player_stat[self.nickname].player_details.games.cs2.faceit_elo),
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )

    @staticmethod
    def _get_player_game_stat_color(kd_ratio: float) -> ColorTuple:
        if kd_ratio >= 1.3:
            return ColorTuple.GREEN
        elif kd_ratio < 0.6:
            return ColorTuple.RED
        elif 0.8 > kd_ratio >= 0.6:
            return ColorTuple.ORANGE
        else:
            return ColorTuple.WHITE

    def _draw_game_kd(
        self, canvas: ImageDraw, game: GameStatLast, idx_game: int
    ) -> None:
        stat_color = self._get_player_game_stat_color(game.kd_ratio)
        kad = f"{game.kills}/{game.assists}/{game.deaths}"
        canvas.text(
            (665, 50 * idx_game + 30),
            kad,
            font=self.font,
            fill=stat_color,
            stroke_width=1,
            stroke_fill="black",
        )

    def _draw_game_time(
        self, canvas: ImageDraw, game: GameStatLast, idx_game: int
    ) -> None:
        minsk_time = game.started_at.astimezone(pytz.timezone("Europe/Minsk"))
        game_date = minsk_time.strftime("%d %b")
        game_time = minsk_time.strftime("%H:%M")
        w = canvas.textlength(game_time, font=self.font)
        canvas.text(
            (488, 50 * idx_game + 30),
            game_date,
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        canvas.text(
            (648 - w, 50 * idx_game + 30),
            game_time,
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )

    def _draw_avg_elo(
        self, canvas: ImageDraw, game: GameStatLast, idx_game: int
    ) -> None:
        avg_elo_text: str = f"{game.match_avg_elo / 1000:.1f}k"
        w = canvas.textlength(avg_elo_text, font=self.font)
        canvas.text(
            (478 - w, 50 * idx_game + 30),
            avg_elo_text,
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )

    def _draw_game_background(self, game: GameStatLast, idx_game: int) -> None:
        if game.result:
            self.image.paste(self.win_bg, (775, 50 * idx_game + 24), self.win_bg)
        else:
            self.image.paste(self.lose_bg, (775, 50 * idx_game + 24), self.lose_bg)

    def _draw_game_map(
        self, canvas: ImageDraw, game: GameStatLast, idx_game: int
    ) -> None:
        canvas.text(
            (870, 50 * idx_game + 30),
            game.map_score,
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        if game.map_name in available_maps.values:
            current_map = Image.open(f"{TEMPLATE_PATH}/maps/cs2_{game.map_name}.jpg")
        else:
            current_map = Image.new(mode="RGBA", size=(90, 50), color="black")

        current_map = current_map.resize((90, 50))
        self.image.paste(current_map, (770, 50 * idx_game + 24))

    def _draw_player_last_10_stats(
        self, canvas: ImageDraw, games: GameStatLastStorage
    ) -> None:
        canvas.text(
            (10, 310),
            "Last 10 games played:",
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        kad = (
            f"KAD: {games.mean_kills():.1f} / {games.mean_assists():.1f}"
            f" / {games.mean_deaths():.1f}"
        )
        canvas.text((10, 340), kad, font=self.font, stroke_width=1, stroke_fill="black")
        canvas.text(
            (10, 370),
            f"K/D: {games.mean_kd():.2f}",
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        canvas.text(
            (10, 400),
            f"K/R: {games.mean_kr():.2f}",
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        canvas.text(
            (10, 430),
            f"Total 4K: {games.total_quadro()}",
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        canvas.text(
            (10, 460),
            f"Total 5K: {games.total_ace()}",
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )
        canvas.text(
            (10, 490),
            f"HS: {games.mean_hs():.1f}%",
            font=self.font,
            stroke_width=1,
            stroke_fill="black",
        )

    def _draw_game(self, canvas: ImageDraw, game: GameStatLast, idx_game: int) -> None:
        self._draw_game_background(game, idx_game)
        self._draw_game_map(canvas, game, idx_game)
        self._draw_game_kd(canvas, game, idx_game)
        self._draw_game_time(canvas, game, idx_game)
        if not self.use_faceit_api:
            self._draw_avg_elo(canvas, game, idx_game)

    def _draw_avatar(self):
        self.image.paste(self.image_avatar, (10, 10))


if __name__ == "__main__":

    async def main():
        # player_details = await faceit_client.player_details("Ayudesee")

        # print(steam_app_stat)
        last_imcol = LastStatsImCol("-NAPAD")
        imgs = await last_imcol.collect_image()
        imgs.show()

    asyncio.run(main())
