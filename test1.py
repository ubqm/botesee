from PIL import Image, ImageFont, ImageDraw
import requests

request_json = {'transaction_id': 'f3ecc18b-1857-41c2-b0fb-b1bbf9702fc2', 'event': 'match_status_finished', 'event_id': '372bade4-5718-4d44-bdc1-2295b2b47a06', 'third_party_id': 'ad42c90b-45a9-49b6-8ab0-9c8662330543', 'app_id': '4ef06a92-08ba-425e-bf12-c49c17d5ec7e', 'timestamp': '2021-11-26T12:08:16Z', 'retry_count': 0, 'version': 1, 'payload': {'id': '1-d8935aa8-18a1-44e1-95f3-93381f147948', 'organizer_id': 'faceit', 'region': 'EU', 'game': 'csgo', 'version': 49, 'entity': {'id': '42e160fc-2651-4fa5-9a9b-829199e27adb', 'name': '5v5 Ranked', 'type': 'matchmaking'}, 'teams': [{'id': '3b6d3e0b-5da3-41ad-8bb9-57f658b7b8c1', 'name': 'team_VALTERRI', 'type': '', 'avatar': 'https://distribution.faceit-cdn.net/images/53b27ab8-b6cf-4735-8525-b398c13e06dd.jpeg', 'leader_id': '3b6d3e0b-5da3-41ad-8bb9-57f658b7b8c1', 'co_leader_id': '', 'roster': [{'id': '3b6d3e0b-5da3-41ad-8bb9-57f658b7b8c1', 'nickname': 'VALTERRI', 'avatar': 'https://distribution.faceit-cdn.net/images/53b27ab8-b6cf-4735-8525-b398c13e06dd.jpeg', 'game_id': '76561199112806464', 'game_name': 'korjcs', 'game_skill_level': 7, 'membership': '', 'anticheat_required': True}, {'id': 'cf7456bb-d9f9-496a-ab56-e5f227ce0c0f', 'nickname': 'Hayash1n', 'avatar': 'https://assets.faceit-cdn.net/avatars/cf7456bb-d9f9-496a-ab56-e5f227ce0c0f_1602190997425.jpg', 'game_id': '76561199073027642', 'game_name': 'hayash1n', 'game_skill_level': 5, 'membership': '', 'anticheat_required': True}, {'id': '5b979b4f-0928-4cc8-9cf7-e0738987335d', 'nickname': 'sherba2', 'avatar': 'https://distribution.faceit-cdn.net/images/40fece05-f7ee-4f65-bc0b-152201c38103.jpeg', 'game_id': '76561199168202676', 'game_name': 'Nisab', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': 'a3be0e59-7061-4045-af86-9b4a46b9e1bf', 'nickname': 'VildeadVAC', 'avatar': 'https://assets.faceit-cdn.net/avatars/a3be0e59-7061-4045-af86-9b4a46b9e1bf_1623504497187.jpg', 'game_id': '76561198358558410', 'game_name': 'Niya', 'game_skill_level': 7, 'membership': '', 'anticheat_required': True}, {'id': 'b3be78cb-d9d5-44fa-8d06-21050fd91b0b', 'nickname': 'sa1ve', 'avatar': 'https://assets.faceit-cdn.net/avatars/b3be78cb-d9d5-44fa-8d06-21050fd91b0b_1633866728715.jpg', 'game_id': '76561198822855913', 'game_name': 'sa1ve', 'game_skill_level': 7, 'membership': '', 'anticheat_required': True}], 'substitutions': 0, 'substitutes': None}, {'id': '57a38406-838d-4ec8-8a78-c364abda587f', 'name': 'team_Archi_28', 'type': '', 'avatar': 'https://assets.faceit-cdn.net/avatars/57a38406-838d-4ec8-8a78-c364abda587f_1616275205611.jpg', 'leader_id': '57a38406-838d-4ec8-8a78-c364abda587f', 'co_leader_id': '', 'roster': [{'id': '33d35bf8-a601-430a-b9c4-b0cf4da7f2c8', 'nickname': 'sun_device', 'avatar': 'https://distribution.faceit-cdn.net/images/a2f1c674-b520-44b7-b8b1-7f782b9980d7.jpeg', 'game_id': '76561198202704953', 'game_name': 'DeVVe', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': '32bf7b6f-5b3d-41a5-9a2b-a8814ee51fd8', 'nickname': 'vaizu374', 'avatar': 'https://distribution.faceit-cdn.net/images/607b4433-db5c-4d04-aaba-98340ab20e79.jpeg', 'game_id': '76561199106066551', 'game_name': 'azwxsecdrvftbgynhujmi', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': '57a38406-838d-4ec8-8a78-c364abda587f', 'nickname': 'Archi_28', 'avatar': 'https://assets.faceit-cdn.net/avatars/57a38406-838d-4ec8-8a78-c364abda587f_1616275205611.jpg', 'game_id': '76561199002867922', 'game_name': 'Archi', 'game_skill_level': 4, 'membership': '', 'anticheat_required': True}, {'id': 'd9f53258-8683-4fee-9e02-d49d5abc20da', 'nickname': '-fromjkeey', 'avatar': 'https://assets.faceit-cdn.net/avatars/d9f53258-8683-4fee-9e02-d49d5abc20da_1633792929506.jpg', 'game_id': '76561198187574425', 'game_name': '-fromjkeey', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': 'e1cddcbb-afdc-4e8e-abf2-eea5638f0363', 'nickname': 'dlp1x', 'avatar': 'https://assets.faceit-cdn.net/avatars/e1cddcbb-afdc-4e8e-abf2-eea5638f0363_1609000282402.jpg', 'game_id': '76561198129814795', 'game_name': 'dlp1x', 'game_skill_level': 8, 'membership': '', 'anticheat_required': True}], 'substitutions': 0, 'substitutes': None}], 'created_at': '2021-11-26T11:13:40Z', 'updated_at': '2021-11-26T12:08:16Z', 'started_at': '2021-11-26T11:17:53Z', 'finished_at': '2021-11-26T12:08:16Z'}}
stat_json = {'rounds': [{'best_of': '2', 'competition_id': None, 'game_id': 'csgo', 'game_mode': '5v5', 'match_id': '1-d8935aa8-18a1-44e1-95f3-93381f147948', 'match_round': '1', 'played': '1', 'round_stats': {'Region': 'EU', 'Winner': '3b6d3e0b-5da3-41ad-8bb9-57f658b7b8c1', 'Score': '16 / 14', 'Map': 'de_inferno', 'Rounds': '30'}, 'teams': [{'team_id': '3b6d3e0b-5da3-41ad-8bb9-57f658b7b8c1', 'premade': False, 'team_stats': {'Second Half Score': '10', 'Team Win': '1', 'Final Score': '16', 'Team Headshots': '7.6', 'Overtime score': '0', 'Team': 'team_VALTERRI', 'First Half Score': '6'}, 'players': [{'player_id': '3b6d3e0b-5da3-41ad-8bb9-57f658b7b8c1', 'nickname': 'VALTERRI', 'player_stats': {'Result': '1', 'Triple Kills': '1', 'K/D Ratio': '1.21', 'Assists': '1', 'Quadro Kills': '0', 'K/R Ratio': '0.77', 'Penta Kills': '1', 'Headshots %': '30', 'Deaths': '19', 'MVPs': '4', 'Kills': '23', 'Headshots': '7'}}, {'player_id': 'cf7456bb-d9f9-496a-ab56-e5f227ce0c0f', 'nickname': 'Hayash1n', 'player_stats': {'Assists': '7', 'Triple Kills': '1', 'MVPs': '6', 'Quadro Kills': '0', 'Deaths': '23', 'K/R Ratio': '0.73', 'Kills': '22', 'Penta Kills': '0', 'Result': '1', 'K/D Ratio': '0.96', 'Headshots %': '45', 'Headshots': '10'}}, {'player_id': '5b979b4f-0928-4cc8-9cf7-e0738987335d', 'nickname': 'sherba2', 'player_stats': {'Kills': '21', 'Triple Kills': '0', 'Assists': '3', 'Headshots %': '33', 'MVPs': '0', 'Headshots': '7', 'Result': '1', 'K/R Ratio': '0.7', 'K/D Ratio': '0.91', 'Penta Kills': '0', 'Deaths': '23', 'Quadro Kills': '0'}}, {'player_id': 'a3be0e59-7061-4045-af86-9b4a46b9e1bf', 'nickname': 'VildeadVAC', 'player_stats': {'Result': '1', 'Triple Kills': '1', 'Kills': '17', 'K/R Ratio': '0.57', 'Penta Kills': '0', 'K/D Ratio': '0.89', 'Headshots %': '24', 'MVPs': '1', 'Headshots': '4', 'Quadro Kills': '0', 'Deaths': '19', 'Assists': '5'}}, {'player_id': 'b3be78cb-d9d5-44fa-8d06-21050fd91b0b', 'nickname': 'sa1ve', 'player_stats': {'Headshots': '10', 'Assists': '4', 'K/D Ratio': '0.92', 'K/R Ratio': '0.73', 'MVPs': '5', 'Kills': '22', 'Quadro Kills': '0', 'Headshots %': '45', 'Result': '1', 'Triple Kills': '2', 'Penta Kills': '0', 'Deaths': '24'}}]}, {'team_id': '57a38406-838d-4ec8-8a78-c364abda587f', 'premade': False, 'team_stats': {'Final Score': '14', 'Team Headshots': '12.5', 'First Half Score': '9', 'Second Half Score': '5', 'Overtime score': '0', 'Team': 'team_Archi_28', 'Team Win': '0'}, 'players': [{'player_id': '32bf7b6f-5b3d-41a5-9a2b-a8814ee51fd8', 'nickname': 'vaizu374', 'player_stats': {'Penta Kills': '0', 'Result': '0', 'Headshots': '23', 'Triple Kills': '3', 'Quadro Kills': '1', 'K/D Ratio': '1.89', 'Assists': '4', 'K/R Ratio': '1.2', 'Kills': '36', 'Headshots %': '64', 'MVPs': '8', 'Deaths': '19'}}, {'player_id': '57a38406-838d-4ec8-8a78-c364abda587f', 'nickname': 'Archi_28', 'player_stats': {'Headshots %': '71', 'K/R Ratio': '0.7', 'Quadro Kills': '0', 'Triple Kills': '2', 'MVPs': '4', 'Kills': '21', 'K/D Ratio': '0.88', 'Headshots': '15', 'Penta Kills': '0', 'Result': '0', 'Deaths': '24', 'Assists': '3'}}, {'player_id': 'd9f53258-8683-4fee-9e02-d49d5abc20da', 'nickname': '-fromjkeey', 'player_stats': {'Result': '0', 'MVPs': '0', 'Kills': '21', 'Assists': '6', 'Penta Kills': '0', 'Headshots %': '38', 'Quadro Kills': '0', 'K/R Ratio': '0.7', 'Triple Kills': '0', 'Headshots': '8', 'Deaths': '22', 'K/D Ratio': '0.95'}}, {'player_id': 'e1cddcbb-afdc-4e8e-abf2-eea5638f0363', 'nickname': 'dlp1x', 'player_stats': {'Deaths': '19', 'Assists': '2', 'MVPs': '1', 'Quadro Kills': '0', 'Kills': '15', 'K/D Ratio': '0.79', 'Headshots %': '27', 'Headshots': '4', 'Result': '0', 'K/R Ratio': '0.5', 'Triple Kills': '0', 'Penta Kills': '0'}}]}]}]}
stat_json_bo3 = {'rounds': [{'best_of': '3', 'competition_id': None, 'game_id': 'csgo', 'game_mode': '5v5', 'match_id': '1-ca834a73-edbc-4348-b07c-1d52f457fc72', 'match_round': '1', 'played': '1', 'round_stats': {'Score': '12 / 16', 'Winner': 'f9146246-c88a-4fd8-a02e-e51dee628357', 'Region': 'EU', 'Map': 'de_inferno', 'Rounds': '28'}, 'teams': [{'team_id': '4eaaceaf-0e19-49fe-9616-99b907e71d08', 'premade': True, 'team_stats': {'Final Score': '12', 'Team Win': '0', 'Team Headshots': '9.8', 'Overtime score': '0', 'First Half Score': '8', 'Second Half Score': '4', 'Team': 'Penta Eye'}, 'players': [{'player_id': '67b15e2f-4d95-4151-9af6-fa5c476c8037', 'nickname': '7oXiK', 'player_stats': {'Assists': '3', 'Triple Kills': '0', 'Penta Kills': '0', 'K/R Ratio': '0.54', 'K/D Ratio': '0.94', 'Kills': '15', 'Headshots': '8', 'Deaths': '16', 'MVPs': '1', 'Headshots %': '53', 'Quadro Kills': '0', 'Result': '0'}}, {'player_id': '220685cd-1a18-4402-a9a9-ac240313cabd', 'nickname': 'XeeDo', 'player_stats': {'Deaths': '22', 'MVPs': '4', 'Quadro Kills': '0', 'Kills': '23', 'K/R Ratio': '0.82', 'Assists': '0', 'Penta Kills': '0', 'Result': '0', 'Triple Kills': '1', 'Headshots': '11', 'Headshots %': '48', 'K/D Ratio': '1.05'}}, {'player_id': '33d7179c-1480-429f-beb7-bb3c2dae2d4e', 'nickname': 'MoonLightttt', 'player_stats': {'Headshots %': '64', 'MVPs': '3', 'Result': '0', 'Kills': '14', 'Headshots': '9', 'Triple Kills': '0', 'Penta Kills': '0', 'Assists': '2', 'K/R Ratio': '0.5', 'K/D Ratio': '0.74', 'Quadro Kills': '0', 'Deaths': '19'}}, {'player_id': 'd1a0fba9-7352-476c-be03-a7babd155f0e', 'nickname': '-kind', 'player_stats': {'Deaths': '21', 'K/D Ratio': '0.76', 'Headshots %': '31', 'Kills': '16', 'K/R Ratio': '0.57', 'Result': '0', 'Triple Kills': '1', 'Penta Kills': '0', 'MVPs': '2', 'Headshots': '5', 'Quadro Kills': '0', 'Assists': '2'}}, {'player_id': 'd0b7218c-a540-423f-960e-f6e9a8b3b10a', 'nickname': '-EcoCobra-', 'player_stats': {'Penta Kills': '0', 'MVPs': '2', 'K/R Ratio': '0.86', 'Quadro Kills': '2', 'K/D Ratio': '1.2', 'Triple Kills': '0', 'Headshots %': '67', 'Kills': '24', 'Result': '0', 'Headshots': '16', 'Assists': '4', 'Deaths': '20'}}]}, {'team_id': 'f9146246-c88a-4fd8-a02e-e51dee628357', 'premade': True, 'team_stats': {'Team': 'Neo noir', 'Final Score': '16', 'Overtime score': '0', 'First Half Score': '7', 'Team Win': '1', 'Team Headshots': '8.8', 'Second Half Score': '9'}, 'players': [{'player_id': '87dcb2d9-e667-49fc-9282-6826751bea3c', 'nickname': 'putjje', 'player_stats': {'K/D Ratio': '1.18', 'Penta Kills': '0', 'Headshots %': '45', 'Deaths': '17', 'Quadro Kills': '0', 'Kills': '20', 'Triple Kills': '1', 'K/R Ratio': '0.71', 'Result': '1', 'Headshots': '9', 'Assists': '0', 'MVPs': '6'}}, {'player_id': 'ad42c90b-45a9-49b6-8ab0-9c8662330543', 'nickname': 'Ayudesee', 'player_stats': {'Headshots %': '50', 'Penta Kills': '0', 'Deaths': '18', 'Assists': '4', 'Result': '1', 'Kills': '18', 'Triple Kills': '1', 'K/D Ratio': '1', 'K/R Ratio': '0.64', 'MVPs': '1', 'Headshots': '9', 'Quadro Kills': '0'}}, {'player_id': '8cbb0b36-4c6b-4ebd-a92b-829234016626', 'nickname': 'TV_Hawk_BLR', 'player_stats': {'MVPs': '4', 'Kills': '16', 'Headshots %': '44', 'Triple Kills': '1', 'Assists': '6', 'K/R Ratio': '0.57', 'Result': '1', 'K/D Ratio': '0.94', 'Penta Kills': '0', 'Deaths': '17', 'Headshots': '7', 'Quadro Kills': '0'}}, {'player_id': '278790a2-1f08-4350-bd96-427f7dcc8722', 'nickname': '-NAPAD', 'player_stats': {'Assists': '5', 'Headshots %': '42', 'Result': '1', 'Deaths': '20', 'Triple Kills': '0', 'Quadro Kills': '1', 'K/D Ratio': '1.2', 'K/R Ratio': '0.86', 'MVPs': '2', 'Headshots': '10', 'Kills': '24', 'Penta Kills': '0'}}, {'player_id': '18e2a663-9e20-4db9-8b29-3c3cbdff30ac', 'nickname': '-MORZY', 'player_stats': {'K/R Ratio': '0.71', 'Headshots %': '45', 'MVPs': '3', 'K/D Ratio': '1', 'Headshots': '9', 'Result': '1', 'Quadro Kills': '0', 'Triple Kills': '1', 'Deaths': '20', 'Assists': '8', 'Kills': '20', 'Penta Kills': '0'}}]}]}, {'best_of': '3', 'competition_id': None, 'game_id': 'csgo', 'game_mode': '5v5', 'match_id': '1-ca834a73-edbc-4348-b07c-1d52f457fc72', 'match_round': '2', 'played': '2', 'round_stats': {'Rounds': '29', 'Winner': 'f9146246-c88a-4fd8-a02e-e51dee628357', 'Region': 'EU', 'Map': 'de_overpass', 'Score': '13 / 16'}, 'teams': [{'team_id': '4eaaceaf-0e19-49fe-9616-99b907e71d08', 'premade': True, 'team_stats': {'Final Score': '13', 'Overtime score': '0', 'First Half Score': '10', 'Second Half Score': '3', 'Team': 'Penta Eye', 'Team Win': '0', 'Team Headshots': '9.2'}, 'players': [{'player_id': '67b15e2f-4d95-4151-9af6-fa5c476c8037', 'nickname': '7oXiK', 'player_stats': {'Triple Kills': '1', 'Quadro Kills': '0', 'Kills': '24', 'Assists': '1', 'K/R Ratio': '0.83', 'Headshots': '10', 'Result': '0', 'Deaths': '19', 'Penta Kills': '0', 'Headshots %': '42', 'MVPs': '3', 'K/D Ratio': '1.26'}}, {'player_id': '220685cd-1a18-4402-a9a9-ac240313cabd', 'nickname': 'XeeDo', 'player_stats': {'K/D Ratio': '0.7', 'Assists': '2', 'Headshots %': '43', 'Deaths': '20', 'K/R Ratio': '0.48', 'Result': '0', 'Penta Kills': '0', 'Headshots': '6', 'MVPs': '1', 'Triple Kills': '0', 'Quadro Kills': '0', 'Kills': '14'}}, {'player_id': '33d7179c-1480-429f-beb7-bb3c2dae2d4e', 'nickname': 'MoonLightttt', 'player_stats': {'Penta Kills': '0', 'Headshots': '8', 'Kills': '14', 'K/D Ratio': '0.64', 'K/R Ratio': '0.48', 'Triple Kills': '0', 'MVPs': '3', 'Assists': '3', 'Headshots %': '57', 'Result': '0', 'Deaths': '22', 'Quadro Kills': '0'}}, {'player_id': 'd1a0fba9-7352-476c-be03-a7babd155f0e', 'nickname': '-kind', 'player_stats': {'Headshots': '11', 'Triple Kills': '1', 'Quadro Kills': '1', 'Penta Kills': '0', 'Deaths': '22', 'MVPs': '5', 'Kills': '28', 'K/R Ratio': '0.97', 'K/D Ratio': '1.27', 'Result': '0', 'Assists': '3', 'Headshots %': '39'}}, {'player_id': 'd0b7218c-a540-423f-960e-f6e9a8b3b10a', 'nickname': '-EcoCobra-', 'player_stats': {'Deaths': '23', 'K/D Ratio': '0.96', 'Headshots %': '50', 'Penta Kills': '0', 'Result': '0', 'Assists': '4', 'Headshots': '11', 'Quadro Kills': '0', 'Kills': '22', 'Triple Kills': '1', 'K/R Ratio': '0.76', 'MVPs': '1'}}]}, {'team_id': 'f9146246-c88a-4fd8-a02e-e51dee628357', 'premade': True, 'team_stats': {'Team': 'Neo noir', 'Final Score': '16', 'Overtime score': '0', 'First Half Score': '5', 'Second Half Score': '11', 'Team Win': '1', 'Team Headshots': '9.2'}, 'players': [{'player_id': '87dcb2d9-e667-49fc-9282-6826751bea3c', 'nickname': 'putjje', 'player_stats': {'Kills': '18', 'Assists': '5', 'Penta Kills': '0', 'MVPs': '3', 'Quadro Kills': '0', 'Triple Kills': '2', 'K/D Ratio': '0.82', 'Headshots %': '39', 'Result': '1', 'Headshots': '7', 'K/R Ratio': '0.62', 'Deaths': '22'}}, {'player_id': 'ad42c90b-45a9-49b6-8ab0-9c8662330543', 'nickname': 'Ayudesee', 'player_stats': {'Headshots %': '33', 'Result': '1', 'Quadro Kills': '1', 'Kills': '33', 'MVPs': '7', 'K/D Ratio': '1.74', 'Deaths': '19', 'K/R Ratio': '1.14', 'Headshots': '11', 'Triple Kills': '3', 'Assists': '3', 'Penta Kills': '0'}}, {'player_id': '8cbb0b36-4c6b-4ebd-a92b-829234016626', 'nickname': 'TV_Hawk_BLR', 'player_stats': {'K/R Ratio': '0.45', 'Result': '1', 'Deaths': '19', 'Assists': '7', 'MVPs': '1', 'Triple Kills': '1', 'Headshots': '8', 'Kills': '13', 'Penta Kills': '0', 'Headshots %': '62', 'Quadro Kills': '0', 'K/D Ratio': '0.68'}}, {'player_id': '278790a2-1f08-4350-bd96-427f7dcc8722', 'nickname': '-NAPAD', 'player_stats': {'Headshots %': '56', 'Quadro Kills': '2', 'Headshots': '14', 'Result': '1', 'Triple Kills': '0', 'Assists': '4', 'MVPs': '4', 'K/D Ratio': '1.14', 'K/R Ratio': '0.86', 'Kills': '25', 'Penta Kills': '0', 'Deaths': '22'}}, {'player_id': '18e2a663-9e20-4db9-8b29-3c3cbdff30ac', 'nickname': '-MORZY', 'player_stats': {'Kills': '17', 'Deaths': '20', 'K/R Ratio': '0.59', 'Result': '1', 'Triple Kills': '0', 'Penta Kills': '0', 'Headshots %': '35', 'Headshots': '6', 'Assists': '2', 'Quadro Kills': '0', 'K/D Ratio': '0.85', 'MVPs': '1'}}]}]}]}


def collect_image(request_json, stat_json):
    image_list = []
    font_folder = 'Outfit'
    font_file = 'Outfit-Bold.ttf'
    font_file_mainscore = 'Outfit-ExtraBold.ttf'

    font_avs = ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file}', 18)
    font_mainscore = ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file_mainscore}', 50)
    font_player_score = ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file}', 32)
    font_player_stats = ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file}', 22)
    font_halftimes = ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file}', 22)

    dark_avatar_bot = Image.open('templates/background_features/for_avatar_bot.png')
    dark_avatar_top = Image.open('templates/background_features/for_avatar_top.png')

    for idx_round, round in enumerate(stat_json['rounds']):
        img1 = Image.open(f'templates/maps/{round["round_stats"]["Map"]}.jpg')
        img1 = img1.resize((960, 540))
        draw = ImageDraw.Draw(img1)
        if round['teams'][0]['team_stats']['Team Win'] == '1':
            img2 = Image.open('templates/background_features/Win-topleft.png')
            img3 = Image.open('templates/background_features/Lose-botleft.png')
        else:
            img2 = Image.open('templates/background_features/Lose-topleft.png')
            img3 = Image.open('templates/background_features/Win-botleft.png')
        img1.paste(img2, (0, 0), img2)
        img1.paste(img3, (0, 0), img3)
        dark_middle = Image.open('templates/background_features/dark-middle2.png')
        img1.paste(dark_middle, (0, 0), dark_middle)

        if 'Overtime score' in round['teams'][0]['team_stats'].keys():
            if round['teams'][0]['team_stats']['Overtime score'] == '0' and round['teams'][1]['team_stats']['Overtime score'] == '0':
                isOvertimeinGame = False
            else:
                isOvertimeinGame = True
        else:
            isOvertimeinGame = False

        for idx_team, team in enumerate(round['teams']):
            if isOvertimeinGame:
                halftimes = f"{team['team_stats']['First Half Score']}—{team['team_stats']['Second Half Score']}—{team['team_stats']['Overtime score']}"
                w, h = draw.textsize(halftimes, font=font_halftimes)
                draw.text(((146 - w) / 2, 235 + 42 * idx_team), halftimes, font=font_halftimes)
            else:
                halftimes = f"{team['team_stats']['First Half Score']}—{team['team_stats']['Second Half Score']}"
                w, h = draw.textsize(halftimes, font=font_halftimes)
                draw.text(((146 - w) / 2, 235 + 42 * idx_team), halftimes, font=font_halftimes)

            for idx_player, player in enumerate(team['players']):
                for idx_req_player, req_player in enumerate(request_json['payload']['teams'][idx_team]['roster']):
                    if player['nickname'] == req_player['nickname']:
                        if float(player["player_stats"]["K/D Ratio"]) >= 1.3:
                            stat_color = (0, 190, 0, 255)
                        elif float(player["player_stats"]["K/D Ratio"]) < 0.6:
                            stat_color = (170, 0, 0, 255)
                        elif 0.8 > float(player["player_stats"]["K/D Ratio"]) >= 0.6:
                            stat_color = (255, 165, 0, 255)
                        else:
                            stat_color = (255, 255, 255, 255)

                        if req_player['avatar'] != '':
                            avatar_req = requests.get(req_player['avatar'], stream=True)
                            avatar_img = Image.open(avatar_req.raw)
                            avatar_img = avatar_img.resize((130, 130))
                        else:
                            avatar_img = Image.open('templates/question-mark-icon.jpg')
                            avatar_img = avatar_img.resize((130, 130))
                        faceitlvl = req_player['game_skill_level']
                        if idx_team == 0:
                            avatar_img.paste(dark_avatar_bot, (0, 0), dark_avatar_bot)
                            avatar_img.paste(Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"),
                                             (0, 0),
                                             Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"))
                        else:
                            avatar_img.paste(dark_avatar_top, (0, 0), dark_avatar_top)
                            avatar_img.paste(Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"),
                                             (0, 106),
                                             Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"))
                        draw_avatar = ImageDraw.Draw(avatar_img)

                        w, h = draw.textsize(req_player['nickname'], font=font_avs)
                        if w > 130:
                            draw_avatar.text((0, 107 - idx_team * 107), req_player['nickname'], font=font_avs, fill=stat_color)
                        else:
                            draw_avatar.text(((130 - w) / 2, 107 - idx_team * 107), req_player['nickname'], font=font_avs)

                        img1.paste(avatar_img, (146 + idx_player * 162, 20 + 370 * idx_team))

                        kad = f'{player["player_stats"]["Kills"]}/{player["player_stats"]["Assists"]}/{player["player_stats"]["Deaths"]}'
                        w, h = draw.textsize(kad, font=font_player_score)
                        draw.text((130 + (162 - w) / 2 + idx_player * 162, 155 + 195 * idx_team), kad, font=font_player_score)
                        mvp = f'MVP: {player["player_stats"]["MVPs"]}'
                        draw.text((146 + idx_player * 162, 200 + 116 * idx_team), mvp, font=font_player_stats)
                        kr = f'K/R: {player["player_stats"]["K/R Ratio"]}'
                        draw.text((146 + idx_player * 162, 220 + 76 * idx_team), kr, font=font_player_stats)
                        kd = f'K/D: {player["player_stats"]["K/D Ratio"]}'
                        draw.text((146 + idx_player * 162, 240 + 36 * idx_team), kd, font=font_player_stats, fill=stat_color)
                        # hs = f'HS %: {player["player_stats"]["Headshots %"]}'
                        # draw.text((146 + idx_player * 162, 240 + 36 * idx_team), hs, font=font_player_stats)

        w, h = draw.textsize(round["teams"][0]["team_stats"]["Final Score"], font=font_mainscore)
        draw.text(((146 - w) / 2, 65), round["teams"][0]["team_stats"]["Final Score"], font=font_mainscore)
        w, h = draw.textsize(round["teams"][1]["team_stats"]["Final Score"], font=font_mainscore)
        draw.text(((146 - w) / 2, 425), round["teams"][1]["team_stats"]["Final Score"], font=font_mainscore)
        image_list.append(img1)

    return image_list
#
#
imgl = collect_image(request_json, stat_json)
for image in imgl:
    image.show()