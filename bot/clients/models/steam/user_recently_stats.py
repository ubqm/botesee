from pydantic import BaseModel


class GameStat(BaseModel):
    appid: int
    name: str | None
    playtime_2weeks: int
    playtime_forever: int
    img_icon_url: str | None
    playtime_windows_forever: int | None
    playtime_mac_forever: int | None
    playtime_linux_forever: int | None


class RecentStatistics(BaseModel):
    total_count: int | None
    games: list[GameStat] | None

    def __getitem__(self, appid: int) -> GameStat | None:
        if not self.games:
            return None
        for stat in self.games:
            if stat.appid == appid:
                return stat
        return None


class RecentStatisticsResponse(BaseModel):
    response: RecentStatistics | None

    def get_csgo(self) -> GameStat | None:
        if not self.response:
            return None
        if not self.response.games:
            return None
        return self.response[730]
