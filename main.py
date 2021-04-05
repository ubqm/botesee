import discord
import os
from discord import Client
from flask import Flask, request, Response
from threading import Thread
from functools import partial

TOKEN = ''
with open('token.txt', 'r') as file:
    TOKEN = file.read()

app = Flask(__name__)


@app.route('/', methods=['POST'])
def respond():
    print(request.json)
    print('respond function called')
    return Response(status=200)


class MyClient(discord.Client):
    roles_that_cant_vote = ['@everyone']

    async def on_ready(self):
        for guild in self.guilds:
            print(f'Logged on as {self.user}, server: {guild.name}, guild_id:{guild.id}')

    async def on_message(self, message):
        print(f'New message from {message.author}: {message.content}')
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
            print(f'Emoji {payload.emoji} added by:{payload.member}, Message by: {message.author}, Message: {message.content}')

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
                print(f'*** Message "{message.content}" deleted with {upvotes} Upvotes, {downvotes} Downvotes, message_id:{message.id}')
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


if __name__ == '__main__':
    intents = discord.Intents.all()
    client = MyClient(intents=intents)

    port = int(os.environ.get('PORT', 5000))
    partial_run = partial(app.run, host='0.0.0.0', port=port)

    t = Thread(target=partial_run)
    t.start()

    client.run(TOKEN)
