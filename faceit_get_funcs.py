import requests
import json

# '''
# ad42c90b-45a9-49b6-8ab0-9c8662330543
# 278790a2-1f08-4350-bd96-427f7dcc8722
# 18e2a663-9e20-4db9-8b29-3c3cbdff30ac
# 8cbb0b36-4c6b-4ebd-a92b-829234016626
# e1cddcbb-afdc-4e8e-abf2-eea5638f0363
# 9da3572e-1960-4ba0-bd3c-d38ef34c1f1c
# b8e5cd07-1b43-4203-9173-465fddcd391f
# 4e7d1f6c-9045-4800-8eda-23c892dcd814
# '''

api_token = '7e7008f6-79f4-4e57-a80a-c486f89fa50e'
base_url = "https://open.faceit.com/data/v4"

headers = {
    'accept': 'application/json',
    'Authorization': f'Bearer {api_token}'
}


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
    print(res)
    print(res.headers)

    if res.status_code is 200:
        return json.loads(res.content.decode('utf-8'))
    else:
        return None


def match_details(match_id=None):
    if match_id is None:
        print("match_id cannot be nothing")
    else:
        api_url = "{}/matches/{}".format(base_url, match_id)

        res = requests.get(api_url, headers=headers)
        if res.status_code is 200:
            return json.loads(res.content.decode('utf-8'))
        else:
            return None


def match_stats(match_id=None):
    if match_id is None:
        print("match_id cannot be nothing")
    else:
        api_url = "{}/matches/{}/stats".format(base_url, match_id)

        res = requests.get(api_url, headers=headers)
        if res.status_code is 200:
            return json.loads(res.content.decode('utf-8'))
        else:
            return None
