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
# request_json = {'transaction_id': 'ea21ff1c-da66-44f4-9b1d-8d69d4757674', 'event': 'match_status_finished', 'event_id': 'f577fc62-a2ec-4983-9224-b2f6ababa9b8', 'third_party_id': 'ad42c90b-45a9-49b6-8ab0-9c8662330543', 'app_id': '4ef06a92-08ba-425e-bf12-c49c17d5ec7e', 'timestamp': '2021-04-08T11:10:06Z', 'retry_count': 0, 'version': 1, 'payload': {'id': '1-2a269a3b-5e11-4ba9-8ce6-81cd79d16809', 'organizer_id': 'faceit', 'region': 'EU', 'game': 'csgo', 'version': 48, 'entity': {'id': '42e160fc-2651-4fa5-9a9b-829199e27adb', 'name': 'CS:GO 5v5', 'type': 'matchmaking'}, 'teams': [{'id': 'dc4eff6f-d501-4249-a910-435d3b26a2b8', 'name': 'team_crckedD', 'type': '', 'avatar': 'https://assets.faceit-cdn.net/avatars/dc4eff6f-d501-4249-a910-435d3b26a2b8_1617786870610.jpg', 'leader_id': 'dc4eff6f-d501-4249-a910-435d3b26a2b8', 'co_leader_id': '', 'roster': [{'id': 'dc4eff6f-d501-4249-a910-435d3b26a2b8', 'nickname': 'crckedD', 'avatar': 'https://assets.faceit-cdn.net/avatars/dc4eff6f-d501-4249-a910-435d3b26a2b8_1617786870610.jpg', 'game_id': '76561199038678403', 'game_name': '-sweden 100ping', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': 'd2f2eaa0-d855-4e40-8d58-c497ab788584', 'nickname': 'Sokkan', 'avatar': 'https://assets.faceit-cdn.net/avatars/d2f2eaa0-d855-4e40-8d58-c497ab788584_1617192548276.jpg', 'game_id': '76561198056151703', 'game_name': 'Tyran', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': '89f750fa-3934-410f-93a1-fb7e68d9c079', 'nickname': '-KAJZE', 'avatar': 'https://assets.faceit-cdn.net/avatars/89f750fa-3934-410f-93a1-fb7e68d9c079_1601068561726.jpg', 'game_id': '76561198414640173', 'game_name': 'KAJZE', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': '0ecf6c91-280e-46d5-ba15-3e03b2e0bb07', 'nickname': 'Velvis', 'avatar': 'https://assets.faceit-cdn.net/avatars/0ecf6c91-280e-46d5-ba15-3e03b2e0bb07_1614864208684.jpg', 'game_id': '76561198122333283', 'game_name': '♛𝓥𝓮𝓵𝓿𝓲𝓼♛', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': '0e2de681-8f5e-445e-9935-f030b3f1ad54', 'nickname': 'Neff0', 'avatar': '', 'game_id': '76561198165335674', 'game_name': 'Neffo', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}], 'substitutions': 0, 'substitutes': None}, {'id': 'ed19e4d0-27a3-4562-b4ab-9cd5b9f33cab', 'name': 'team_burgE77', 'type': '', 'avatar': '', 'leader_id': 'ed19e4d0-27a3-4562-b4ab-9cd5b9f33cab', 'co_leader_id': '', 'roster': [{'id': 'ed19e4d0-27a3-4562-b4ab-9cd5b9f33cab', 'nickname': 'burgE77', 'avatar': '', 'game_id': '76561198843744707', 'game_name': 'burge35', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': '638e4e95-7cba-4d4a-8cb0-273fb09fd7bd', 'nickname': '4o_dal_jeest', 'avatar': 'https://assets.faceit-cdn.net/avatars/638e4e95-7cba-4d4a-8cb0-273fb09fd7bd_1603709780030.jpg', 'game_id': '76561199003173738', 'game_name': 'lev2512', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': '7007d6cb-fd8d-4279-94c6-3705d1c8e3f3', 'nickname': '-Exp0', 'avatar': 'https://assets.faceit-cdn.net/avatars/7007d6cb-fd8d-4279-94c6-3705d1c8e3f3_1552612915592.jpg', 'game_id': '76561198160813877', 'game_name': 'Exp0 ♛', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': '278790a2-1f08-4350-bd96-427f7dcc8722', 'nickname': '-NAPAD', 'avatar': 'https://assets.faceit-cdn.net/avatars/278790a2-1f08-4350-bd96-427f7dcc8722_1583523957971.jpg', 'game_id': '76561198061461007', 'game_name': '-NAPAD`11 #ACIDHOUZE', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': 'c6841b96-765c-469f-ac3a-e22d5c4c87c0', 'nickname': '-example-_-', 'avatar': 'https://assets.faceit-cdn.net/avatars/c6841b96-765c-469f-ac3a-e22d5c4c87c0_1611353077607.jpg', 'game_id': '76561199041548369', 'game_name': '-example-_-', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}], 'substitutions': 0, 'substitutes': None}], 'created_at': '2021-04-08T10:27:04Z', 'updated_at': '2021-04-08T11:10:06Z', 'started_at': '2021-04-08T10:30:35Z', 'finished_at': '2021-04-08T11:10:06Z'}}
# req_bad_stats = {'transaction_id': 'f3ecc18b-1857-41c2-b0fb-b1bbf9702fc2', 'event': 'match_status_finished', 'event_id': '372bade4-5718-4d44-bdc1-2295b2b47a06', 'third_party_id': 'ad42c90b-45a9-49b6-8ab0-9c8662330543', 'app_id': '4ef06a92-08ba-425e-bf12-c49c17d5ec7e', 'timestamp': '2021-11-26T12:08:16Z', 'retry_count': 0, 'version': 1, 'payload': {'id': '1-d8935aa8-18a1-44e1-95f3-93381f147948', 'organizer_id': 'faceit', 'region': 'EU', 'game': 'csgo', 'version': 49, 'entity': {'id': '42e160fc-2651-4fa5-9a9b-829199e27adb', 'name': '5v5 Ranked', 'type': 'matchmaking'}, 'teams': [{'id': '3b6d3e0b-5da3-41ad-8bb9-57f658b7b8c1', 'name': 'team_VALTERRI', 'type': '', 'avatar': 'https://distribution.faceit-cdn.net/images/53b27ab8-b6cf-4735-8525-b398c13e06dd.jpeg', 'leader_id': '3b6d3e0b-5da3-41ad-8bb9-57f658b7b8c1', 'co_leader_id': '', 'roster': [{'id': '3b6d3e0b-5da3-41ad-8bb9-57f658b7b8c1', 'nickname': 'VALTERRI', 'avatar': 'https://distribution.faceit-cdn.net/images/53b27ab8-b6cf-4735-8525-b398c13e06dd.jpeg', 'game_id': '76561199112806464', 'game_name': 'korjcs', 'game_skill_level': 7, 'membership': '', 'anticheat_required': True}, {'id': 'cf7456bb-d9f9-496a-ab56-e5f227ce0c0f', 'nickname': 'Hayash1n', 'avatar': 'https://assets.faceit-cdn.net/avatars/cf7456bb-d9f9-496a-ab56-e5f227ce0c0f_1602190997425.jpg', 'game_id': '76561199073027642', 'game_name': 'hayash1n', 'game_skill_level': 5, 'membership': '', 'anticheat_required': True}, {'id': '5b979b4f-0928-4cc8-9cf7-e0738987335d', 'nickname': 'sherba2', 'avatar': 'https://distribution.faceit-cdn.net/images/40fece05-f7ee-4f65-bc0b-152201c38103.jpeg', 'game_id': '76561199168202676', 'game_name': 'Nisab', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': 'a3be0e59-7061-4045-af86-9b4a46b9e1bf', 'nickname': 'VildeadVAC', 'avatar': 'https://assets.faceit-cdn.net/avatars/a3be0e59-7061-4045-af86-9b4a46b9e1bf_1623504497187.jpg', 'game_id': '76561198358558410', 'game_name': 'Niya', 'game_skill_level': 7, 'membership': '', 'anticheat_required': True}, {'id': 'b3be78cb-d9d5-44fa-8d06-21050fd91b0b', 'nickname': 'sa1ve', 'avatar': 'https://assets.faceit-cdn.net/avatars/b3be78cb-d9d5-44fa-8d06-21050fd91b0b_1633866728715.jpg', 'game_id': '76561198822855913', 'game_name': 'sa1ve', 'game_skill_level': 7, 'membership': '', 'anticheat_required': True}], 'substitutions': 0, 'substitutes': None}, {'id': '57a38406-838d-4ec8-8a78-c364abda587f', 'name': 'team_Archi_28', 'type': '', 'avatar': 'https://assets.faceit-cdn.net/avatars/57a38406-838d-4ec8-8a78-c364abda587f_1616275205611.jpg', 'leader_id': '57a38406-838d-4ec8-8a78-c364abda587f', 'co_leader_id': '', 'roster': [{'id': '33d35bf8-a601-430a-b9c4-b0cf4da7f2c8', 'nickname': 'sun_device', 'avatar': 'https://distribution.faceit-cdn.net/images/a2f1c674-b520-44b7-b8b1-7f782b9980d7.jpeg', 'game_id': '76561198202704953', 'game_name': 'DeVVe', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': '32bf7b6f-5b3d-41a5-9a2b-a8814ee51fd8', 'nickname': 'vaizu374', 'avatar': 'https://distribution.faceit-cdn.net/images/607b4433-db5c-4d04-aaba-98340ab20e79.jpeg', 'game_id': '76561199106066551', 'game_name': 'azwxsecdrvftbgynhujmi', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': '57a38406-838d-4ec8-8a78-c364abda587f', 'nickname': 'Archi_28', 'avatar': 'https://assets.faceit-cdn.net/avatars/57a38406-838d-4ec8-8a78-c364abda587f_1616275205611.jpg', 'game_id': '76561199002867922', 'game_name': 'Archi', 'game_skill_level': 4, 'membership': '', 'anticheat_required': True}, {'id': 'd9f53258-8683-4fee-9e02-d49d5abc20da', 'nickname': '-fromjkeey', 'avatar': 'https://assets.faceit-cdn.net/avatars/d9f53258-8683-4fee-9e02-d49d5abc20da_1633792929506.jpg', 'game_id': '76561198187574425', 'game_name': '-fromjkeey', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': 'e1cddcbb-afdc-4e8e-abf2-eea5638f0363', 'nickname': 'dlp1x', 'avatar': 'https://assets.faceit-cdn.net/avatars/e1cddcbb-afdc-4e8e-abf2-eea5638f0363_1609000282402.jpg', 'game_id': '76561198129814795', 'game_name': 'dlp1x', 'game_skill_level': 8, 'membership': '', 'anticheat_required': True}], 'substitutions': 0, 'substitutes': None}], 'created_at': '2021-11-26T11:13:40Z', 'updated_at': '2021-11-26T12:08:16Z', 'started_at': '2021-11-26T11:17:53Z', 'finished_at': '2021-11-26T12:08:16Z'}}
with open('token_faceit.txt', 'r') as file:
    api_token = file.read()
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

    if res.status_code == 200:
        return json.loads(res.content.decode('utf-8'))
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
