import requests
import json
import os


Faceit_token = os.environ['Faceit_token']
base_url = "https://open.faceit.com/data/v4"
headers = {'accept': 'application/json', 'Authorization': f'Bearer {Faceit_token}'}


def player_details(nickname=None, game=None, game_player_id=None):

    api_url = "{}/players".format(base_url)
    if nickname is not None:
        api_url += "?nickname={}".format(nickname)
    if game_player_id is not None:
        if nickname is not None:
            api_url += "&game_player_id={}".format(game_player_id)
        else:
            api_url += "?game_player_id={}".format(game_player_id)
    if game is not None:
        api_url += "&game={}".format(game)

    res = requests.get(api_url, headers=headers)

    if res.status_code == 200:
        return json.loads(res.content.decode('utf-8'))
    else:
        return None


def player_history(player_id=None, game='csgo', limit=20):
    api_url = f"{base_url}/players/{player_id}/history?game={game}&offset=0&limit={limit}"
    if player_id is not None:
        res = requests.get(api_url, headers=headers)
        if res.status_code == 200:
            return json.loads(res.content.decode('utf-8'))
        else:
            return None
    else:
        return None


def match_details(match_id=None):
    if match_id is None:
        print("match_id cannot be nothing")
    else:
        api_url = "{}/matches/{}".format(base_url, match_id)

        res = requests.get(api_url, headers=headers)
        if res.status_code == 200:
            return json.loads(res.content.decode('utf-8'))
        else:
            return None


def match_stats(match_id=None):
    if match_id is None:
        print("match_id cannot be nothing")
    else:
        api_url = "{}/matches/{}/stats".format(base_url, match_id)

        res = requests.get(api_url, headers=headers)
        if res.status_code == 200:
            return json.loads(res.content.decode('utf-8'))
        else:
            return None


def region_stats(player_id, region, country=""):
    if country == "":
        api_url = "{}/rankings/games/csgo/regions/{}/players/{}?limit=2".format(base_url, region, player_id)
        res = requests.get(api_url, headers=headers)
        if res.status_code == 200:
            return json.loads(res.content.decode('utf-8'))
        else:
            return None
    else:
        api_url = "{}/rankings/games/csgo/regions/{}/players/{}?country={}&limit=2".format(base_url, region, player_id,
                                                                                           country)
        res = requests.get(api_url, headers=headers)
        if res.status_code == 200:
            return json.loads(res.content.decode('utf-8'))
        else:
            return None
