import asyncio
from uuid import UUID

import aiohttp
from aiohttp import ClientSession
from loguru import logger

from bot import conf
from bot.clients.models.faceit.match_details import MatchDetails
from bot.clients.models.faceit.match_stats import MatchStatistics
from bot.clients.models.faceit.player_details import PlayerDetails
from bot.clients.models.faceit.player_history import PlayerHistory
from bot.clients.models.faceit.player_stats import PlayerGameStats
from bot.clients.models.faceit.player_stats_collection import PlayerStatsCollection
from bot.clients.models.faceit.region_stats import RegionStatistics
from bot.image_collectors._exceptions import BadAPICallException
from bot.utils.enums import subscribers


class FaceitClient:
    base_url = "https://open.faceit.com/data/v4"

    @classmethod
    async def player_details(cls, session: ClientSession, nickname: str) -> PlayerDetails:
        api_url = f"{cls.base_url}/players?nickname={nickname}"
        async with session.get(api_url) as response:
            if response.status != 200:
                logger.error(f"player_details APICall Error {response.status}: {response.content}")
                raise BadAPICallException(f"player_details with {response.status}: {response.content}")
            res = await response.json()
            return PlayerDetails(**res)

    @classmethod
    async def get_player_elo_by_nickname(cls, session: ClientSession, nickname: str, game: str = "cs2") -> int:
        details = await cls.player_details(session, nickname)
        if not details:
            return 0

        match game:
            case "csgo":
                return details.games.csgo.faceit_elo
            case "cs2":
                return details.games.cs2.faceit_elo if details.games.cs2 else 0
            case _:
                return 0

    @classmethod
    async def player_details_by_id(cls, session, player_id: UUID | str) -> PlayerDetails:
        player_id = str(player_id)
        api_url = f"{cls.base_url}/players/{player_id}"
        async with session.get(api_url) as response:
            if response.status != 200:
                logger.error(f"player_details_by_id APICall Error {response.status}: {response.content}")
                raise BadAPICallException(f"player_details_by_id with {response.status}: {response.content}")
            res = await response.json()
            return PlayerDetails(**res)

    @classmethod
    async def player_history(
        cls,
        session: ClientSession,
        player_id: UUID | str,
        game: str = "cs2",
        offset: int = 0,
        limit: int = 20,
    ) -> PlayerHistory:
        player_id = str(player_id)
        api_url = f"{cls.base_url}/players/{player_id}/history?game={game}&offset={offset}&limit={limit}"
        async with session.get(api_url) as response:
            if response.status != 200:
                logger.error(f"player_history APICall Error {response.status}: {response.content}")
                raise BadAPICallException(f"player_history with {response.status}: {response.content}")
            res = await response.json()
            return PlayerHistory(**res)

    @classmethod
    async def player_stats(
        cls, session: ClientSession, player_id: UUID | str, game_id: str = "cs2"
    ) -> PlayerGameStats:
        player_id = str(player_id)
        api_url = f"{cls.base_url}/players/{player_id}/stats/{game_id}"
        async with session.get(api_url) as response:
            if response.status != 200:
                logger.error(f"player_stats APICall Error {response.status}: {response.content}")
                raise BadAPICallException(f"player_stats with {response.status}: {response.content}")
            res = await response.json()
            return PlayerGameStats(**res)

    @classmethod
    async def player_stats_collection(
        cls,
        session: ClientSession,
        player_id: UUID | str,
        game_id: str = "cs2",
        page_size: int = 10,
        page: int = 1,
    ) -> PlayerStatsCollection:
        player_id = str(player_id)
        api_url = f"{cls.base_url}/players/{player_id}/games/{game_id}/stats?size={page_size}&page={page}"
        async with session.get(api_url) as response:
            if response.status != 200:
                raise BadAPICallException(f"player_stats with {response.status}: {response.content}")
            res = await response.json()
        return PlayerStatsCollection(**res)

    @classmethod
    async def match_details(cls, session: ClientSession, match_id: str) -> MatchDetails:
        api_url = f"{cls.base_url}/matches/{match_id}"
        async with session.get(api_url) as response:
            if response.status != 200:
                logger.error(f"match_details APICall Error {response.status}: {response.content}")
                raise BadAPICallException(f"match_details with {response.status}: {response.content}")
            res = await response.json()
            return MatchDetails(**res)

    @classmethod
    async def match_stats(cls, session: ClientSession, match_id: str) -> MatchStatistics:
        api_url = f"{cls.base_url}/matches/{match_id}/stats"
        async with session.get(api_url) as response:
            if response.status != 200:
                logger.error(f"match_stats APICall Error {response.status}: {response.content}")
                raise BadAPICallException(f"match_stats with {response.status}: {response.content}")
            res = await response.json()
            return MatchStatistics(**res)

    @classmethod
    async def region_stats(
        cls,
        session: ClientSession,
        player_id: UUID | str,
        region: str,
        country: str | None = None,
        game: str = "cs2",
    ) -> RegionStatistics:
        player_id = str(player_id)
        api_url = f"{cls.base_url}/rankings/games/{game}/regions/{region}/players/{player_id}?limit=2"
        if country:
            api_url += f"&country={country}"
        async with session.get(api_url) as response:
            if response.status != 200:
                logger.error(f"region_stats APICall Error {response.status}: {response.content}")
                raise BadAPICallException(f"region_stats with {response.status}: {response.content}")
            res = await response.json()
            return RegionStatistics(**res)


if __name__ == "__main__":

    async def main():
        async with aiohttp.ClientSession(headers=conf.FACEIT_HEADERS) as session:
            # res = await FaceitClient.match_stats(session, "1-c900d437-eff7-4536-9a32-f01c5cf7580c")
            # res = await FaceitClient.player_details_by_id(session, UUID("ad42c90b-45a9-49b6-8ab0-9c8662330543"))
            # res = await FaceitClient.player_details(session, "Ayudesee")
            # res = await FaceitClient.get_player_elo_by_nickname(session, "T1A-", "cs2")
            # res = await FaceitClient.player_history(session, UUID("ad42c90b-45a9-49b6-8ab0-9c8662330543"), limit=2)
            res = await FaceitClient.player_history(session, subscribers.TIA, limit=2)
            # res = await FaceitClient.match_details(session, "1-f0ad4c71-7fce-432b-8ca0-5261d85be686")
            # res = await FaceitClient.region_stats(session, UUID("278790a2-1f08-4350-bd96-427f7dcc8722"), region="EU")

            # res = await FaceitClient.player_stats_game(session, subscribers.AYUDESEE)

            print(res)

    asyncio.run(main())
