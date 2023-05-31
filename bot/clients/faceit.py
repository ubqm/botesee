import asyncio
from uuid import UUID

import aiohttp
from aiohttp import ClientSession

from bot import conf
from bot.clients.models.faceit.match_details import MatchDetails
from bot.clients.models.faceit.match_stats import MatchStatistics
from bot.clients.models.faceit.player_details import PlayerDetails
from bot.clients.models.faceit.player_history import PlayerHistory
from bot.clients.models.faceit.region_stats import RegionStatistics


class FaceitClient:
    base_url = "https://open.faceit.com/data/v4"

    @classmethod
    async def player_details(cls, session: ClientSession, nickname: str) -> PlayerDetails | None:
        api_url = f"{cls.base_url}/players?nickname={nickname}"
        async with session.get(api_url) as response:
            if response.status != 200:
                return None
            res = await response.json()
            return PlayerDetails(**res)

    @classmethod
    async def get_player_elo_by_nickname(cls, session: ClientSession, nickname: str) -> int:
        details = await cls.player_details(session, nickname)
        return details.games.csgo.faceit_elo if details else 0

    @classmethod
    async def player_details_by_id(cls, session, player_id: UUID | str) -> PlayerDetails | None:
        player_id = str(player_id)
        api_url = f"{cls.base_url}/players/{player_id}"
        async with session.get(api_url) as response:
            if response.status != 200:
                return None
            res = await response.json()
            return PlayerDetails(**res)

    @classmethod
    async def player_history(
        cls,
        session: ClientSession,
        player_id: UUID | str,
        game: str = "csgo",
        offset: int = 0,
        limit: int = 20,
    ) -> PlayerHistory | None:
        player_id = str(player_id)
        api_url = f"{cls.base_url}/players/{player_id}/history?game={game}&offset={offset}&limit={limit}"
        async with session.get(api_url) as response:
            if response.status != 200:
                return None
            res = await response.json()
            return PlayerHistory(**res)

    @classmethod
    async def match_details(cls, session: ClientSession, match_id: str) -> MatchDetails | None:
        api_url = f"{cls.base_url}/matches/{match_id}"
        async with session.get(api_url) as response:
            if response.status != 200:
                return None
            res = await response.json()
            return MatchDetails(**res)

    @classmethod
    async def match_stats(cls, session: ClientSession, match_id: str) -> MatchStatistics | None:
        api_url = f"{cls.base_url}/matches/{match_id}/stats"
        async with session.get(api_url) as response:
            if response.status != 200:
                return None
            res = await response.json()
            return MatchStatistics(**res)

    @classmethod
    async def region_stats(
        cls,
        session: ClientSession,
        player_id: UUID | str,
        region: str,
        country: str | None = None,
    ) -> RegionStatistics | None:
        player_id = str(player_id)
        api_url = f"{cls.base_url}/rankings/games/csgo/regions/{region}/players/{player_id}?limit=2"
        if country:
            api_url += f"&country={country}"
        async with session.get(api_url) as response:
            if response.status != 200:
                return None
            res = await response.json()
            return RegionStatistics(**res)


if __name__ == "__main__":

    async def main():
        async with aiohttp.ClientSession(headers=conf.FACEIT_HEADERS) as session:
            # res = await FaceitClient.match_stats(session, "1-c900d437-eff7-4536-9a32-f01c5cf7580c")
            # res = await FaceitClient.player_details_by_id(session, UUID("ad42c90b-45a9-49b6-8ab0-9c8662330543"))
            # res = await FaceitClient.player_details(session, "-NAPAD")
            # res = await FaceitClient.player_history(session, UUID("ad42c90b-45a9-49b6-8ab0-9c8662330543"), limit=2)
            # res = await FaceitClient.match_details(session, "1-f0ad4c71-7fce-432b-8ca0-5261d85be686")
            res = await FaceitClient.region_stats(session, UUID("278790a2-1f08-4350-bd96-427f7dcc8722"), region="EU")
            print(f"{res = }")

    asyncio.run(main())
