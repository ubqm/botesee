import PIL.ImageShow
from PIL import Image, ImageFont
import requests
from io import BytesIO
from PIL import ImageDraw
from imageCollector import collect_image

request_json_test = {'transaction_id': 'aab7fe07-9433-457b-8ac7-8793a804196c', 'event': 'match_status_finished',
                     'event_id': 'a3e4d508-0502-4283-b8ac-7b10020e3d61',
                     'third_party_id': 'ad42c90b-45a9-49b6-8ab0-9c8662330543', 'app_id': '4ef06a92-08ba-425e-bf12-c49c17d5ec7e',
                     'timestamp': '2021-11-22T18:45:44Z', 'retry_count': 0, 'version': 1,
                     'payload': {'id': '1-f76d48b9-70b1-4c1d-8a2d-b7e555aea199', 'organizer_id': 'faceit', 'region': 'EU', 'game': 'csgo', 'version': 39,
                                 'entity': {'id': '42e160fc-2651-4fa5-9a9b-829199e27adb', 'name': 'CS:GO 5v5', 'type': 'matchmaking'},
                                 'teams': [{'id': 'eebcf20d-1332-466f-b132-57011312cc23', 'name': 'team_lost1769-', 'type': '',
                                            'avatar': 'https://distribution.faceit-cdn.net/images/e3d3cc7a-e406-4e9d-9fc6-8a8f3c99bd98.jpeg',
                                            'leader_id': 'eebcf20d-1332-466f-b132-57011312cc23', 'co_leader_id': '',
                                            'roster': [{'id': 'fd440a46-2164-41e1-b965-5473163d49c2', 'nickname': 'FanteN-',
                                                        'avatar': 'https://assets.faceit-cdn.net/avatars/fd440a46-2164-41e1-b965-5473163d49c2_1590256788660.jpg',
                                                        'game_id': '76561198118829978', 'game_name': 'Cut The Air', 'game_skill_level': 10, 'membership': '',
                                                        'anticheat_required': True},
                                                       {'id': '738a2f85-c60e-40c6-a944-5d0add94f041', 'nickname': 'otus',
                                                        'avatar': 'https://distribution.faceit-cdn.net/images/7ee393ca-48f3-406e-88ae-7f6bc874119c.jpeg',
                                                        'game_id': '76561199062338256', 'game_name': '< blank >', 'game_skill_level': 10, 'membership': '',
                                                        'anticheat_required': True},
                                                       {'id': 'eebcf20d-1332-466f-b132-57011312cc23', 'nickname': 'lost1769-',
                                                        'avatar': 'https://distribution.faceit-cdn.net/images/e3d3cc7a-e406-4e9d-9fc6-8a8f3c99bd98.jpeg',
                                                        'game_id': '76561199199828610', 'game_name': 'MYSTXRIVL', 'game_skill_level': 10,
                                                        'membership': '', 'anticheat_required': True},
                                                       {'id': '5440b697-1c14-4222-9a6c-85ac9b89a41f', 'nickname': 'Sarnecki',
                                                        'avatar': 'https://assets.faceit-cdn.net/avatars/5440b697-1c14-4222-9a6c-85ac9b89a41f_1550577722507.png',
                                                        'game_id': '76561198049585109', 'game_name': '*Sarnecki|♥Karolina', 'game_skill_level': 10,
                                                        'membership': '', 'anticheat_required': True},
                                                       {'id': '01007cac-59ab-476f-b34d-72995818f043', 'nickname': 'meyerowitz',
                                                        'avatar': 'https://assets.faceit-cdn.net/avatars/01007cac-59ab-476f-b34d-72995818f043_1592528720298.jpg',
                                                        'game_id': '76561197997513588', 'game_name': 'hundertwasser', 'game_skill_level': 10,
                                                        'membership': '', 'anticheat_required': True}], 'substitutions': 0, 'substitutes': None},
                                           {'id': 'c3498b55-97dc-4ae6-9297-0e0045ddaa3a', 'name': 'team_mpd-', 'type': '',
                                            'avatar': 'https://distribution.faceit-cdn.net/images/14de5b23-ef40-49a5-9889-77152d645c53.jpeg',
                                            'leader_id': 'c3498b55-97dc-4ae6-9297-0e0045ddaa3a', 'co_leader_id': '',
                                            'roster': [{'id': '278790a2-1f08-4350-bd96-427f7dcc8722', 'nickname': '-NAPAD',
                                                        'avatar': 'https://assets.faceit-cdn.net/avatars/278790a2-1f08-4350-bd96-427f7dcc8722_1583523957971.jpg',
                                                        'game_id': '76561198061461007', 'game_name': '-NAPAD`11 #ACIDHOUZE', 'game_skill_level': 10,
                                                        'membership': '', 'anticheat_required': True},
                                                       {'id': '0c5783e3-52eb-4c2b-b81d-93ee4805b8d5', 'nickname': 'BAKAAAAAA-',
                                                        'avatar': 'https://assets.faceit-cdn.net/avatars/0c5783e3-52eb-4c2b-b81d-93ee4805b8d5_1629649328411.jpg',
                                                        'game_id': '76561198328266530', 'game_name': 'bakaMASH-', 'game_skill_level': 10,
                                                        'membership': '', 'anticheat_required': True},
                                                       {'id': '852c8fc9-6f4c-430d-b875-4d7c60658c83', 'nickname': 'og_n0nePg3Lu',
                                                        'avatar': '', 'game_id': '76561198016997779', 'game_name': 'Málmhaus',
                                                        'game_skill_level': 10, 'membership': '', 'anticheat_required': True},
                                                       {'id': '6840cd9e-4062-4a7f-90eb-946290a61680', 'nickname': 'RayderT',
                                                        'avatar': 'https://assets.faceit-cdn.net/avatars/6840cd9e-4062-4a7f-90eb-946290a61680_1593039364683.jpg',
                                                        'game_id': '76561198036485109', 'game_name': 'Rayder', 'game_skill_level': 10, 'membership': '',
                                                        'anticheat_required': True},
                                                       {'id': 'c3498b55-97dc-4ae6-9297-0e0045ddaa3a', 'nickname': 'mpd-',
                                                        'avatar': 'https://distribution.faceit-cdn.net/images/14de5b23-ef40-49a5-9889-77152d645c53.jpeg',
                                                        'game_id': '76561198877437783', 'game_name': 'morto por dentro', 'game_skill_level': 10,
                                                        'membership': '', 'anticheat_required': True}], 'substitutions': 0, 'substitutes': None}],
                                 'created_at': '2021-11-22T18:08:25Z', 'updated_at': '2021-11-22T18:45:43Z', 'started_at': '2021-11-22T18:14:57Z', 'finished_at': '2021-11-22T18:45:43Z'}}

stats = {'rounds': [{'best_of': '2', 'competition_id': None, 'game_id': 'csgo', 'game_mode': '5v5',
                     'match_id': '1-d1844336-87fd-4c87-805d-451bb8c32570', 'match_round': '1', 'played': '1',
                     'round_stats': {'Score': '22 / 18', 'Winner': 'ebe8d675-f5b9-49e5-971a-bf846865a7e9', 'Rounds': '40', 'Map': 'de_train', 'Region': 'EU'},
                     'teams': [{'team_id': 'ebe8d675-f5b9-49e5-971a-bf846865a7e9', 'premade': False,
                                'team_stats': {'Second Half Score': '8', 'Team': 'team_KungleBee', 'Team Win': '1',
                                               'Overtime score': '7', 'Team Headshots': '10.6', 'Final Score': '22', 'First Half Score': '7'},
                                'players': [{'player_id': '1e5a3812-12b6-436e-aab7-7d1bc19f215e', 'nickname': 'Jak3yy',
                                             'player_stats': {'Quadro Kills': '0', 'Assists': '7', 'K/D Ratio': '0.85',
                                                              'K/R Ratio': '0.58', 'Result': '1', 'Triple Kills': '2',
                                                              'Headshots': '8', 'MVPs': '5', 'Kills': '23',
                                                              'Penta Kills': '0', 'Headshots %': '35', 'Deaths': '27'}},
                                            {'player_id': '2538e12d-9852-4a0a-b379-3c14244d0556', 'nickname': 'rennyS',
                                             'player_stats': {'Headshots %': '68', 'K/R Ratio': '0.85', 'MVPs': '4',
                                                              'Triple Kills': '2', 'Deaths': '29', 'Headshots': '23',
                                                              'Kills': '34', 'K/D Ratio': '1.17', 'Quadro Kills': '0',
                                                              'Result': '1', 'Assists': '4', 'Penta Kills': '1'}},
                                            {'player_id': '44170d9e-851f-4cb8-8f65-5a8f499abd71', 'nickname': '1Witt',
                                             'player_stats': {'Headshots %': '26', 'Headshots': '10', 'Assists': '3',
                                                              'K/R Ratio': '0.95', 'Triple Kills': '2', 'Result': '1',
                                                              'Deaths': '26', 'Penta Kills': '0', 'Quadro Kills': '2',
                                                              'Kills': '38', 'K/D Ratio': '1.46', 'MVPs': '6'}},
                                            {'player_id': '4a5660d6-e564-4e32-a96d-34b98c1877d7', 'nickname': 'Banelor',
                                             'player_stats': {'MVPs': '1', 'Headshots %': '25', 'Kills': '16',
                                                              'Penta Kills': '0', 'K/D Ratio': '0.59', 'Result': '1',
                                                              'Headshots': '4', 'Assists': '8', 'Deaths': '27',
                                                              'Quadro Kills': '0', 'Triple Kills': '0', 'K/R Ratio': '0.4'}},
                                            {'player_id': 'a548c810-d5aa-4b72-941a-c0c6e40306f6', 'nickname': 'KungleBee',
                                             'player_stats': {'K/R Ratio': '1', 'Result': '1', 'Penta Kills': '0',
                                                              'Kills': '40', 'Triple Kills': '5', 'Assists': '5',
                                                              'K/D Ratio': '1.48', 'Quadro Kills': '0', 'Headshots': '8',
                                                              'Deaths': '27', 'Headshots %': '20', 'MVPs': '6'}}]},
                               {'team_id': 'a549dacf-e548-4060-ab66-30d33a23f9a5', 'premade': False, 'team_stats':
                                   {'First Half Score': '8', 'Second Half Score': '7', 'Team Win': '0',
                                    'Overtime score': '3', 'Team': 'team_TV_Hawk_BLR', 'Team Headshots': '9.2',
                                    'Final Score': '18'}, 'players': [{'player_id': '18e2a663-9e20-4db9-8b29-3c3cbdff30ac',
                                                                       'nickname': 'NoAim_BLR',
                                                                       'player_stats': {
                                                                           'Deaths': '30', 'K/D Ratio': '0.83',
                                                                           'Penta Kills': '0', 'Quadro Kills': '0',
                                                                           'Headshots': '8', 'MVPs': '3', 'Assists': '5',
                                                                           'Result': '0', 'Kills': '25', 'Triple Kills': '0',
                                                                           'Headshots %': '32', 'K/R Ratio': '0.62'}},
                                                                      {'player_id': '278790a2-1f08-4350-bd96-427f7dcc8722',
                                                                       'nickname': '-NAPAD', 'player_stats':
                                                                           {'Quadro Kills': '0', 'Headshots %': '52',
                                                                            'Headshots': '16', 'Triple Kills': '2',
                                                                            'Result': '0', 'Kills': '31', 'Assists': '8',
                                                                            'MVPs': '3', 'Penta Kills': '0', 'K/R Ratio':
                                                                                '0.78', 'Deaths': '31', 'K/D Ratio': '1'}},
                                                                      {'player_id': '8cbb0b36-4c6b-4ebd-a92b-829234016626',
                                                                       'nickname': 'TV_Hawk_BLR', 'player_stats':
                                                                           {'K/R Ratio': '0.7', 'Triple Kills': '1',
                                                                            'K/D Ratio': '0.88', 'Kills': '28', 'Deaths': '32',
                                                                            'Headshots': '9', 'Result': '0', 'Quadro Kills': '0',
                                                                            'MVPs': '5', 'Assists': '5', 'Penta Kills': '0', 'Headshots %': '32'}},
                                                                      {'player_id': 'bb9472c5-4c0b-4f91-b6ff-4101d210bdbd', 'nickname': 'gorkit', 'player_stats':
                                                                          {'Quadro Kills': '1', 'MVPs': '4', 'Kills': '32', 'K/D Ratio': '1.1', 'Assists': '8',
                                                                           'Result': '0', 'Triple Kills': '2', 'Deaths': '29', 'K/R Ratio': '0.8',
                                                                           'Headshots %': '25', 'Headshots': '8', 'Penta Kills': '0'}},
                                                                      {'player_id': 'e1cddcbb-afdc-4e8e-abf2-eea5638f0363', 'nickname': 'DeLPix',
                                                                       'player_stats': {'Kills': '20', 'Assists': '1', 'Result': '0', 'K/R Ratio': '0.5',
                                                                                        'Triple Kills': '0', 'Penta Kills': '0', 'Quadro Kills': '0', 'K/D Ratio': '0.69',
                                                                                        'MVPs': '3', 'Headshots %': '25', 'Headshots': '5', 'Deaths': '29'}}]}]}]}
bo3_stats = {'rounds': [{'best_of': '3', 'competition_id': None, 'game_id': 'csgo', 'game_mode': '5v5', 'match_id': '1-ca834a73-edbc-4348-b07c-1d52f457fc72', 'match_round': '1', 'played': '1', 'round_stats': {'Score': '12 / 16', 'Rounds': '28', 'Region': 'EU', 'Map': 'de_inferno', 'Winner': 'f9146246-c88a-4fd8-a02e-e51dee628357'}, 'teams': [{'team_id': '4eaaceaf-0e19-49fe-9616-99b907e71d08', 'premade': True, 'team_stats': {'Team Headshots': '9.8', 'Overtime score': '0', 'Team': 'Penta Eye', 'Final Score': '12', 'First Half Score': '8', 'Second Half Score': '4', 'Team Win': '0'}, 'players': [{'player_id': '67b15e2f-4d95-4151-9af6-fa5c476c8037', 'nickname': '7oXiK', 'player_stats': {'Headshots': '8', 'Quadro Kills': '0', 'Penta Kills': '0', 'Deaths': '16', 'Result': '0', 'Kills': '15', 'MVPs': '1', 'K/D Ratio': '0.94', 'Headshots %': '53', 'Assists': '3', 'Triple Kills': '0', 'K/R Ratio': '0.54'}}, {'player_id': '220685cd-1a18-4402-a9a9-ac240313cabd', 'nickname': 'XeeDo', 'player_stats': {'MVPs': '4', 'Headshots': '11', 'Kills': '23', 'Assists': '0', 'Headshots %': '48', 'Triple Kills': '1', 'Result': '0', 'Penta Kills': '0', 'Deaths': '22', 'K/D Ratio': '1.05', 'Quadro Kills': '0', 'K/R Ratio': '0.82'}}, {'player_id': '33d7179c-1480-429f-beb7-bb3c2dae2d4e', 'nickname': 'MoonLightttt', 'player_stats': {'Quadro Kills': '0', 'Triple Kills': '0', 'Result': '0', 'Deaths': '19', 'Headshots %': '64', 'K/R Ratio': '0.5', 'K/D Ratio': '0.74', 'Assists': '2', 'MVPs': '3', 'Headshots': '9', 'Kills': '14', 'Penta Kills': '0'}}, {'player_id': 'd1a0fba9-7352-476c-be03-a7babd155f0e', 'nickname': '-kind', 'player_stats': {'Quadro Kills': '0', 'Assists': '2', 'Penta Kills': '0', 'K/R Ratio': '0.57', 'Kills': '16', 'K/D Ratio': '0.76', 'Deaths': '21', 'Headshots %': '31', 'MVPs': '2', 'Result': '0', 'Headshots': '5', 'Triple Kills': '1'}}, {'player_id': 'd0b7218c-a540-423f-960e-f6e9a8b3b10a', 'nickname': '-EcoCobra-', 'player_stats': {'Result': '0', 'Quadro Kills': '2', 'MVPs': '2', 'K/R Ratio': '0.86', 'Deaths': '20', 'K/D Ratio': '1.2', 'Assists': '4', 'Headshots': '16', 'Triple Kills': '0', 'Kills': '24', 'Headshots %': '67', 'Penta Kills': '0'}}]}, {'team_id': 'f9146246-c88a-4fd8-a02e-e51dee628357', 'premade': True, 'team_stats': {'Overtime score': '0', 'Team Win': '1', 'Team Headshots': '8.8', 'Final Score': '16', 'First Half Score': '7', 'Second Half Score': '9', 'Team': 'Neo noir'}, 'players': [{'player_id': '87dcb2d9-e667-49fc-9282-6826751bea3c', 'nickname': 'putjje', 'player_stats': {'Assists': '0', 'Deaths': '17', 'Headshots %': '45', 'MVPs': '6', 'K/R Ratio': '0.71', 'K/D Ratio': '1.18', 'Headshots': '9', 'Triple Kills': '1', 'Penta Kills': '0', 'Result': '1', 'Quadro Kills': '0', 'Kills': '20'}}, {'player_id': 'ad42c90b-45a9-49b6-8ab0-9c8662330543', 'nickname': 'Ayudesee', 'player_stats': {'Triple Kills': '1', 'Result': '1', 'Penta Kills': '0', 'Assists': '4', 'Headshots %': '50', 'Kills': '18', 'Headshots': '9', 'Quadro Kills': '0', 'K/R Ratio': '0.64', 'K/D Ratio': '1', 'MVPs': '1', 'Deaths': '18'}}, {'player_id': '8cbb0b36-4c6b-4ebd-a92b-829234016626', 'nickname': 'TV_Hawk_BLR', 'player_stats': {'K/R Ratio': '0.57', 'Result': '1', 'K/D Ratio': '0.94', 'Triple Kills': '1', 'Deaths': '17', 'Penta Kills': '0', 'MVPs': '4', 'Headshots': '7', 'Quadro Kills': '0', 'Kills': '16', 'Headshots %': '44', 'Assists': '6'}}, {'player_id': '278790a2-1f08-4350-bd96-427f7dcc8722', 'nickname': '-NAPAD', 'player_stats': {'K/R Ratio': '0.86', 'MVPs': '2', 'Quadro Kills': '1', 'Triple Kills': '0', 'Assists': '5', 'Headshots %': '42', 'Kills': '24', 'Penta Kills': '0', 'Deaths': '20', 'Result': '1', 'Headshots': '10', 'K/D Ratio': '1.2'}}, {'player_id': '18e2a663-9e20-4db9-8b29-3c3cbdff30ac', 'nickname': '-MORZY', 'player_stats': {'Headshots %': '45', 'Assists': '8', 'Deaths': '20', 'MVPs': '3', 'Triple Kills': '1', 'K/R Ratio': '0.71', 'Result': '1', 'Penta Kills': '0', 'Kills': '20', 'Quadro Kills': '0', 'Headshots': '9', 'K/D Ratio': '1'}}]}]}, {'best_of': '3', 'competition_id': None, 'game_id': 'csgo', 'game_mode': '5v5', 'match_id': '1-ca834a73-edbc-4348-b07c-1d52f457fc72', 'match_round': '2', 'played': '2', 'round_stats': {'Score': '13 / 16', 'Region': 'EU', 'Map': 'de_overpass', 'Winner': 'f9146246-c88a-4fd8-a02e-e51dee628357', 'Rounds': '29'}, 'teams': [{'team_id': '4eaaceaf-0e19-49fe-9616-99b907e71d08', 'premade': True, 'team_stats': {'Overtime score': '0', 'First Half Score': '10', 'Team': 'Penta Eye', 'Team Headshots': '9.2', 'Second Half Score': '3', 'Team Win': '0', 'Final Score': '13'}, 'players': [{'player_id': '67b15e2f-4d95-4151-9af6-fa5c476c8037', 'nickname': '7oXiK', 'player_stats': {'Triple Kills': '1', 'Result': '0', 'K/R Ratio': '0.83', 'K/D Ratio': '1.26', 'Headshots %': '42', 'Penta Kills': '0', 'Deaths': '19', 'Quadro Kills': '0', 'Kills': '24', 'MVPs': '3', 'Headshots': '10', 'Assists': '1'}}, {'player_id': '220685cd-1a18-4402-a9a9-ac240313cabd', 'nickname': 'XeeDo', 'player_stats': {'Assists': '2', 'K/D Ratio': '0.7', 'Quadro Kills': '0', 'Headshots %': '43', 'MVPs': '1', 'Result': '0', 'Headshots': '6', 'Triple Kills': '0', 'Kills': '14', 'Penta Kills': '0', 'Deaths': '20', 'K/R Ratio': '0.48'}}, {'player_id': '33d7179c-1480-429f-beb7-bb3c2dae2d4e', 'nickname': 'MoonLightttt', 'player_stats': {'Result': '0', 'K/D Ratio': '0.64', 'Headshots': '8', 'K/R Ratio': '0.48', 'Quadro Kills': '0', 'Assists': '3', 'Triple Kills': '0', 'Headshots %': '57', 'Kills': '14', 'Penta Kills': '0', 'MVPs': '3', 'Deaths': '22'}}, {'player_id': 'd1a0fba9-7352-476c-be03-a7babd155f0e', 'nickname': '-kind', 'player_stats': {'MVPs': '5', 'Kills': '28', 'Result': '0', 'Assists': '3', 'Headshots %': '39', 'Headshots': '11', 'Deaths': '22', 'Quadro Kills': '1', 'Triple Kills': '1', 'Penta Kills': '0', 'K/R Ratio': '0.97', 'K/D Ratio': '1.27'}}, {'player_id': 'd0b7218c-a540-423f-960e-f6e9a8b3b10a', 'nickname': '-EcoCobra-', 'player_stats': {'MVPs': '1', 'Deaths': '23', 'Headshots': '11', 'Kills': '22', 'K/D Ratio': '0.96', 'K/R Ratio': '0.76', 'Penta Kills': '0', 'Triple Kills': '1', 'Result': '0', 'Quadro Kills': '0', 'Assists': '4', 'Headshots %': '50'}}]}, {'team_id': 'f9146246-c88a-4fd8-a02e-e51dee628357', 'premade': True, 'team_stats': {'Second Half Score': '11', 'Team Win': '1', 'Final Score': '16', 'Overtime score': '0', 'First Half Score': '5', 'Team': 'Neo noir', 'Team Headshots': '9.2'}, 'players': [{'player_id': '87dcb2d9-e667-49fc-9282-6826751bea3c', 'nickname': 'putjje', 'player_stats': {'Triple Kills': '2', 'Assists': '5', 'Penta Kills': '0', 'K/R Ratio': '0.62', 'K/D Ratio': '0.82', 'Result': '1', 'Quadro Kills': '0', 'MVPs': '3', 'Headshots %': '39', 'Kills': '18', 'Deaths': '22', 'Headshots': '7'}}, {'player_id': 'ad42c90b-45a9-49b6-8ab0-9c8662330543', 'nickname': 'Ayudesee', 'player_stats': {'Assists': '3', 'Headshots %': '33', 'Deaths': '19', 'Result': '1', 'MVPs': '7', 'Quadro Kills': '1', 'Kills': '33', 'K/R Ratio': '1.14', 'K/D Ratio': '1.74', 'Triple Kills': '3', 'Headshots': '11', 'Penta Kills': '0'}}, {'player_id': '8cbb0b36-4c6b-4ebd-a92b-829234016626', 'nickname': 'TV_Hawk_BLR', 'player_stats': {'Assists': '7', 'Headshots %': '62', 'Result': '1', 'K/R Ratio': '0.45', 'MVPs': '1', 'Quadro Kills': '0', 'Triple Kills': '1', 'Penta Kills': '0', 'K/D Ratio': '0.68', 'Headshots': '8', 'Deaths': '19', 'Kills': '13'}}, {'player_id': '278790a2-1f08-4350-bd96-427f7dcc8722', 'nickname': '-NAPAD', 'player_stats': {'Deaths': '22', 'Headshots %': '56', 'K/R Ratio': '0.86', 'Kills': '25', 'Assists': '4', 'Penta Kills': '0', 'Headshots': '14', 'MVPs': '4', 'Result': '1', 'Quadro Kills': '2', 'K/D Ratio': '1.14', 'Triple Kills': '0'}}, {'player_id': '18e2a663-9e20-4db9-8b29-3c3cbdff30ac', 'nickname': '-MORZY', 'player_stats': {'Penta Kills': '0', 'K/D Ratio': '0.85', 'Result': '1', 'Deaths': '20', 'Kills': '17', 'Assists': '2', 'K/R Ratio': '0.59', 'Quadro Kills': '0', 'Headshots %': '35', 'Headshots': '6', 'Triple Kills': '0', 'MVPs': '1'}}]}]}]}
#
# request_json_test = {'transaction_id': '7bf8485f-8a20-42f6-8064-9811d7f63e35', 'event': 'match_status_finished',
#                      'event_id': 'ea136662-02a6-4088-b6a5-8687ac240c2d',
#                      'third_party_id': 'ad42c90b-45a9-49b6-8ab0-9c8662330543',
#                      'app_id': '4ef06a92-08ba-425e-bf12-c49c17d5ec7e', 'timestamp': '2021-04-05T22:28:54Z',
#                      'retry_count': 0, 'version': 1,
#                      'payload': {'id': '1-d1844336-87fd-4c87-805d-451bb8c32570', 'organizer_id': 'faceit',
#                                  'region': 'EU', 'game': 'csgo', 'version': 58,
#                                  'entity': {'id': '42e160fc-2651-4fa5-9a9b-829199e27adb', 'name': 'CS:GO 5v5',
#                                             'type': 'matchmaking'}, 'teams': [
#                              {'id': 'ebe8d675-f5b9-49e5-971a-bf846865a7e9', 'name': 'team_KungleBee', 'type': 'mix',
#                               'avatar': 'https://assets.faceit-cdn.net/avatars/1e5a3812-12b6-436e-aab7-7d1bc19f215e_1550499116087.png',
#                               'leader_id': '1e5a3812-12b6-436e-aab7-7d1bc19f215e', 'co_leader_id': '', 'roster': [
#                                  {'id': '1e5a3812-12b6-436e-aab7-7d1bc19f215e', 'nickname': 'Jak3yy',
#                                   'avatar': 'https://assets.faceit-cdn.net/avatars/1e5a3812-12b6-436e-aab7-7d1bc19f215e_1550499116087.png',
#                                   'game_id': '76561198065782573', 'game_name': 'Jak3y', 'game_skill_level': 10,
#                                   'membership': '', 'anticheat_required': True},
#                                  {'id': '2538e12d-9852-4a0a-b379-3c14244d0556', 'nickname': 'rennyS',
#                                   'avatar': 'https://assets.faceit-cdn.net/avatars/2538e12d-9852-4a0a-b379-3c14244d0556_1591721604651.jpg',
#                                   'game_id': '76561197972418923', 'game_name': 'RennyS', 'game_skill_level': 10,
#                                   'membership': '', 'anticheat_required': True},
#                                  {'id': '44170d9e-851f-4cb8-8f65-5a8f499abd71', 'nickname': '1Witt',
#                                   'avatar': 'https://assets.faceit-cdn.net/avatars/44170d9e-851f-4cb8-8f65-5a8f499abd71_1550496472515.jpg',
#                                   'game_id': '76561198044701092', 'game_name': 'Yoshi', 'game_skill_level': 10,
#                                   'membership': '', 'anticheat_required': True},
#                                  {'id': '4a5660d6-e564-4e32-a96d-34b98c1877d7', 'nickname': 'Banelor',
#                                   'avatar': 'https://assets.faceit-cdn.net/avatars/4a5660d6-e564-4e32-a96d-34b98c1877d7_1550604558060.jpg',
#                                   'game_id': '76561198044262801', 'game_name': 'Mint Green Lips', 'game_skill_level': 7,
#                                   'membership': '', 'anticheat_required': True},
#                                  {'id': 'a548c810-d5aa-4b72-941a-c0c6e40306f6', 'nickname': 'KungleBee',
#                                   'avatar': 'https://assets.faceit-cdn.net/avatars/a548c810-d5aa-4b72-941a-c0c6e40306f6_1616210467076.jpg',
#                                   'game_id': '76561198004012597', 'game_name': 'KungleBee', 'game_skill_level': 10,
#                                   'membership': '', 'anticheat_required': True}], 'substitutions': 0,
#                               'substitutes': None},
#                              {'id': 'a549dacf-e548-4060-ab66-30d33a23f9a5', 'name': 'team_TV_Hawk_BLR', 'type': 'mix',
#                               'avatar': 'https://assets.faceit-cdn.net/avatars/bb9472c5-4c0b-4f91-b6ff-4101d210bdbd_1608862032695.jpg',
#                               'leader_id': 'bb9472c5-4c0b-4f91-b6ff-4101d210bdbd', 'co_leader_id': '', 'roster': [
#                                  {'id': '18e2a663-9e20-4db9-8b29-3c3cbdff30ac', 'nickname': 'NoAim_BLR',
#                                   'avatar': 'https://assets.faceit-cdn.net/avatars/18e2a663-9e20-4db9-8b29-3c3cbdff30ac_1606394549162.jpg',
#                                   'game_id': '76561198182169775', 'game_name': '✪ EXCLUS1VE', 'game_skill_level': 9,
#                                   'membership': '', 'anticheat_required': True},
#                                  {'id': '278790a2-1f08-4350-bd96-427f7dcc8722', 'nickname': '-NAPAD',
#                                   'avatar': 'https://assets.faceit-cdn.net/avatars/278790a2-1f08-4350-bd96-427f7dcc8722_1583523957971.jpg',
#                                   'game_id': '76561198061461007', 'game_name': '-NAPAD`11 #ACIDHOUZE',
#                                   'game_skill_level': 10, 'membership': '', 'anticheat_required': True},
#                                  {'id': '8cbb0b36-4c6b-4ebd-a92b-829234016626', 'nickname': 'TV_Hawk_BLR',
#                                   'avatar': 'https://assets.faceit-cdn.net/avatars/8cbb0b36-4c6b-4ebd-a92b-829234016626_1616327629470.jpg',
#                                   'game_id': '76561198940708592', 'game_name': 'twitch.tv/hawk_blr',
#                                   'game_skill_level': 10, 'membership': '', 'anticheat_required': True},
#                                  {'id': 'bb9472c5-4c0b-4f91-b6ff-4101d210bdbd', 'nickname': 'gorkit',
#                                   'avatar': 'https://assets.faceit-cdn.net/avatars/bb9472c5-4c0b-4f91-b6ff-4101d210bdbd_1608862032695.jpg',
#                                   'game_id': '76561198052084433', 'game_name': 'gorkit', 'game_skill_level': 10,
#                                   'membership': '', 'anticheat_required': True},
#                                  {'id': 'e1cddcbb-afdc-4e8e-abf2-eea5638f0363', 'nickname': 'DeLPix',
#                                   'avatar': 'https://assets.faceit-cdn.net/avatars/e1cddcbb-afdc-4e8e-abf2-eea5638f0363_1609000282402.jpg',
#                                   'game_id': '76561198129814795', 'game_name': 'dlp1x', 'game_skill_level': 8,
#                                   'membership': '', 'anticheat_required': True}], 'substitutions': 0,
#                               'substitutes': None}], 'created_at': '2021-04-05T21:18:53Z',
#                                  'updated_at': '2021-04-05T22:28:53Z', 'started_at': '2021-04-05T21:24:35Z',
#                                  'finished_at': '2021-04-05T22:28:53Z'}}

font_folder = 'outfit'
font_file = 'Outfit-SemiBold.ttf'
font_file_mainscore = 'Outfit-ExtraBold.ttf'


font_avs = ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file}', 18)
font_mainscore = ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file_mainscore}', 50)
font_player_score = ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file}', 32)
font_player_stats = ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file}', 22)
font_halftimes = ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file}', 22)

dark_avatar_bot = Image.open('templates/background_features/for_avatar_bot.png')
faceit = Image.open('templates/faceit_icons/faceit1.png').convert("RGBA")
steam_question = Image.open('templates/question-mark-icon.jpg')
steam_question = steam_question.resize((130, 130))
dark_avatar_top= Image.open('templates/background_features/for_avatar_top.png')
for idx_round, round in enumerate(stats['rounds']):
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
    for idx_team, team in enumerate(round['teams']):
        if 'Overtime score' in team['team_stats'].keys():
            halftimes = f"{team['team_stats']['First Half Score']}—{team['team_stats']['Second Half Score']}—{team['team_stats']['Overtime score']}"
            draw.text((25, 235 + 50 * idx_team), halftimes, font=font_halftimes)
        else:
            halftimes = f"{team['team_stats']['First Half Score']}—{team['team_stats']['Second Half Score']}"
            draw.text((33, 235 + 50 * idx_team), halftimes, font=font_halftimes)
        for idx_player, player in enumerate(team['players']):
            if request_json_test['payload']['teams'][idx_team]['roster'][idx_player]['avatar']:
                avatar_req = requests.get(request_json_test['payload']['teams'][idx_team]['roster'][idx_player]['avatar'], stream=True)
                avatar_img = Image.open(avatar_req.raw)
                avatar_img = avatar_img.resize((130, 130))
            else:
                avatar_img = steam_question
            faceitlvl = request_json_test['payload']['teams'][idx_team]['roster'][idx_player]['game_skill_level']
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

            w, h = draw.textsize(request_json_test['payload']['teams'][idx_team]['roster'][idx_player]['nickname'], font=font_avs)
            if w > 130:
                draw_avatar.text((0, 107 - idx_team * 107), request_json_test['payload']['teams'][idx_team]['roster'][idx_player]['nickname'], font=font_avs)
            else:
                draw_avatar.text(((130 - w) / 2, 107 - idx_team * 107), request_json_test['payload']['teams'][idx_team]['roster'][idx_player]['nickname'], font=font_avs)

            img1.paste(steam_question, (146 + idx_player * 162, 20 + 370 * idx_team))
            img1.paste(avatar_img, (146 + idx_player * 162, 20 + 370 * idx_team))

            kad = f'{player["player_stats"]["Kills"]}/{player["player_stats"]["Assists"]}/{player["player_stats"]["Deaths"]}'
            w, h = draw.textsize(kad, font=font_player_score)
            draw.text((130 + (162 - w) / 2 + idx_player * 162, 155 + 195 * idx_team), kad, font=font_player_score)
            mvp = f'MVP: {player["player_stats"]["MVPs"]}'
            draw.text((146 + idx_player * 162, 200 + 116 * idx_team), mvp, font=font_player_stats)
            kr = f'K/R: {player["player_stats"]["K/R Ratio"]}'
            draw.text((146 + idx_player * 162, 220 + 76 * idx_team), kr, font=font_player_stats)
            hs = f'HS %: {player["player_stats"]["Headshots %"]}'
            draw.text((146 + idx_player * 162, 240 + 36 * idx_team), hs, font=font_player_stats)

    w, h = draw.textsize(round["teams"][0]["team_stats"]["Final Score"], font=font_mainscore)
    draw.text(((146 - w) / 2, 65), round["teams"][0]["team_stats"]["Final Score"], font=font_mainscore)
    w, h = draw.textsize(round["teams"][1]["team_stats"]["Final Score"], font=font_mainscore)
    draw.text(((146 - w) / 2, 425), round["teams"][1]["team_stats"]["Final Score"], font=font_mainscore)

    img1.show()

# image_list = collect_image(request_json_test, stats)
# for image in image_list:
#     image.show()