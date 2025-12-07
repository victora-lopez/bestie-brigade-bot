from config import TOKEN, INTENTS, PREFIX
import discord
from discord.ext import commands
import logging

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} is activated and ready for use')

@bot.command()
async def rankcheck(ctx):
    
    await ctx.send(f"Entered rankcheck function, {ctx.author} initiated")

bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
