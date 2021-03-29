import discord
from discord import Client

TOKEN = ''
with open('token.txt', 'r') as file:
    TOKEN = file.read()

authors = ['Ayudesee#9410', 'Huginn#4160', 'Hawk#1975', '-NAPAD#1705', 'DG アニメ#4612', 'gOOgle#4515', 'PiQa#4459',
           'Exclus1ve_#5197']
# <RawReactionActionEvent message_id=825443973366546442 user_id=112698229040177152 channel_id=506178772819771404 guild_id=506178772819771402 emoji=<PartialEmoji animated=False name='👎' id=None> event_type='REACTION_ADD' member=<Member id=112698229040177152 name='Ayudesee' discriminator='9410' bot=False nick=None guild=<Guild id=506178772819771402 name='Chill' shard_id=None chunked=False member_count=5>>>


class MyClient(discord.Client):
    async def on_ready(self):
        for _ in self.guilds:
            print(f'Logged on as {self.user}, server: {_.name}, guild_id:{_.id}')
        print('')

    async def on_message(self, message):
        print(f'New message from {message.author}: {message.content}')
        if message.attachments:
            await message.add_reaction('👍')
            await message.add_reaction('👎')


    async def on_raw_reaction_add(self, payload):
        upvotes = 0
        downvotes = 0
        if payload.emoji.name == '👍' or payload.emoji.name == '👎':
            print(payload)
            channel = Client.get_channel(self, payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            print(f'Message by: {message.author}, Emoji {payload.emoji} added by:{payload.member}, Message: {message.content}')
            for _ in message.reactions:
                if _.emoji == '👍':
                    upvotes = _.count
                    print(f'Upvotes:{upvotes}')
                if _.emoji == '👎':
                    downvotes = _.count
                    print(f'Downvotes:{downvotes}')
            if upvotes < downvotes - 2:
                await message.delete()
                print(f'*** Message "{message.content}" deleted with {upvotes} Upvotes, {downvotes} Downvotes, message_id:{message.id}')
            print(' ')

    async def on_raw_reaction_remove(self, payload):
        upvotes = 0
        downvotes = 0
        if payload.emoji.name == '👍' or payload.emoji.name == '👎':
            print(payload)
            channel = Client.get_channel(self, payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            print(f'Message by: {message.author}, Emoji {payload.emoji} removed by:{payload.member}, Message: {message.content}')
            for _ in message.reactions:
                if _.emoji == '👍':
                    upvotes = _.count
                if _.emoji == '👎':
                    downvotes = _.count

            print(f'Upvotes:{upvotes}')
            print(f'Downvotes:{downvotes}')
            if upvotes < downvotes - 2:
                await message.delete()
                print(f'*** Message "{message.content}" deleted with {upvotes} Upvotes, {downvotes} Downvotes, message_id:{message.id}')
            print(' ')


client = MyClient()
client.run(TOKEN)
