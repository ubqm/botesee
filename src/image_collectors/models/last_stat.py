from datetime import datetime

from PIL import Image
from PIL.Image import Image as ImageClass
from pydantic import BaseModel, ConfigDict, Field

from src.clients.models.faceit.player_details import PlayerDetails
from src.clients.models.faceit.player_history import PlayerHistory
from src.clients.models.faceit.region_stats import RegionStatistics
from src.clients.models.steam.user_app_stats import UserAppStatistics
from src.clients.models.steam.user_recently_stats import RecentStatisticsResponse


class GameStatLast(BaseModel):
    result: bool
    kills: int
    assists: int
    deaths: int
    kd_ratio: float
    kr_ratio: float
    mvps: int
    headshots_p: int
    quadro: int
    ace: int
    map_score: str
    map_name: str
    started_at: datetime
    match_avg_elo: int = 0
    adr: float = 0.0
    utility_dpr: float = 0.0
    flash_sr: float = 0.0


class GameStatLastStorage(BaseModel):
    games: list[GameStatLast] = Field(min_length=1)

    def __iter__(self):
        return iter(self.games)

    def map_stats(self, search_map: str, game_num: int = 10) -> tuple[int, int, float]:
        """Returns total wins, total loss and win percentage
        on a map in a last amount of games"""
        total_games = 0
        total_wins = 0
        total_loss = 0
        for game in self.games:
            if game.map_name == search_map:
                if game.result:
                    total_wins += 1
                else:
                    total_loss += 1
            total_games += 1
            if total_games == game_num:
                break
        percentage = (
            int((total_wins / (total_wins + total_loss)) * 100)
            if (total_wins + total_loss)
            else 0
        )
        return total_wins, total_loss, percentage

    def mean_kills(self, game_num: int = 10) -> float:
        total_kills = 0
        total_games = 0
        for game in self.games:
            total_kills += game.kills

            total_games += 1
            if total_games == game_num:
                break
        return total_kills / total_games

    def mean_assists(self, game_num: int = 10) -> float:
        total_assists = 0
        total_games = 0
        for game in self.games:
            total_assists += game.assists

            total_games += 1
            if total_games == game_num:
                break
        return total_assists / total_games

    def mean_deaths(self, game_num: int = 10) -> float:
        total_deaths = 0
        total_games = 0
        for game in self.games:
            total_deaths += game.deaths

            total_games += 1
            if total_games == game_num:
                break
        return total_deaths / total_games

    def mean_kd(self, game_num: int = 10) -> float:
        total_kd = 0.0
        total_games = 0
        for game in self.games:
            total_kd += game.kd_ratio

            total_games += 1
            if total_games == game_num:
                break
        return total_kd / total_games

    def mean_kr(self, game_num: int = 10) -> float:
        total_kr = 0.0
        total_games = 0
        for game in self.games:
            total_kr += game.kr_ratio

            total_games += 1
            if total_games == game_num:
                break
        return total_kr / total_games

    def mean_hs(self, game_num: int = 10) -> float:
        total_hs = 0
        total_games = 0
        for game in self.games:
            total_hs += game.headshots_p

            total_games += 1
            if total_games == game_num:
                break
        return total_hs / total_games

    def total_quadro(self, game_num: int = 10) -> int:
        total_quadro = 0
        total_games = 0
        for game in self.games:
            total_quadro += game.quadro

            total_games += 1
            if total_games == game_num:
                break
        return total_quadro

    def total_ace(self, game_num: int = 10) -> int:
        total_ace = 0
        total_games = 0
        for game in self.games:
            total_ace += game.ace

            total_games += 1
            if total_games == game_num:
                break
        return total_ace

    def mean_mvp(self, game_num: int = 10) -> float:
        total_mvp = 0
        total_games = 0
        for game in self.games:
            total_mvp += game.mvps

            total_games += 1
            if total_games == game_num:
                break
        return total_mvp / total_games

    def mean_adr(self, game_num: int = 10) -> float:
        games = self.games[:game_num]
        return sum(game.adr for game in games) / len(games)

    def mean_util_dpr(self, game_num: int = 10) -> float:
        games = self.games[:game_num]
        return sum(game.utility_dpr for game in games) / len(games)

    def mean_util_flash_sr(self, game_num: int = 10) -> float:
        games = self.games[:game_num]
        return sum(game.flash_sr for game in games) / len(games) * 100

    def total_winrate(self, game_num: int = 10) -> int:
        games_won = 0
        total_games = 0
        for game in self.games:
            games_won += game.result

            total_games += 1
            if total_games == game_num:
                break
        return int(games_won / total_games * 100)


class SteamStatLast(BaseModel):
    playtime_2weeks: str
    playtime_forever: str
    percentage_played: str
    cs2_time_played_hrs: str


class PlayerStatLast(BaseModel):
    mean_k: int = 0
    mean_a: int = 0
    mean_d: int = 0
    mean_kd: float = 0.0
    mean_kr: float = 0.0
    mean_hs: int = 0
    total_4k: int = 0
    total_5k: int = 0


class FullPlayerStat(BaseModel):
    player_details: PlayerDetails
    player_history: PlayerHistory
    player_region_stats: RegionStatistics
    player_country_stats: RegionStatistics
    steam_app_stat: UserAppStatistics | None = None
    steam_recently_stat: RecentStatisticsResponse | None = None
    avatar: ImageClass | None = None
    background: ImageClass = Image.new(mode="RGBA", size=(960, 540), color="black")

    model_config = ConfigDict(arbitrary_types_allowed=True)
