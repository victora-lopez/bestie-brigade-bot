import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('PREFIX','!')
OWNER_IDS = os.getenv('OWNER_IDS',None)
INTENTS = None
