import discord
import os

from io import BytesIO
from imageCollector import collect_image
from faceit_get_funcs import match_stats
from IPython.terminal.pt_inputhooks.asyncio import loop
from discord import Client
from flask import Flask, request, Response
from threading import Thread
from functools import partial

TOKEN = ''
with open('token.txt', 'r') as file:
    TOKEN = file.read()

app = Flask(__name__)
json_test = {'rounds': [{'best_of': '2', 'competition_id': None, 'game_id': 'csgo', 'game_mode': '5v5',
                         'match_id': '1-d1844336-87fd-4c87-805d-451bb8c32570', 'match_round': '1', 'played': '1',
                         'round_stats': {'Region': 'EU', 'Rounds': '40',
                                         'Winner': 'ebe8d675-f5b9-49e5-971a-bf846865a7e9', 'Score': '22 / 18',
                                         'Map': 'de_train'}, 'teams': [
        {'team_id': 'ebe8d675-f5b9-49e5-971a-bf846865a7e9', 'premade': False,
         'team_stats': {'Team': 'team_KungleBee', 'Team Headshots': '10.6', 'Final Score': '22', 'Overtime score': '7',
                        'First Half Score': '7', 'Second Half Score': '8', 'Team Win': '1'}, 'players': [
            {'player_id': '1e5a3812-12b6-436e-aab7-7d1bc19f215e', 'nickname': 'Jak3yy',
             'player_stats': {'Penta Kills': '0', 'Headshots': '8', 'Triple Kills': '2', 'Result': '1',
                              'Quadro Kills': '0', 'Deaths': '27', 'K/R Ratio': '0.58', 'Assists': '7', 'Kills': '23',
                              'Headshots %': '35', 'MVPs': '5', 'K/D Ratio': '0.85'}},
            {'player_id': '2538e12d-9852-4a0a-b379-3c14244d0556', 'nickname': 'rennyS',
             'player_stats': {'Triple Kills': '2', 'Penta Kills': '1', 'K/D Ratio': '1.17', 'Deaths': '29',
                              'K/R Ratio': '0.85', 'Headshots': '23', 'Quadro Kills': '0', 'Kills': '34',
                              'Headshots %': '68', 'Assists': '4', 'MVPs': '4', 'Result': '1'}},
            {'player_id': '44170d9e-851f-4cb8-8f65-5a8f499abd71', 'nickname': '1Witt',
             'player_stats': {'Result': '1', 'Quadro Kills': '2', 'Triple Kills': '2', 'Kills': '38', 'Assists': '3',
                              'Headshots': '10', 'Deaths': '26', 'K/R Ratio': '0.95', 'MVPs': '6', 'Headshots %': '26',
                              'Penta Kills': '0', 'K/D Ratio': '1.46'}},
            {'player_id': '4a5660d6-e564-4e32-a96d-34b98c1877d7', 'nickname': 'Banelor',
             'player_stats': {'Deaths': '27', 'Result': '1', 'Assists': '8', 'Penta Kills': '0', 'K/R Ratio': '0.4',
                              'Kills': '16', 'Triple Kills': '0', 'Headshots': '4', 'MVPs': '1', 'Headshots %': '25',
                              'K/D Ratio': '0.59', 'Quadro Kills': '0'}},
            {'player_id': 'a548c810-d5aa-4b72-941a-c0c6e40306f6', 'nickname': 'KungleBee',
             'player_stats': {'K/R Ratio': '1', 'Assists': '5', 'MVPs': '6', 'Quadro Kills': '0', 'K/D Ratio': '1.48',
                              'Headshots %': '20', 'Result': '1', 'Triple Kills': '5', 'Penta Kills': '0',
                              'Kills': '40', 'Deaths': '27', 'Headshots': '8'}}]},
        {'team_id': 'a549dacf-e548-4060-ab66-30d33a23f9a5', 'premade': False,
         'team_stats': {'Team Headshots': '9.2', 'Final Score': '18', 'Second Half Score': '7', 'First Half Score': '8',
                        'Team Win': '0', 'Overtime score': '3', 'Team': 'team_TV_Hawk_BLR'}, 'players': [
            {'player_id': '18e2a663-9e20-4db9-8b29-3c3cbdff30ac', 'nickname': 'NoAim_BLR',
             'player_stats': {'Headshots': '8', 'Deaths': '30', 'Penta Kills': '0', 'Result': '0', 'MVPs': '3',
                              'K/R Ratio': '0.62', 'Headshots %': '32', 'Kills': '25', 'Triple Kills': '0',
                              'K/D Ratio': '0.83', 'Assists': '5', 'Quadro Kills': '0'}},
            {'player_id': '278790a2-1f08-4350-bd96-427f7dcc8722', 'nickname': '-NAPAD',
             'player_stats': {'Triple Kills': '2', 'Deaths': '31', 'Headshots': '16', 'Assists': '8',
                              'K/R Ratio': '0.78', 'Result': '0', 'Headshots %': '52', 'Quadro Kills': '0', 'MVPs': '3',
                              'Kills': '31', 'Penta Kills': '0', 'K/D Ratio': '1'}},
            {'player_id': '8cbb0b36-4c6b-4ebd-a92b-829234016626', 'nickname': 'TV_Hawk_BLR',
             'player_stats': {'K/D Ratio': '0.88', 'Result': '0', 'Headshots': '9', 'Triple Kills': '1',
                              'Headshots %': '32', 'Assists': '5', 'Kills': '28', 'Quadro Kills': '0', 'Deaths': '32',
                              'K/R Ratio': '0.7', 'MVPs': '5', 'Penta Kills': '0'}},
            {'player_id': 'bb9472c5-4c0b-4f91-b6ff-4101d210bdbd', 'nickname': 'gorkit',
             'player_stats': {'MVPs': '4', 'K/D Ratio': '1.1', 'K/R Ratio': '0.8', 'Result': '0', 'Kills': '32',
                              'Assists': '8', 'Headshots': '8', 'Deaths': '29', 'Headshots %': '25', 'Penta Kills': '0',
                              'Triple Kills': '2', 'Quadro Kills': '1'}},
            {'player_id': 'e1cddcbb-afdc-4e8e-abf2-eea5638f0363', 'nickname': 'DeLPix',
             'player_stats': {'Penta Kills': '0', 'K/R Ratio': '0.5', 'Result': '0', 'Triple Kills': '0',
                              'Assists': '1', 'K/D Ratio': '0.69', 'MVPs': '3', 'Headshots %': '25',
                              'Quadro Kills': '0', 'Deaths': '29', 'Kills': '20', 'Headshots': '5'}}]}]}]}
request_json_test = {'transaction_id': '7bf8485f-8a20-42f6-8064-9811d7f63e35', 'event': 'match_status_finished',
                     'event_id': 'ea136662-02a6-4088-b6a5-8687ac240c2d',
                     'third_party_id': 'ad42c90b-45a9-49b6-8ab0-9c8662330543',
                     'app_id': '4ef06a92-08ba-425e-bf12-c49c17d5ec7e', 'timestamp': '2021-04-05T22:28:54Z',
                     'retry_count': 0, 'version': 1,
                     'payload': {'id': '1-d1844336-87fd-4c87-805d-451bb8c32570', 'organizer_id': 'faceit',
                                 'region': 'EU', 'game': 'csgo', 'version': 58,
                                 'entity': {'id': '42e160fc-2651-4fa5-9a9b-829199e27adb', 'name': 'CS:GO 5v5',
                                            'type': 'matchmaking'}, 'teams': [
                             {'id': 'ebe8d675-f5b9-49e5-971a-bf846865a7e9', 'name': 'team_KungleBee', 'type': 'mix',
                              'avatar': 'https://assets.faceit-cdn.net/avatars/1e5a3812-12b6-436e-aab7-7d1bc19f215e_1550499116087.png',
                              'leader_id': '1e5a3812-12b6-436e-aab7-7d1bc19f215e', 'co_leader_id': '', 'roster': [
                                 {'id': '1e5a3812-12b6-436e-aab7-7d1bc19f215e', 'nickname': 'Jak3yy',
                                  'avatar': 'https://assets.faceit-cdn.net/avatars/1e5a3812-12b6-436e-aab7-7d1bc19f215e_1550499116087.png',
                                  'game_id': '76561198065782573', 'game_name': 'Jak3y', 'game_skill_level': 10,
                                  'membership': '', 'anticheat_required': True},
                                 {'id': '2538e12d-9852-4a0a-b379-3c14244d0556', 'nickname': 'rennyS',
                                  'avatar': 'https://assets.faceit-cdn.net/avatars/2538e12d-9852-4a0a-b379-3c14244d0556_1591721604651.jpg',
                                  'game_id': '76561197972418923', 'game_name': 'RennyS', 'game_skill_level': 10,
                                  'membership': '', 'anticheat_required': True},
                                 {'id': '44170d9e-851f-4cb8-8f65-5a8f499abd71', 'nickname': '1Witt',
                                  'avatar': 'https://assets.faceit-cdn.net/avatars/44170d9e-851f-4cb8-8f65-5a8f499abd71_1550496472515.jpg',
                                  'game_id': '76561198044701092', 'game_name': 'Yoshi', 'game_skill_level': 10,
                                  'membership': '', 'anticheat_required': True},
                                 {'id': '4a5660d6-e564-4e32-a96d-34b98c1877d7', 'nickname': 'Banelor',
                                  'avatar': 'https://assets.faceit-cdn.net/avatars/4a5660d6-e564-4e32-a96d-34b98c1877d7_1550604558060.jpg',
                                  'game_id': '76561198044262801', 'game_name': 'Mint Green Lips', 'game_skill_level': 7,
                                  'membership': '', 'anticheat_required': True},
                                 {'id': 'a548c810-d5aa-4b72-941a-c0c6e40306f6', 'nickname': 'KungleBee',
                                  'avatar': 'https://assets.faceit-cdn.net/avatars/a548c810-d5aa-4b72-941a-c0c6e40306f6_1616210467076.jpg',
                                  'game_id': '76561198004012597', 'game_name': 'KungleBee', 'game_skill_level': 10,
                                  'membership': '', 'anticheat_required': True}], 'substitutions': 0,
                              'substitutes': None},
                             {'id': 'a549dacf-e548-4060-ab66-30d33a23f9a5', 'name': 'team_TV_Hawk_BLR', 'type': 'mix',
                              'avatar': 'https://assets.faceit-cdn.net/avatars/bb9472c5-4c0b-4f91-b6ff-4101d210bdbd_1608862032695.jpg',
                              'leader_id': 'bb9472c5-4c0b-4f91-b6ff-4101d210bdbd', 'co_leader_id': '', 'roster': [
                                 {'id': '18e2a663-9e20-4db9-8b29-3c3cbdff30ac', 'nickname': 'NoAim_BLR',
                                  'avatar': 'https://assets.faceit-cdn.net/avatars/18e2a663-9e20-4db9-8b29-3c3cbdff30ac_1606394549162.jpg',
                                  'game_id': '76561198182169775', 'game_name': '✪ EXCLUS1VE', 'game_skill_level': 9,
                                  'membership': '', 'anticheat_required': True},
                                 {'id': '278790a2-1f08-4350-bd96-427f7dcc8722', 'nickname': '-NAPAD',
                                  'avatar': 'https://assets.faceit-cdn.net/avatars/278790a2-1f08-4350-bd96-427f7dcc8722_1583523957971.jpg',
                                  'game_id': '76561198061461007', 'game_name': '-NAPAD`11 #ACIDHOUZE',
                                  'game_skill_level': 10, 'membership': '', 'anticheat_required': True},
                                 {'id': '8cbb0b36-4c6b-4ebd-a92b-829234016626', 'nickname': 'TV_Hawk_BLR',
                                  'avatar': 'https://assets.faceit-cdn.net/avatars/8cbb0b36-4c6b-4ebd-a92b-829234016626_1616327629470.jpg',
                                  'game_id': '76561198940708592', 'game_name': 'twitch.tv/hawk_blr',
                                  'game_skill_level': 10, 'membership': '', 'anticheat_required': True},
                                 {'id': 'bb9472c5-4c0b-4f91-b6ff-4101d210bdbd', 'nickname': 'gorkit',
                                  'avatar': 'https://assets.faceit-cdn.net/avatars/bb9472c5-4c0b-4f91-b6ff-4101d210bdbd_1608862032695.jpg',
                                  'game_id': '76561198052084433', 'game_name': 'gorkit', 'game_skill_level': 10,
                                  'membership': '', 'anticheat_required': True},
                                 {'id': 'e1cddcbb-afdc-4e8e-abf2-eea5638f0363', 'nickname': 'DeLPix',
                                  'avatar': 'https://assets.faceit-cdn.net/avatars/e1cddcbb-afdc-4e8e-abf2-eea5638f0363_1609000282402.jpg',
                                  'game_id': '76561198129814795', 'game_name': 'dlp1x', 'game_skill_level': 8,
                                  'membership': '', 'anticheat_required': True}], 'substitutions': 0,
                              'substitutes': None}], 'created_at': '2021-04-05T21:18:53Z',
                                 'updated_at': '2021-04-05T22:28:53Z', 'started_at': '2021-04-05T21:24:35Z',
                                 'finished_at': '2021-04-05T22:28:53Z'}}


@app.route('/', methods=['GET'])
def respond_default_get():
    # для тестов на своей машине
    # loop.create_task(
    #     bot_client.post_faceit_test_finished(channel_id=828940900033626113, request_json=request_json_test))
    return Response(status=200)


@app.route('/match_status_ready', methods=['POST'])
def respond_status_ready():
    print(request.json)
    loop.create_task(bot_client.post_faceit_message_ready(channel_id=828940900033626113, request_json=request.json))
    print('respond match_status_ready function called')
    return Response(status=200)


@app.route('/match_status_finished', methods=['POST'])
def respond_status_finished():
    print(request.json)
    loop.create_task(bot_client.post_faceit_message_finished(channel_id=828940900033626113, request_json=request.json))
    print('respond match_status_finished function called')
    return Response(status=200)


@app.route('/match_status_aborted', methods=['POST'])
def respond_status_aborted():
    print(request.json)
    loop.create_task(bot_client.post_faceit_message_aborted(channel_id=828940900033626113, request_json=request.json))
    print('respond match_status_aborted function called')
    return Response(status=200)


class MyClient(discord.Client):
    roles_that_cant_vote = ['@everyone']

    async def on_ready(self):
        for guild in self.guilds:
            print(f'Logged on as {self.user}, server: {guild.name}, guild_id:{guild.id}')

    async def on_message(self, message):
        print(f'New message from {message.author}: {message.content}')
        if message.author.id != 825393722186924112:
            if message.attachments or message.embeds or (message.content.find('https://') != -1) or (
                    message.content.find('http://') != -1):
                await message.add_reaction('👍')
                await message.add_reaction('👎')

    async def on_raw_reaction_add(self, payload):
        upvotes = 0
        downvotes = 0
        users_upvote = []
        users_downvote = []
        if payload.emoji.name == '👍' or payload.emoji.name == '👎':
            print(payload)
            channel = Client.get_channel(self, payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            print(
                f'Emoji {payload.emoji} added by:{payload.member}, Message by: {message.author}, Message: {message.content}')

            for _ in message.reactions:
                if _.emoji == '👍':
                    users_upvote = await _.users().flatten()
                elif _.emoji == '👎':
                    users_downvote = await _.users().flatten()

            for user in users_upvote:
                for role in user.roles:
                    if role.name != '@everyone':
                        upvotes += 1
                        break

            for user in users_downvote:
                for role in user.roles:
                    if role.name != '@everyone':
                        downvotes += 1
                        break

            print(f'Upvotes/Downvotes = {upvotes}/{downvotes}')
            if upvotes < downvotes - 2:
                await message.delete()
                print(
                    f'*** Message "{message.content}" deleted with {upvotes} Upvotes, {downvotes} Downvotes, message_id:{message.id}')
            print(' ')

    async def on_raw_reaction_remove(self, payload):
        upvotes = 0
        downvotes = 0
        users_upvote = []
        users_downvote = []
        if payload.emoji.name == '👍' or payload.emoji.name == '👎':
            print(payload)
            channel = Client.get_channel(self, payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            print(
                f'Emoji {payload.emoji} removed by:{payload.member}, Message by: {message.author}, Message: {message.content}')

            for _ in message.reactions:
                if _.emoji == '👍':
                    users_upvote = await _.users().flatten()
                elif _.emoji == '👎':
                    users_downvote = await _.users().flatten()

            for user in users_upvote:
                for role in user.roles:
                    if role.name != '@everyone':
                        upvotes += 1
                        break

            for user in users_downvote:
                for role in user.roles:
                    if role.name != '@everyone':
                        downvotes += 1
                        break

            print(f'Upvotes/Downvotes = {upvotes}/{downvotes}')
            if upvotes < downvotes - 2:
                await message.delete()
                print(
                    f'*** Message "{message.content}" deleted with {upvotes} Upvotes, {downvotes} Downvotes, message_id:{message.id}')
            print(' ')

    async def post_faceit_message_ready(self, channel_id, request_json):
        channel = self.get_channel(id=channel_id)
        my_color = 9936031
        embed_msg = discord.Embed(title="Match Ready", type="rich",
                                  description='[{0}](https://www.faceit.com/en/csgo/room/{1})'.format(
                                      request_json['payload']['id'], request_json['payload']['id']),
                                  color=my_color)
        str_nick1 = ''
        str_nick2 = ''

        for player in range(0, 5):
            str_nick1 += str(request_json['payload']['teams'][0]['roster'][player]['nickname']) + '\n'
            str_nick2 += str(request_json['payload']['teams'][1]['roster'][player]['nickname']) + '\n'

        embed_msg.add_field(name=request_json['payload']['teams'][0]['name'], value=str_nick1, inline=True)
        embed_msg.add_field(name=request_json['payload']['teams'][1]['name'], value=str_nick2, inline=True)
        await channel.send(embed=embed_msg)
        return 0

    async def post_faceit_message_finished(self, channel_id, request_json):
        sub_players = ['ad42c90b-45a9-49b6-8ab0-9c8662330543',
                       '278790a2-1f08-4350-bd96-427f7dcc8722',
                       '18e2a663-9e20-4db9-8b29-3c3cbdff30ac',
                       '8cbb0b36-4c6b-4ebd-a92b-829234016626',
                       'e1cddcbb-afdc-4e8e-abf2-eea5638f0363',
                       '9da3572e-1960-4ba0-bd3c-d38ef34c1f1c',
                       'b8e5cd07-1b43-4203-9173-465fddcd391f',
                       '4e7d1f6c-9045-4800-8eda-23c892dcd814']
        # str_nick1 = ''
        # str_nick2 = ''
        # stats1 = ''
        # stats2 = ''
        # mvphs1 = ''
        # mvphs2 = ''
        # my_color = 9936031
        channel = self.get_channel(id=channel_id)
        statistics = match_stats(request_json['payload']['id'])

        str_nick = ''
        for team in statistics['rounds'][0]['teams']:
            for player in team['players']:
                str_nick += '{}, '.format(player['nickname'])
        #         for idx in sub_players:
        #             if player['player_id'] == idx:
        #                 if team['team_stats']['Team Win'] == '1':
        #                     my_color = 2067276
        #                     break
        #                 else:
        #                     my_color = 10038562
        #                     break
        #
        # embed_msg = discord.Embed(title="Match Finished", type="rich",
        #                           description='[{0}](https://www.faceit.com/en/csgo/room/{1})'.format(
        #                               statistics['rounds'][0]['round_stats']['Map'], request_json['payload']['id']),
        #                           color=my_color)  # DARK RED - 10038562, DARK GREEN - 2067276, GREY - 9936031
        #
        # for player in statistics['rounds'][0]['teams'][0]['players']:
        #     str_nick1 += '{}\n'.format(player['nickname'])
        #     stats1 += '({}/{} | {})\n'.format(
        #         player['player_stats']['Kills'],
        #         player['player_stats']['Deaths'],
        #         player['player_stats']['K/D Ratio'])
        #     mvphs1 += '({} | {})\n'.format(
        #         player['player_stats']['MVPs'],
        #         player['player_stats']['Headshots %'])
        #
        # for player in statistics['rounds'][0]['teams'][1]['players']:
        #     str_nick2 += '{}\n'.format(player['nickname'])
        #     stats2 += '({}/{} | {})\n'.format(
        #         player['player_stats']['Kills'],
        #         player['player_stats']['Deaths'],
        #         player['player_stats']['K/D Ratio'])
        #     mvphs2 += '({} | {})\n'.format(
        #         player['player_stats']['MVPs'],
        #         player['player_stats']['Headshots %'])
        #
        # embed_msg.add_field(name='Rounds: ' + statistics['rounds'][0]['teams'][0]['team_stats']['Final Score'],
        #                     value=str_nick1, inline=True)
        # embed_msg.add_field(name='(K/D|KD)', value=stats1, inline=True)
        # embed_msg.add_field(name='(MVP|HS%)', value=mvphs1, inline=True)
        # embed_msg.add_field(name='Rounds: ' + statistics['rounds'][0]['teams'][1]['team_stats']['Final Score'],
        #                     value=str_nick2, inline=True)
        # embed_msg.add_field(name='(K/D|KD)', value=stats2, inline=True)
        # embed_msg.add_field(name='(MVP|HS%)', value=mvphs2, inline=True)

        image_list = collect_image(request_json, statistics)
        await self.delete_message_by_faceit_match_id(request_json['payload']['id'])
        for image in image_list:
            with BytesIO() as image_binary:
                image.save(image_binary, 'PNG')
                image_binary.seek(0)
                await channel.send('https://www.faceit.com/en/csgo/room/{0}'.format(request_json['payload']['id']) + ','
                                   + str_nick + statistics['rounds'][0]['round_stats']['Map'],
                                   file=discord.File(fp=image_binary, filename='image.png'))
        return 0

    async def post_faceit_message_aborted(self, channel_id, request_json):
        channel = self.get_channel(id=channel_id)
        my_color = 1
        embed_msg = discord.Embed(title="Match Aborted", type="rich",
                                  description='[{0}](https://www.faceit.com/en/csgo/room/{1})'.format(
                                      request_json['payload']['id'], request_json['payload']['id']),
                                  color=my_color)
        str_nick1 = ''
        str_nick2 = ''

        for player in range(0, 5):
            str_nick1 += str(request_json['payload']['teams'][0]['roster'][player]['nickname']) + '\n'
            str_nick2 += str(request_json['payload']['teams'][1]['roster'][player]['nickname']) + '\n'

        embed_msg.add_field(name=request_json['payload']['teams'][0]['name'], value=str_nick1, inline=True)
        embed_msg.add_field(name=request_json['payload']['teams'][1]['name'], value=str_nick2, inline=True)
        await self.delete_message_by_faceit_match_id(request_json['payload']['id'])
        await channel.send(embed=embed_msg)
        return 0

    async def delete_message_by_faceit_match_id(self, match_id):
        channel = Client.get_channel(self, 828940900033626113)
        messages = await channel.history(limit=10).flatten()
        for message in messages:
            if message.embeds:
                if match_id in message.embeds[0].description:
                    await message.delete()
                    break

    async def post_faceit_test_finished(self, channel_id, request_json):
        pass


if __name__ == '__main__':
    intents = discord.Intents.all()
    bot_client = MyClient(intents=intents)

    port = int(os.environ.get('PORT', 5000))
    print(f'variable port:{port}')
    partial_run = partial(app.run, host='0.0.0.0', port=port)

    t = Thread(target=partial_run)
    t.start()

    bot_client.run(TOKEN)
