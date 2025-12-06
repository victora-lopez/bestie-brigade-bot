import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event()
async def on_ready():
    print(f'{client.user} is activated and ready for use')

