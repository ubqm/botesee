import asyncio
import json
from typing import Union

import aiohttp

from env_variables import faceit_headers

base_url = "https://open.faceit.com/data/v4"


async def player_details(session, nickname=None) -> Union[dict, None]:
    api_url = "{}/players".format(base_url)
    if nickname is None:
        return None
    api_url += f"?nickname={nickname}"
    async with session.get(api_url) as res:
        if res.status == 200:
            bin_data = await res.read()
            return json.loads(bin_data.decode())
        else:
            return None


async def get_player_elo_by_nickname(session, nickname: str = None) -> str:
    res = await player_details(session, nickname)
    return str(res['games']['csgo']['faceit_elo']) if res else 'N/A'


async def player_details_by_id(session, player_id=None):
    api_url = "{}/players".format(base_url)
    if player_id is None:
        return None
    api_url += f"/{player_id}"
    async with session.get(api_url) as res:
        if res.status == 200:
            bin_data = await res.read()
            return json.loads(bin_data.decode())
        else:
            return None


async def player_history(session, player_id=None, game="csgo", offset=0, limit=20):
    api_url = f"{base_url}/players/{player_id}/history?game={game}&offset={offset}&limit={limit}"
    if player_id is None:
        return None
    async with session.get(api_url) as res:
        if res.status == 200:
            bin_data = await res.read()
            return json.loads(bin_data.decode())
        else:
            return None


async def match_details(session, match_id=None):
    if match_id is None:
        return None
    api_url = "{}/matches/{}".format(base_url, match_id)
    async with session.get(api_url) as res:
        if res.status == 200:
            bin_data = await res.read()
            return json.loads(bin_data.decode())
        else:
            return None


async def match_stats(session, match_id=None):
    if match_id is None:
        return None
    api_url = "{}/matches/{}/stats".format(base_url, match_id)
    async with session.get(api_url) as res:
        if res.status == 200:
            bin_data = await res.read()
            return json.loads(bin_data.decode())
        else:
            return None


async def region_stats(session, player_id, region, country=None):
    api_url = f"{base_url}/rankings/games/csgo/regions/{region}/players/{player_id}"
    if country:
        api_url += f"?country={country}&limit=2"
    else:
        api_url += "&limit=2"
    async with session.get(api_url) as res:
        if res.status == 200:
            bin_data = await res.read()
            return json.loads(bin_data.decode())
        else:
            return None


async def main():
    async with aiohttp.ClientSession(headers=faceit_headers) as session:
        res = await player_details(session, "Dantist")
        print(res)

if __name__ == '__main__':
    asyncio.run(main())
