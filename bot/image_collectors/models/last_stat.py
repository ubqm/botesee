from datetime import datetime

from PIL.Image import Image
from pydantic import BaseModel

from bot.clients.models.faceit.player_details import PlayerDetails
from bot.clients.models.faceit.player_history import PlayerHistory
from bot.clients.models.faceit.region_stats import RegionStatistics
from bot.clients.models.steam.user_app_stats import UserAppStatistics
from bot.clients.models.steam.user_recently_stats import RecentStatisticsResponse


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


class GameStatLastStorage(BaseModel):
    games: list[GameStatLast]

    def __iter__(self):
        return iter(self.games)

    def map_stats(self, search_map: str, game_num: int = 10) -> tuple[int, int, float]:
        """Returns total wins, total loss and win percentage on a map in a last amount of games"""
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
        percentage = int((total_wins / (total_wins + total_loss)) * 100) if (total_wins + total_loss) else 0
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
        total_kd = 0
        total_games = 0
        for game in self.games:
            total_kd += game.kd_ratio

            total_games += 1
            if total_games == game_num:
                break
        return total_kd / total_games

    def mean_kr(self, game_num: int = 10) -> float:
        total_kr = 0
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
    csgo_time_played_hrs: str


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
    player_history: PlayerHistory | None = None
    player_region_stats: RegionStatistics | None = None
    player_country_stats: RegionStatistics | None = None
    steam_app_stat: UserAppStatistics | None = None
    steam_recently_stat: RecentStatisticsResponse | None = None
    avatar: Image | None = None
    background: Image | None = None

    class Config:
        arbitrary_types_allowed = True
