import discord
from discord import Client


with open('token.txt', 'r') as file:
    TOKEN = file.read()


class MyClient(discord.Client):
    async def on_ready(self):
        for guild in self.guilds:
            print(f'Logged on as {self.user}, server: {guild.name}, guild_id:{guild.id}')
            channel = Client.get_channel(self, 828940900033626113)
            messages = await channel.history(limit=10).flatten()
            for message in messages:
                print(message.embeds[0].description)
                print(type(message.embeds[0].description))

    async def delete_message_by_faceit_match_id(self, match_id):
        channel = Client.get_channel(self, 828940900033626113)
        messages = await channel.history(limit=10).flatten()
        for message in messages:
            if message.embeds:
                if match_id in message.embeds[0]:
                    await message.delete()
                    break


def main():
    intents = discord.Intents.all()
    bot_client = MyClient(intents=intents)
    bot_client.run(TOKEN)


if __name__ == '__main__':
    main()
