import json
import os

Steam_token = os.environ['Steam_token']
base_url = "https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v2/"


async def user_app_stat(session, steamid, appid=730):
    if steamid is None:
        return None

    api_url = f"{base_url}?key={Steam_token}&steamid={steamid}&appid={appid}"
    async with session.get(api_url) as res:
        if res.status == 200:
            bin_data = await res.read()
            return json.loads(bin_data.decode())
        else:
            return None


async def user_rec_played_stat(session, steamid=""):
    api_url = f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={Steam_token}&steamid={steamid}&format=json"
    if steamid is None:
        return None

    async with session.get(api_url) as res:
        if res.status == 200:
            bin_data = await res.read()
            return json.loads(bin_data.decode())
        else:
            return None
