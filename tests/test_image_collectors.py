import asyncio
import os
import aiohttp
from env_variables import faceit_headers
from api_funcs.async_faceit_get_funcs import match_stats
from ImageCollectors.ImageCollectorMatchFinished import ImageCollectorMatchFinished
from ImageCollectors.ImageCollectorStatLast import ImageCollectorStatLast
from ImageCollectors.ImageCollectorCompare import ImageCollectorCompare


async def mf():
    request_json = {'transaction_id': '47c8ade3-db36-4c0a-8471-7c340e9d7ac8', 'event': 'match_status_finished',
                    'event_id': '6db8bfa8-0bbc-4a19-88b1-ea93ae8e3005',
                    'third_party_id': 'ad42c90b-45a9-49b6-8ab0-9c8662330543',
                    'app_id': '4ef06a92-08ba-425e-bf12-c49c17d5ec7e', 'timestamp': '2022-01-10T20:29:35Z',
                    'retry_count': 0, 'version': 1,
                    'payload': {'id': '1-37a40c85-82ae-436d-9f90-fb7db5484033', 'organizer_id': 'faceit',
                                'region': 'EU', 'game': 'csgo', 'version': 43,
                                'entity': {'id': 'a3c75828-7f0f-4940-adb9-994b4b389070', 'name': 'CS:GO 5v5 PREMIUM',
                                           'type': 'matchmaking'}, 'teams': [
                            {'id': '8d5ead5d-b1b6-458d-93d0-1a0548d2de3f', 'name': 'team_CJ-2k', 'type': '',
                             'avatar': 'https://distribution.faceit-cdn.net/images/3911c173-368e-4dbd-8b1f-b0d19ade695a.jpeg',
                             'leader_id': '8d5ead5d-b1b6-458d-93d0-1a0548d2de3f', 'co_leader_id': '', 'roster': [
                                {'id': '278790a2-1f08-4350-bd96-427f7dcc8722', 'nickname': '-NAPAD',
                                 'avatar': 'https://assets.faceit-cdn.net/avatars/278790a2-1f08-4350-bd96-427f7dcc8722_1583523957971.jpg',
                                 'game_id': '76561198061461007', 'game_name': '-NAPAD`11 #ACIDHOUZE',
                                 'game_skill_level': 10, 'membership': '', 'anticheat_required': True},
                                {'id': 'd0b7218c-a540-423f-960e-f6e9a8b3b10a', 'nickname': '-EcoCobra-',
                                 'avatar': 'https://assets.faceit-cdn.net/avatars/d0b7218c-a540-423f-960e-f6e9a8b3b10a_1633631507859.jpg',
                                 'game_id': '76561198391731293', 'game_name': 'yowai mo', 'game_skill_level': 10,
                                 'membership': '', 'anticheat_required': True},
                                {'id': '6dc2d3a1-8653-4ce6-8a2c-cb30122361e8', 'nickname': 'S1non--',
                                 'avatar': 'https://distribution.faceit-cdn.net/images/72491042-bdd6-4fc5-a8ba-e7fea300ac88.jpeg',
                                 'game_id': '76561198251305342', 'game_name': 'S1non', 'game_skill_level': 10,
                                 'membership': '', 'anticheat_required': True},
                                {'id': '131b67d6-3e3a-4a79-a4bc-7d73ea404c8e', 'nickname': 'Deokishisu',
                                 'avatar': 'https://distribution.faceit-cdn.net/images/110c80b9-1f38-4426-9429-d6edeaa150c1.jpeg',
                                 'game_id': '76561199174381757', 'game_name': 'xGOD', 'game_skill_level': 10,
                                 'membership': '', 'anticheat_required': True},
                                {'id': '8d5ead5d-b1b6-458d-93d0-1a0548d2de3f', 'nickname': 'CJ-2k',
                                 'avatar': 'https://distribution.faceit-cdn.net/images/3911c173-368e-4dbd-8b1f-b0d19ade695a.jpeg',
                                 'game_id': '76561199006885634', 'game_name': 'asd', 'game_skill_level': 10,
                                 'membership': '', 'anticheat_required': True}], 'substitutions': 0,
                             'substitutes': None},
                            {'id': 'f8580374-5c09-43bc-bef2-463f1fde9aff', 'name': 'team_sinnopsyy', 'type': '',
                             'avatar': 'https://distribution.faceit-cdn.net/images/62a8416a-7cba-44b9-bab6-c5430f992eb9.jpeg',
                             'leader_id': 'f8580374-5c09-43bc-bef2-463f1fde9aff', 'co_leader_id': '', 'roster': [
                                {'id': 'f8580374-5c09-43bc-bef2-463f1fde9aff', 'nickname': 'sinnopsyy',
                                 'avatar': 'https://distribution.faceit-cdn.net/images/62a8416a-7cba-44b9-bab6-c5430f992eb9.jpeg',
                                 'game_id': '76561198165327895', 'game_name': 'sinnopsy=D', 'game_skill_level': 10,
                                 'membership': '', 'anticheat_required': True},
                                {'id': '440c0bf9-028a-4234-932c-3cb53e285851', 'nickname': 'katNine',
                                 'avatar': 'https://distribution.faceit-cdn.net/images/c44d20cc-b2aa-4129-a9d4-5bbeb382d42e.jpeg',
                                 'game_id': '76561198025532625', 'game_name': 'k', 'game_skill_level': 10,
                                 'membership': '', 'anticheat_required': True},
                                {'id': '1b4e291a-c1c9-48c1-8738-5fda9a109151', 'nickname': 'Coopah-iwnl-',
                                 'avatar': 'https://assets.faceit-cdn.net/avatars/1b4e291a-c1c9-48c1-8738-5fda9a109151_1626554809867.jpg',
                                 'game_id': '76561198137616643', 'game_name': 'I only frag when im on drugs❤',
                                 'game_skill_level': 10, 'membership': '', 'anticheat_required': True},
                                {'id': 'e284326a-04c2-41b2-8e1b-851e9b5f9761', 'nickname': '-ReGnZ-',
                                 'avatar': 'https://assets.faceit-cdn.net/avatars/e284326a-04c2-41b2-8e1b-851e9b5f9761_1550964104764.jpg',
                                 'game_id': '76561198070260050', 'game_name': 'ReGnZ', 'game_skill_level': 10,
                                 'membership': '', 'anticheat_required': True},
                                {'id': '0b21055e-a2a6-4a4e-a1b8-3691352ce8f5', 'nickname': 'faqazy',
                                 'avatar': 'https://distribution.faceit-cdn.net/images/49e275b8-c2e7-419b-a0dc-389dc21d7166.jpeg',
                                 'game_id': '76561198799957222', 'game_name': '᠌ ᠌ ᠌᠌ ᠌ ᠌ ᠌ ᠌', 'game_skill_level': 10,
                                 'membership': '', 'anticheat_required': True}], 'substitutions': 0,
                             'substitutes': None}], 'created_at': '2022-01-10T19:46:45Z',
                                'updated_at': '2022-01-10T20:29:35Z', 'started_at': '2022-01-10T19:51:43Z',
                                'finished_at': '2022-01-10T20:29:35Z'}}
    async with aiohttp.ClientSession(headers=faceit_headers) as session:
        stat_json = await match_stats(session, request_json['payload']['id'])
    imc = ImageCollectorMatchFinished(request_json, stat_json, "-NAPAD\n-EcoCobra-\nS1non--\nDeokishisu\nCJ-2k",
                                      '2946\n2229\n2954\n2065\n2238',
                                      "sinnopsyy\nkatNine\nCoopah-iwnl-\n-ReGnZ-\nfaqazy",
                                      "3440\n2136\n1774\n1384\n3621")
    imgl = await imc.collect_image()
    if imgl:
        return True


async def sl():
    imgclst = ImageCollectorStatLast("-NAPAD")
    image = await imgclst.collect_image()
    if image:
        return True


async def cmp():
    imgcmpr = ImageCollectorCompare("Ayudesee", "-NAPAD", "10", "games")
    image = await imgcmpr.collect_image()
    if image:
        return True


async def main():
    print(await cmp())
    print(await sl())
    print(await mf())


async def test_image_collectors():
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    task_cmp = asyncio.create_task(cmp())
    task_sl = asyncio.create_task(sl())
    task_mf = asyncio.create_task(mf())
    res_cmp = await task_cmp
    res_sl = await task_sl
    res_mf = await task_mf
    assert res_cmp is True
    assert res_sl is True
    assert res_mf is True
