import asyncio

import httpx
from httpx import URL, AsyncClient, AsyncHTTPTransport
from httpx._client import USE_CLIENT_DEFAULT, UseClientDefault
from loguru import logger

from src import conf
from src.clients.models.steam.user_app_stats import UserAppStatistics
from src.clients.models.steam.user_recently_stats import RecentStatisticsResponse


class SteamClient(AsyncClient):
    def __init__(self, api_key: str):
        super().__init__(
            transport=AsyncHTTPTransport(retries=4),
            base_url="https://api.steampowered.com/",
        )
        self.api_key = api_key

    async def _request(
        self,
        method: str,
        url: str,
        params: dict | None = None,
        json: dict | None = None,
        timeout: tuple | UseClientDefault = USE_CLIENT_DEFAULT,
        retry_attempts: int = 5,
    ) -> dict:
        for i in range(retry_attempts):
            try:
                logger.info(f"{URL(url, params=params)}")
                response = await self.request(
                    method, url, params=params, json=json, timeout=timeout
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    logger.info(f"HTTP 403 for {e.response.url}")
                    return {}
                logger.info(f"Retrying {url} for {i} time. {e}")
                await asyncio.sleep(0.5 * 2**i)
            else:
                return response.json()
        raise httpx.ReadTimeout(
            f"Unable to read data from {url}. I tried {retry_attempts} times..."
        )

    async def user_app_stat(self, steamid: str, appid: int = 730) -> UserAppStatistics:
        url = "ISteamUserStats/GetUserStatsForGame/v2/"
        params = {
            "key": self.api_key,
            "steamid": steamid,
            "appid": appid,
        }
        res = await self._request("GET", url, params)
        return UserAppStatistics(**res)

    async def user_rec_played_stat(self, steamid: str) -> RecentStatisticsResponse:
        url = "IPlayerService/GetRecentlyPlayedGames/v0001/"
        params = {
            "key": self.api_key,
            "steamid": steamid,
            "format": "json",
        }
        res = await self._request("GET", url, params)
        return RecentStatisticsResponse(**res)


steam_client = SteamClient(conf.STEAM_TOKEN)


if __name__ == "__main__":

    async def main():
        # ubqm = "76561198030140352"
        napad = "76561198061461007"
        res = await steam_client.user_app_stat(napad)
        print(res)
        res = await steam_client.user_rec_played_stat(napad)
        print(res)

    asyncio.run(main())
