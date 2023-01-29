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

    def __getitem__(self, appid: int) -> GameStat | None:
        for stat in self.games:
            if stat.appid == appid:
                return stat


class RecentStatisticsResponse(BaseModel):
    response: RecentStatistics | None

    def get_csgo(self) -> GameStat | None:
        if not self.response:
            return None
        if not self.response.games:
            return None
        return self.response[730]
