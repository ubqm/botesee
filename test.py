import os

import discord
from discord import Client
import io
from PIL import Image, ImageFont
from imageCollector import collect_image
from io import BytesIO

request_json = {'transaction_id': 'aab7fe07-9433-457b-8ac7-8793a804196c', 'event': 'match_status_finished',
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

Discord_token = os.environ['Discord_token']


class MyClient(discord.Client):
    async def on_ready(self):
        for guild in self.guilds:
            print(f'Logged on as {self.user}, server: {guild.name}, guild_id:{guild.id}')
            channel = Client.get_channel(self, 828940900033626113)
            messages = await channel.history(limit=10).flatten()

            for message in messages:
                if message.embeds:
                    if request_json['payload']['id'] in message.embeds[0].description:
                        print(request_json['payload']['id'] + 'found')
                        break
        channel = self.get_channel(id=828940900033626113)

        # image = Image.open("default.png")
        # with io.BytesIO() as image_binary:
        #     image.save(image_binary, 'PNG')
        #     image_binary.seek(0)
        #     # await channel.send(
        #     #     'https://www.faceit.com/en/csgo/room/{0}'.format('1-6672c059-bfbf-48f3-a6d6-8e8fddd2a5e3'))
        #     await channel.send('message', file=discord.File(fp=image_binary, filename='image.png'))
        str_nick = ''
        for team in stats['rounds'][0]['teams']:
            for player in team['players']:
                str_nick += '{}, '.format(player['nickname'])
        str_nick = str_nick[:-2]

        embed_msg = discord.Embed(title=str_nick, type="rich",
                                  description='[{0}](https://www.faceit.com/en/csgo/room/{1})'.format(
                                      stats['rounds'][0]['round_stats']['Map'], request_json['payload']['id']),
                                  color=1)
        embed_msg.add_field(name=request_json['payload']['teams'][0]['name'], value='nick1', inline=True)
        embed_msg.add_field(name='ELO', value='value1', inline=True)
        embed_msg.add_field(name='\u200b', value='\u200b')
        embed_msg.add_field(name=request_json['payload']['teams'][1]['name'], value='str_nick2', inline=True)
        embed_msg.add_field(name='ELO', value='elo2', inline=True)
        embed_msg.add_field(name='\u200b', value='\u200b')
        print(embed_msg.fields[0])
        print(embed_msg.fields[1])
        print(embed_msg.fields[2])
        await channel.send(embed=embed_msg)

    async def delete_message_by_faceit_match_id(self, match_id):
        channel = Client.get_channel(self, 828940900033626113)
        messages = await channel.history(limit=10).flatten()
        for message in messages:
            if message.embeds:
                if match_id in message.embeds[0].description:
                    await message.delete()
                    break


def main():
    intents = discord.Intents.all()
    bot_client = MyClient(intents=intents)
    bot_client.run(Discord_token)


if __name__ == '__main__':
    main()
