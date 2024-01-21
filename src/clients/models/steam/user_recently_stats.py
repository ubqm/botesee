from pydantic import BaseModel


class GameStat(BaseModel):
    appid: int
    name: str | None = None
    playtime_2weeks: int
    playtime_forever: int
    img_icon_url: str | None = None
    playtime_windows_forever: int | None = None
    playtime_mac_forever: int | None = None
    playtime_linux_forever: int | None = None


class RecentStatistics(BaseModel):
    total_count: int | None = None
    games: list[GameStat] | None = None

    def __getitem__(self, appid: int) -> GameStat | None:
        if not self.games:
            return None
        for stat in self.games:
            if stat.appid == appid:
                return stat
        return None


class RecentStatisticsResponse(BaseModel):
    response: RecentStatistics | None = None

    def get_cs(self) -> GameStat | None:
        if not self.response:
            return None
        if not self.response.games:
            return None
        return self.response[730]
