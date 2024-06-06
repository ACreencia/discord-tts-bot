#====================================================
#  bot.py
# Author: Alex C
# main file (RUN THIS FILE TO START BOT)
# Description:
# links bot to commands and filters basic messages
#====================================================
import discord
from discord.ext import commands  
from bot_setup import DISCORD_TOKEN, talk_bot
import tts_handler


@talk_bot.event
async def on_ready():
    #talk_bot.remove_command("help")
    await talk_bot.add_cog(tts_handler.tts(talk_bot))
    print(f"{talk_bot.user} now ready")

@talk_bot.event
async def on_message(message):
    """ on_message filter for checking whether a command was invoked or not"""
    if message.author == talk_bot.user:
      return
    # if message has an embed
    if message.embeds:
      return
    
    await talk_bot.process_commands(message)
    







talk_bot.run(DISCORD_TOKEN)
