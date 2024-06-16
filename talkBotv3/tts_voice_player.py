#======================================
# tts_voice_handler.py
# Author: Alex C.
#
#======================================

import discord
import asyncio
import os
from bot_setup import talk_bot
from eleven_labs_handler import temp_file_name

class TTSVoicePlayer:
  """
  A voice player object that is assigned to each guild (server) using the talk_bot for tts voicing.

  This class implements a queue and loop, which allows for multiple guilds (servers) to use tts voicing
  simultaneously.

  When the bot disconnects from a voice channel it's instance will be destroyed
  """

  __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', '_voice_association')
  


  '''
  Params                      : Description
  ctx (discord.Context)       : The context/object in which a command is being invoked under
  bot (ext. discord.Client)   : The bot that contains the command being used
  _guild (discord.guild)      : The guild/server associated with the context's command
  _channel (discord.Channel)  : The voice channel associated with the context's command
  _cog  (cog)                 : The cog (class of related commands) associated with the context
  queue (Queue)               : The Queue of tts voice lines to be played
  next (Event)                : event flag that we set and check to see whether an event is done or not 
  _voice_association {dict}   : List of discord users that have registered, and their associated tts voice_id linked to them
  _elevenlabsHandlers (dict)  : Dictionary of all elevenLabsHandlers across the servers

  '''
  def __init__(self, ctx):
    '''
    Params                      : Description
    ctx (discord.Context)       : The context/object in which a command is being invoked under
    '''
    self.bot = ctx.bot
    self._guild = ctx.guild
    self._cog = ctx.cog
    
    self.queue = asyncio.Queue()
    self.next = asyncio.Event()   # an event flag that can be set, so we know if bot is ready or not after executing event
    self.current = None
    
    # voice related
    self._voice_association = {}

    ctx.bot.loop.create_task(self.tts_loop())


  
  def register_voice_id(self, discord_username, desired_voice_id):
    """
    Stores a username<-->tts_voice_id link within the _voice_association dictionary
    
    Parameters
    --------------- 
    discord_username: (str)      
      discord username of tts user
    desired_voice_id: (int)      
      the elevenlabs voice_id the discord username has chosen for their tts voice

    """
    self._voice_association[discord_username] = desired_voice_id
  
  
  def get_voice_id_of_user(self, discord_username):
    """
    getter function to grab the associated voice_id of the discord username. If None is returned, there is no voice_id linked to the discord username
    
    Parameters
    -------------------
    discord_username: (str)      
      discord username of tts user

    Returns
    ----------
    voice_id: (int)              
      elevenlabs (voice_id) associated with (discord_username)
    """
    try:
      return self._voice_association[discord_username]
    except Exception as e:
      return None
  
  def check_if_username_in_registered(self, discord_username):
    """
    checks if (discord_username) is in the stored list of users

    Parameters
    --------------
    discord_username: (string)
      the discord username 
    """
    return (discord_username in self._voice_association)
    
  def remove_user_from_registered(self, discord_username):
    """
    removes discord_username from the registered voice list

    Parameters
    ---------------
    discord_username: (string)
      the string representation of a user's discord username/id
    
    """
    self._voice_association.pop(discord_username)
    return

  def is_connected_to_vc(self, ctx):
      """
      checks whether the bot is connected to a voice channel. 

      Parameters
      -----------
      ctx: (discord.Context)
        the context object of the current discord server

      Returns
      ------------
      is_connected: (bool)
        returns True if bot is connected to a voice channel already, False if not.   
      """
      # grab voice_client of context so we can check if bot is connected to a voice channel
      voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
      
      return (voice_client != None)
      

  def find_voice_client(self, ctx):
    """
    finds the connected channel within the discord server the bot is connected to

    Parameters
    ------------
    ctx: (discord.Context)
      the context object of the current discord server
    """
  #current_vc_index = client.voice_clients.guild.index(message.guild)
    for connected_channel_session in talk_bot.voice_clients:
      if (connected_channel_session.guild == ctx.message.guild):
        return connected_channel_session
    return None

  async def tts_loop(self):
    """ loop to handle async """
    #Loop to ensure voice lines are being completed before intiating the next 
    await self.bot.wait_until_ready()

    # bot is ready at this point, while bot is not closed, grab next voice_lines
    while not self.bot.is_closed():
      self.next.clear()
      voice_line = await self.queue.get()
      self.current = voice_line

      # audio stream could go here
      # play the tts voice_line, then loop it again (thread-safe) until it is done playing the tts voice_line
      self._guild.voice_client.play(voice_line, after= lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
      await self.next.wait()
      

      # clean up after 
      voice_line.cleanup()
      
      # if there are no more voice_lines in the queue AND the voice_client is not currently playing any audio, delete the temporary mp3 file
      if (self.queue.empty() == True and (not self._guild.voice_client.is_playing())):
        await self.delete_file(temp_file_name)

      self.current = None

  async def get_discord_audio_player(self, ctx, loop):
    """
    generates a discord.FFmpegPCMAudio audio stream)

    Parameters
    ------------
    ctx: (discord.Context)
      the context object of the current discord server
    
    loop: (asyncio.loop)
      a loop that runs asynchronous tasks and callbacks
    
    Returns
    ------------
    audio_player: (discord.FFmpegPCMAudio)
      a ffmpeg audio player thats built-into discord
    """
    loop = loop or asyncio.get_event_loop()
    voice_client = self.find_voice_client(ctx)
    return discord.FFmpegPCMAudio(source=temp_file_name)

  async def delete_file(self, filename):
    """
    deletes a file based on the filename (full path)

    Parameters
    -------------
    filename: (string)
      an absolute path to the file-to-be-deleted
    """
    if os.path.exists(filename):
      os.remove(filename)


  def destroy(self, guild):
    """ TODO: to be implemented properly"""
  # disconnect and cleanup the tts player
    return self.bot.loop.create_task(self._cog.cleanup(guild))    
