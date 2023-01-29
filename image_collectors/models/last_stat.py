from datetime import datetime

from pydantic import BaseModel


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

    def mean_kills(self, game_num: int = 10) -> float:
        total_kills = 0
        idx = 0
        for game in self.games:
            total_kills += game.kills

            idx += 1
            if idx == game_num:
                break
        return total_kills / idx

    def mean_assists(self, game_num: int = 10) -> float:
        total_assists = 0
        idx = 0
        for game in self.games:
            total_assists += game.assists

            idx += 1
            if idx == game_num:
                break
        return total_assists / idx

    def mean_deaths(self, game_num: int = 10) -> float:
        total_deaths = 0
        idx = 0
        for game in self.games:
            total_deaths += game.deaths

            idx += 1
            if idx == game_num:
                break
        return total_deaths / idx

    def mean_kd(self, game_num: int = 10) -> float:
        total_kd = 0
        idx = 0
        for game in self.games:
            total_kd += game.kd_ratio

            idx += 1
            if idx == game_num:
                break
        return total_kd / idx

    def mean_kr(self, game_num: int = 10) -> float:
        total_kr = 0
        idx = 0
        for game in self.games:
            total_kr += game.kr_ratio

            idx += 1
            if idx == game_num:
                break
        return total_kr / idx

    def mean_hs(self, game_num: int = 10) -> float:
        total_hs = 0
        idx = 0
        for game in self.games:
            total_hs += game.headshots_p

            idx += 1
            if idx == game_num:
                break
        return total_hs / idx

    def total_quadro(self, game_num: int = 10) -> int:
        total_quadro = 0
        idx = 0
        for game in self.games:
            total_quadro += game.quadro

            idx += 1
            if idx == game_num:
                break
        return total_quadro

    def total_ace(self, game_num: int = 10) -> int:
        total_ace = 0
        idx = 0
        for game in self.games:
            total_ace += game.ace

            idx += 1
            if idx == game_num:
                break
        return total_ace


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
