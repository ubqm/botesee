import asyncio
import json

import aiohttp
from aiohttp import ClientSession

from clients.models.steam.user_app_stats import UserAppStatistics
from clients.models.steam.user_recently_stats import RecentStatisticsResponse
from env_variables import steam_token


class SteamClient:
    base_url = "https://api.steampowered.com/"
    user_stats_url = base_url + f"ISteamUserStats/GetUserStatsForGame/v2/?key={steam_token}"
    player_service_url = base_url + f"IPlayerService/GetRecentlyPlayedGames/v0001/?key={steam_token}"

    @classmethod
    async def user_app_stat(cls, session: ClientSession, steamid: str, appid: int = 730) -> UserAppStatistics:
        api_url = f"{cls.user_stats_url}&steamid={steamid}&appid={appid}"
        async with session.get(api_url) as response:
            res = await response.json()
            return UserAppStatistics(**res)

    @classmethod
    async def user_rec_played_stat(cls, session: ClientSession, steamid: str) -> RecentStatisticsResponse:
        api_url = f"{cls.player_service_url}&steamid={steamid}&format=json"
        async with session.get(api_url) as response:
            res = await response.json()
            return RecentStatisticsResponse(**res)


if __name__ == '__main__':
    async def main():
        async with aiohttp.ClientSession() as session:
            # res = await SteamClient.user_app_stat(session, "76561198030140352")
            res = await SteamClient.user_rec_played_stat(session, "76561198164505719op")
            print(res)

    asyncio.run(main())
