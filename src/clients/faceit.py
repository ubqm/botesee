import asyncio
import logging
from uuid import UUID

import httpx
from httpx import USE_CLIENT_DEFAULT, URL
from httpx._client import UseClientDefault
from loguru import logger

from src import conf
from src.clients.models.faceit.match_details import MatchDetails
from src.clients.models.faceit.match_stats import MatchStatistics
from src.clients.models.faceit.player_details import PlayerDetails
from src.clients.models.faceit.player_history import PlayerHistory
from src.clients.models.faceit.player_stats import PlayerGameStats
from src.clients.models.faceit.player_stats_collection import PlayerStatsCollection
from src.clients.models.faceit.region_stats import RegionStatistics


class FaceitClient(httpx.AsyncClient):
    def __init__(self, api_key: str):
        headers = {"Authorization": f"Bearer {api_key}", "accept": "application/json"}
        transport = httpx.AsyncHTTPTransport(retries=4)
        super().__init__(
            headers=headers,
            transport=transport,
            base_url="https://open.faceit.com/data/v4/",
        )

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
                logger.info(f"Retrying {url} for {i} time. {e}")
                await asyncio.sleep(0.5 * 2**i)
            else:
                return response.json()
        raise httpx.ReadTimeout(
            f"Unable to read data from {url}. I tried {retry_attempts} times..."
        )

    async def player_details(self, nickname: str) -> PlayerDetails:
        path = "players"
        res = await self._request("GET", url=path, params={"nickname": nickname})
        return PlayerDetails(**res)

    async def get_player_elo_by_player_id(
        self, player_id: str | UUID, game: str = "cs2"
    ) -> int:
        details = await self.player_details_by_id(player_id)
        if not details:
            return 0

        match game:
            case "csgo":
                return details.games.csgo.faceit_elo
            case "cs2":
                return details.games.cs2.faceit_elo if details.games.cs2 else 0
            case _:
                return 0

    async def get_player_elo_by_nickname(self, nickname: str, game: str = "cs2") -> int:
        details = await self.player_details(nickname)
        if not details:
            return 0

        match game:
            case "csgo":
                return details.games.csgo.faceit_elo
            case "cs2":
                return details.games.cs2.faceit_elo if details.games.cs2 else 0
            case _:
                return 0

    async def player_details_by_id(self, player_id: UUID | str) -> PlayerDetails:
        path = f"players/{str(player_id)}"
        res = await self._request("GET", url=path)
        return PlayerDetails(**res)

    async def player_history(
        self,
        player_id: UUID | str,
        game: str = "cs2",
        offset: int = 0,
        limit: int = 20,
    ) -> PlayerHistory:
        api_url = f"players/{str(player_id)}/history"
        res = await self._request(
            "GET", api_url, params={"game": game, "offset": offset, "limit": limit}
        )
        return PlayerHistory(**res)

    async def player_stats(
        self, player_id: UUID | str, game_id: str = "cs2"
    ) -> PlayerGameStats:
        api_url = f"players/{str(player_id)}/stats/{game_id}"
        res = await self._request("GET", api_url)
        return PlayerGameStats(**res)

    async def player_stats_collection(
        self,
        player_id: UUID | str,
        game_id: str = "cs2",
        page_size: int = 10,
        page: int = 1,
    ) -> PlayerStatsCollection:
        api_url = f"players/{player_id}/games/{game_id}/stats"
        res = await self._request(
            "GET", url=api_url, params={"size": page_size, "page": page}
        )
        return PlayerStatsCollection(**res)

    async def match_details(self, match_id: str) -> MatchDetails:
        api_url = f"matches/{match_id}"
        res = await self._request("GET", api_url)
        return MatchDetails(**res)

    async def match_stats(self, match_id: str) -> MatchStatistics:
        api_url = f"matches/{match_id}/stats"
        res = await self._request("GET", api_url, timeout=(1.0, 3.0, 5.0, 9.0))
        return MatchStatistics(**res)

    async def region_stats(
        self,
        player_id: UUID | str,
        region: str,
        country: str | None = None,
        game: str = "cs2",
    ) -> RegionStatistics:
        player_id = str(player_id)
        api_url = f"rankings/games/{game}/regions/{region}/players/{player_id}"
        params = {"limit": 2}
        if country:
            params["country"] = country
        res = await self._request("GET", api_url, params=params)
        return RegionStatistics(**res)


faceit_client = FaceitClient(conf.FACEIT_TOKEN)

httpx_logger = logging.getLogger("httpx")
httpx_logger.disabled = True
httpx_logger.propagate = False


if __name__ == "__main__":

    async def main():
        res = await faceit_client.player_details("Fr1ze")
        # res = await faceit_client.player_history(
        #     UUID("278790a2-1f08-4350-bd96-427f7dcc8722")
        # )
        print(res)

    asyncio.run(main())
