import discord
from discord import Client
import io
from PIL import Image, ImageFont
import requests
from PIL import ImageDraw

request_json = {'transaction_id': 'ea21ff1c-da66-44f4-9b1d-8d69d4757674', 'event': 'match_status_finished', 'event_id': 'f577fc62-a2ec-4983-9224-b2f6ababa9b8', 'third_party_id': 'ad42c90b-45a9-49b6-8ab0-9c8662330543', 'app_id': '4ef06a92-08ba-425e-bf12-c49c17d5ec7e', 'timestamp': '2021-04-08T11:10:06Z', 'retry_count': 0, 'version': 1, 'payload': {'id': '1-2a269a3b-5e11-4ba9-8ce6-81cd79d16809', 'organizer_id': 'faceit', 'region': 'EU', 'game': 'csgo', 'version': 48, 'entity': {'id': '42e160fc-2651-4fa5-9a9b-829199e27adb', 'name': 'CS:GO 5v5', 'type': 'matchmaking'}, 'teams': [{'id': 'dc4eff6f-d501-4249-a910-435d3b26a2b8', 'name': 'team_crckedD', 'type': '', 'avatar': 'https://assets.faceit-cdn.net/avatars/dc4eff6f-d501-4249-a910-435d3b26a2b8_1617786870610.jpg', 'leader_id': 'dc4eff6f-d501-4249-a910-435d3b26a2b8', 'co_leader_id': '', 'roster': [{'id': 'dc4eff6f-d501-4249-a910-435d3b26a2b8', 'nickname': 'crckedD', 'avatar': 'https://assets.faceit-cdn.net/avatars/dc4eff6f-d501-4249-a910-435d3b26a2b8_1617786870610.jpg', 'game_id': '76561199038678403', 'game_name': '-sweden 100ping', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': 'd2f2eaa0-d855-4e40-8d58-c497ab788584', 'nickname': 'Sokkan', 'avatar': 'https://assets.faceit-cdn.net/avatars/d2f2eaa0-d855-4e40-8d58-c497ab788584_1617192548276.jpg', 'game_id': '76561198056151703', 'game_name': 'Tyran', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': '89f750fa-3934-410f-93a1-fb7e68d9c079', 'nickname': '-KAJZE', 'avatar': 'https://assets.faceit-cdn.net/avatars/89f750fa-3934-410f-93a1-fb7e68d9c079_1601068561726.jpg', 'game_id': '76561198414640173', 'game_name': 'KAJZE', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': '0ecf6c91-280e-46d5-ba15-3e03b2e0bb07', 'nickname': 'Velvis', 'avatar': 'https://assets.faceit-cdn.net/avatars/0ecf6c91-280e-46d5-ba15-3e03b2e0bb07_1614864208684.jpg', 'game_id': '76561198122333283', 'game_name': '♛𝓥𝓮𝓵𝓿𝓲𝓼♛', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': '0e2de681-8f5e-445e-9935-f030b3f1ad54', 'nickname': 'Neff0', 'avatar': '', 'game_id': '76561198165335674', 'game_name': 'Neffo', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}], 'substitutions': 0, 'substitutes': None}, {'id': 'ed19e4d0-27a3-4562-b4ab-9cd5b9f33cab', 'name': 'team_burgE77', 'type': '', 'avatar': '', 'leader_id': 'ed19e4d0-27a3-4562-b4ab-9cd5b9f33cab', 'co_leader_id': '', 'roster': [{'id': 'ed19e4d0-27a3-4562-b4ab-9cd5b9f33cab', 'nickname': 'burgE77', 'avatar': '', 'game_id': '76561198843744707', 'game_name': 'burge35', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': '638e4e95-7cba-4d4a-8cb0-273fb09fd7bd', 'nickname': '4o_dal_jeest', 'avatar': 'https://assets.faceit-cdn.net/avatars/638e4e95-7cba-4d4a-8cb0-273fb09fd7bd_1603709780030.jpg', 'game_id': '76561199003173738', 'game_name': 'lev2512', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': '7007d6cb-fd8d-4279-94c6-3705d1c8e3f3', 'nickname': '-Exp0', 'avatar': 'https://assets.faceit-cdn.net/avatars/7007d6cb-fd8d-4279-94c6-3705d1c8e3f3_1552612915592.jpg', 'game_id': '76561198160813877', 'game_name': 'Exp0 ♛', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': '278790a2-1f08-4350-bd96-427f7dcc8722', 'nickname': '-NAPAD', 'avatar': 'https://assets.faceit-cdn.net/avatars/278790a2-1f08-4350-bd96-427f7dcc8722_1583523957971.jpg', 'game_id': '76561198061461007', 'game_name': '-NAPAD`11 #ACIDHOUZE', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}, {'id': 'c6841b96-765c-469f-ac3a-e22d5c4c87c0', 'nickname': '-example-_-', 'avatar': 'https://assets.faceit-cdn.net/avatars/c6841b96-765c-469f-ac3a-e22d5c4c87c0_1611353077607.jpg', 'game_id': '76561199041548369', 'game_name': '-example-_-', 'game_skill_level': 10, 'membership': '', 'anticheat_required': True}], 'substitutions': 0, 'substitutes': None}], 'created_at': '2021-04-08T10:27:04Z', 'updated_at': '2021-04-08T11:10:06Z', 'started_at': '2021-04-08T10:30:35Z', 'finished_at': '2021-04-08T11:10:06Z'}}

with open('token.txt', 'r') as file:
    TOKEN = file.read()


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
        image = Image.open("test.png")
        with io.BytesIO() as image_binary:
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            await channel.send('https://www.faceit.com/en/csgo/room/{0}'.format('1-6672c059-bfbf-48f3-a6d6-8e8fddd2a5e3'))
            # await channel.send('message', file=discord.File(fp=image_binary, filename='image.png'))

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
    bot_client.run(TOKEN)


if __name__ == '__main__':
    main()
