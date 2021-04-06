import discord
import os

from IPython.terminal.pt_inputhooks.asyncio import loop
from discord import Client
from flask import Flask, request, Response
from threading import Thread
from functools import partial

#test channel channel_id=828914045113335819 guild_id=328985007412740107
TOKEN = ''
with open('token.txt', 'r') as file:
    TOKEN = file.read()

app = Flask(__name__)


@app.route('/', methods=['GET'])
def respond_default_get():
    #для тестов на своей машине loop.create_task(bot_client.post_faceit_message_ready(channel_id=828940900033626113, request_json=request.json))
    return Response(status=200)


@app.route('/match_status_ready', methods=['POST'])
def respond_status_ready():
    print(request.json)
    print('request.json type', type(request.json))
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
            if message.attachments or message.embeds:
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

        embed_msg = discord.Embed(title="Match Ready", type="rich", description=f'{0}'.format(request_json['payload']['entity']['id']), color=9936031)  #DARK RED - 10038562, DARK GREEN - 2067276, GREY - 9936031
        str_nick1 = ''
        str_nick2 = ''

        for player in range(0, 5):
            str_nick1 += str(request_json['payload']['teams'][0]['roster'][player]['nickname']) + '\n'
            str_nick2 += str(request_json['payload']['teams'][1]['roster'][player]['nickname']) + '\n'

        embed_msg.add_field(name=request_json['payload']['teams'][0]['name'], value=str_nick1, inline=True)
        embed_msg.add_field(name=request_json['payload']['teams'][1]['name'], value=str_nick2, inline=True)
        #embed_msg.add_field(name='playername1', value='10', inline=False)
        await channel.send(embed=embed_msg)
        return 0

    async def post_faceit_message_finished(self, channel_id, request_json):
        channel = self.get_channel(id=channel_id)

        embed_msg = discord.Embed(title="Match Finished", type="rich", description=f'{0}'.format(request_json['payload']['entity']['id']), color=9936031)  # DARK RED - 10038562, DARK GREEN - 2067276, GREY - 9936031
        str_nick1 = ''
        str_nick2 = ''

        for player in range(0, 5):
            str_nick1 += str(request_json['payload']['teams'][0]['roster'][player]['nickname']) + '\n'
            str_nick2 += str(request_json['payload']['teams'][1]['roster'][player]['nickname']) + '\n'

        embed_msg.add_field(name=request_json['payload']['teams'][0]['name'], value=str_nick1, inline=True)
        embed_msg.add_field(name=request_json['payload']['teams'][1]['name'], value=str_nick2, inline=True)
        embed_msg.add_field(name='', value=' ', inline=False)

        await channel.send(embed=embed_msg)
        return 0

    async def post_faceit_message_aborted(self, channel_id, request_json):
        return 0


if __name__ == '__main__':
    intents = discord.Intents.all()
    bot_client = MyClient(intents=intents)

    port = int(os.environ.get('PORT', 5000))
    partial_run = partial(app.run, host='0.0.0.0', port=port)

    t = Thread(target=partial_run)
    t.start()

    bot_client.run(TOKEN)
