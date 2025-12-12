from config import TOKEN, INTENTS, PREFIX
import discord
from discord.ext import commands
import logging
import os

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} is activated and ready for use')

async def setup_hook():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            extension = "cogs." + filename[:-3]
            try:
                await bot.load_extension(extension)
                print(f'Loaded cog: {extension}')
            except Exception as e:
                print(f'Failed to load cog {extension}: {e}')

bot.setup_hook = setup_hook
bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
