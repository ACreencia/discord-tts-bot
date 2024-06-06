#------------------------------
# Bot_setup.py
# Author: Alex C
# Description: This file handles the intial setup and creation of the bot. It grabs the discord authentication token from the .env file, and gives 
#              a discord <client> object to bot.py along with the DISCORD_TOKEN: <str> 
#------------------------------



import discord
from discord.ext import commands  
import os
from elevenlabs import Voice, VoiceSettings
from elevenlabs.client import ElevenLabs, AsyncElevenLabs

from pathlib import Path
from dotenv import load_dotenv


# obtain path to .env file stored in ../config/.env
path = Path(__file__).parent.absolute()

# obtain token for discord to verify the bot
token_path = str(path) + '\config\.env'

try:
  env_flag = load_dotenv(token_path)
except Exception as e:
  print("ERROR: could not obtain discord token. Please make sure token is in right directory, and that it is a valid token")

# Obtaining keys and tokens from .env file
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
ELEVEN_LABS_API_KEY = os.getenv('ELEVENLABS')

# create intent for discord to understand what bot will listen to
bot_intents = discord.Intents.default()
bot_intents.message_content = True # NOQA
bot_intents.voice_states = True # NOQA

# create bot object
talk_bot = commands.Bot(command_prefix=("!", "$"), intents=bot_intents)
#talk_bot.remove_command("help")



'''
Elevenlabs Test Setup
'''

""" The following block of code will cause an error if the ELEVEN_LABS_API_KEY fails to authenticate. Please ensure your key is valid and in a .env file under the field ELEVENLABS """
# elevenlabs built in async client to automate api calls.
async_client = AsyncElevenLabs(
  api_key = ELEVEN_LABS_API_KEY,
)

