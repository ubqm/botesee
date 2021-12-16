import requests
import json
import os

Steam_token = os.environ['Steam_token']
base_url = 'https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v2/'


def user_app_stat(steamid='', appid=730):
    if steamid != '':
        api_url = f'{base_url}?key={Steam_token}&steamid={steamid}&appid={appid}'
        res = requests.get(api_url)

        if res.status_code == 200:
            return json.loads(res.content.decode('utf-8'))
        else:
            return None
    else:
        return None


def user_rec_played_stat(steamid=''):
    if steamid != '':
        res = requests.get(
            f'http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={Steam_token}&steamid={steamid}&format=json')
        if res.status_code == 200:
            return json.loads(res.content.decode('utf-8'))
        else:
            return None
    else:
        return None
