from pydantic import BaseModel


class GameStat(BaseModel):
    appid: int
    name: str
    playtime_2weeks: int
    playtime_forever: int
    img_icon_url: str
    playtime_windows_forever: int
    playtime_mac_forever: int
    playtime_linux_forever: int


class RecentStatistics(BaseModel):
    total_count: int | None
    games: list[GameStat] | None


class RecentStatisticsResponse(BaseModel):
    response: RecentStatistics | None
