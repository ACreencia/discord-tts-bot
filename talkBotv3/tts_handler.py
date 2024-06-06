#============================
# tts_handler.py
# Author: Alex C
#============================

"""
tts_voicePlayer cog class. 
Taking inspiration and cleaner formatting from EvieePy's code and Rapptz code for implementing a music player modified it to suit tts and implementing cogs + Bot instead of Client:
https://gist.github.com/EvieePy/ab667b74e9758433b3eb806c53a19f34 
https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py 

"""

""" Limitations: https://help.elevenlabs.io/hc/en-us/articles/14312733311761-How-many-requests-can-I-make-and-can-I-increase-it """
import discord
import asyncio
import re
from random import randrange
import asyncio

from async_timeout import timeout
from discord.ext import commands
from bot_setup import talk_bot
from eleven_labs_handler import ElevenLabsHandler
from tts_voice_player import TTSVoicePlayer

from elevenlabs import Voice, VoiceSettings, save
from elevenlabs.client import AsyncElevenLabs




class tts(commands.Cog):
    """ tts related commands """

    """
    _ttsVoiceInstances (dict{ ttsVoicePlayers })    : dictionary of all the invoked ttsVoicePlayers across multiple servers
    _registered_users 
    
    """
    __slots__ = ('bot', '_ttsVoiceInstances', '_registered_users', '_elevenlabsHandlers')

    def __init__(self, bot):
       self.bot = bot
       self._tts_voice_player_instances = {}
       self._registered_users = {}
       self._elevenlabsHandlers = {}
      

    

    # retrieve guild tts player, or generate one if it doesn't exist
    def get_tts_player(self, ctx):
      """
      grabs the tts_player object of the current server/guild

      Parameters
      --------------
      ctx: (discord.Context)
        the context object that is associated with the current discord server/guild
      
      
      Returns
      -------------
      tts_player: (tts_player <Class Object>)
        the tts_player class object
      """
      try:
        # grab tts player for the server/guild
        tts_player = self._tts_voice_player_instances[ctx.guild.id]
      except KeyError:
        # generate a tts player for the server/guild
        tts_player = TTSVoicePlayer(ctx)
        self._tts_voice_player_instances[ctx.guild.id] = tts_player
      return tts_player


    # NOTE: this does NOT verify the users eleven_labs_api, this will encounter an error. 
    def get_elevenlabs_handler(self, ctx):
      """ retrieves the elevenlabs handler from dictionary, or generates one if it does not exist. 
      NOTE: does not verify the api key, must make sure its valid first 
      
      Parameters
      ------------
      ctx: (discord.Context)
        the associated context with the current discord server
      
      Returns
      -------------
      eleven_labs_handler: (eleven_labs_handler <class: Object)
        the eleven_labs_handler class object
      """
      # retrieve elevenlabs handler, or generate one
      try:
        elevenlabs = self._elevenlabsHandlers[ctx.guild.id]
      except KeyError:
        elevenlabs = ElevenLabsHandler()
        self._elevenlabsHandlers[ctx.guild.id] = elevenlabs
      return elevenlabs

    @commands.command(name="usage", aliases=["use","?", "idk"])
    async def usage_message(self, ctx):
      """
      displays the usage/help_message to the user by sending it to the same channel they invoked the !usage command in 

      Parameters
      ------------
      ctx: (discord.Context)
        the associated context within the current discord server/guild
      """
      help_message = """
                     ```Bot Command          :  Description 
                     \n!listen              : bot listens to command sender's messages and convert them into tts messages using a randomly assigned english tts voice
                     \n!stop                : bot stops listening to user who sent command. If they aren't already registered, it will mention user was never registered
                     \n!join                : bot will join the current voice channel of user who sent !join command.
                     \n!leave               : bot will leave its current voice channel
                     \n!change <voice_id>   : changes the tts voice using elevenlabs voice_id (requires making an account and copy/pasting the acquired voice id from desired voice) e.g. !change pvleJogO6ysv81iuFFgp
                     \n                       
                     \nExample usage: 
                     \n<discord_username>: !join ---> !listen --> (bot is now ready to convert your messages to tts) ---> !stop. !leave used only when you want bot to leave voice channel```"""
      await ctx.send(help_message)
    
   
    

    @commands.command(name="listen")
    async def register_user(self, ctx):
      """
      registers the user to have their messages converted into tts 

      Parameters
      ------------
      ctx: (discord.Context)
        the associated context within the current discord server
      
      """
      if ctx.author in self._registered_users:
        await ctx.send(f"{str(ctx.author)} is already registered under tts bot for this session. Please use !help to find proper usage")
        return
      else:
        # obtain tts player
        tts_player = self.get_tts_player(ctx)
        elevenlabs = self.get_elevenlabs_handler(ctx)
        # get a random voice id from elevenlabs, then assign it to user through tts_player
        tts_player.register_voice_id(ctx.author, elevenlabs.get_rand_en_voice())
        await ctx.send(f"Voice assigned and now listening to user: {str(ctx.author)}")
        

        #elevenlabs.assign_rand_en_voice()

    @commands.command(name="join")
    async def join_vc(self, ctx):
      """ 
      handles the bot joining the same voice channel  as user through !join command, even if the bot is in a different channel than user
      
      Parameters
      ------------
      ctx: (discord.Context)
        the associated context within the current discord server/guild
      """
      #self.cleanup(ctx.guild)
      tts_player = self.get_tts_player(ctx)

      
      # if user who invoked join command is in a channel
      if (ctx.message.author.voice != None):

        # if bot is NOT in the same channel as the discord user
        if (ctx.message.author.voice != tts_player.find_voice_client(ctx)):
          connected_channel = tts_player.find_voice_client(ctx)

          # if the bot is in a channel
          if connected_channel != None:
            # must disconnect before reconnecting to a different channel
            await connected_channel.disconnect()
        voice_chat = await ctx.message.author.voice.channel.connect()
      else:
        return await ctx.message.channel.send("You must connect to a voice channel you want the bot to connect to first")

    @commands.command(name="leave")
    async def leave_vc(self, ctx):
      """
      handles the bot leaving the voice channel
      
      Parameters
      ------------
      ctx: (discord.Context)
        the associated context within the current discord server/guild
      """
      tts_player = self.get_tts_player(ctx)
      connected_channel = tts_player.find_voice_client(ctx)
      if connected_channel:
        await connected_channel.disconnect()
      else:
        await ctx.message.channel.send("Must be connected to a voice channel first before invoking  `!leave`  command.")

    @commands.command(name="change")
    async def change_user_voice(self, ctx, arg):
      """
      changes the users voice based on voice_id (arg)

      Parameters
      ------------
      ctx: (discord.Context)
        the associated context within the current discord server/guild

      arg: (string)
        the voice_id (obtained from elevenlabs website) of the desired voice
      """
      tts_player = self.get_tts_player(ctx)
      tts_player.register_voice_id(ctx.message.author, arg)
      await ctx.message.channel.send(f"{ctx.message.author}'s voice changed.")
  
    @commands.command(name="stop")
    async def stop_listening(self, ctx):
      if ctx.author in self._registered_users:
        self._registered_users.pop(ctx.author)
        await ctx.message.channel.send(f"Talk_Bot has stopped listening to {ctx.author}. Thanks for using Talk_bot!")
      else:
        await ctx.message.channel.send(f"{ctx.author} was not registered as a tts user. Use command  `!listen` to register, and  `!stop`  afterwards to stop bot from listening to your messages")

    @commands.Cog.listener()
    async def on_message(self, message):
      """ on_message listener for commencing tts functionality.
      NOTE: it will only commence tts if the user has already used the !listen command to register their username
      
      Parameters
      ----------
      message: (discord.Message)
        the Messageable discord object
      
      """
      # to prevent the bot from responding to itself
      if message.author == talk_bot.user:
        return
      
      # if it is a command, we ignore it and let other command functions handle
      if message.content.startswith("!"):
        return
      
      # check if user is registered, and if so, commence tts functionality
      else:
        ctx = await talk_bot.get_context(message)
        tts_player = self.get_tts_player(ctx)
        if tts_player.check_if_username_in_registered(message.author):
          if (tts_player.is_connected_to_vc(ctx)):
            await self.use_tts(ctx, message)
          else:
            await message.channel.send("Please make sure bot is connected to a voice channel first using  `!join`  command.")
        return
    
    def strip_attachment_urls(self, message):
      """
      removes urls from message if the message has attachments (to prevent tts bot from saying url links)
      NOTE: you cannot directly alter discord.Message because it is a discord model object, thus we create a temp string and return it
      Parameters
      -------------
      message: (discord.Message)
        the discord.Message object that contains message.content (the contents of the message)
      
      Returns
      -------------
      stripped_message: (string)
        the string represtation of the message stripped of url links
      """
      temp_message = ''
      for urls in message.attachments:
        temp_message += message.replace(urls.url, '')
      print(f"this is temp message: {temp_message}")
      return temp_message
          
    async def use_tts(self, ctx, message):
      """
      oversees the generation and playback of tts messages

      Parameters
      ------------
      ctx: (discord.Context)
        the associated context within the current discord server/guild
      
      message: (discord.Message)
        the discord.Message object that is obtained when user invokes command
      """
      # get respective class handlers
      tts_player = self.get_tts_player(ctx)
      eleven_labs_handler = self.get_elevenlabs_handler(ctx)

      # get voice_id associated with discord user, generate tts then delete it afterwards
      discord_username_voice_id = tts_player.get_voice_id_of_user(ctx.message.author)
      # generate tts_mp3, add it to tts_player queue
      if message.attachments:
          # cannot modify discord models directly, need to make a use case
          url_stripped_message = self.strip_attachment_urls(message)
          await eleven_labs_handler.generate_tts_mp3(url_stripped_message, discord_username_voice_id)
      else:
        url_stripped_message = self.strip_url_in_message(message)
        if (url_stripped_message == ""):
          return
        await eleven_labs_handler.generate_tts_mp3(url_stripped_message, discord_username_voice_id)
      
      source = await tts_player.get_discord_audio_player(ctx, loop=self.bot.loop)
      await tts_player.queue.put(source)
      

    def strip_url_in_message(self, message):
      """
      strips urls from a discord message (catches non attachment urls) so tts bot doesn't say the url links using regex
      NOTE: You cannot modify discord.Messages because it is of type discord.Model data type. Thus we return a string instead of modifying object directly
      Parameters
      -------------
      message: (discord.Message)
        the discord.Message object that contains message.content (the contents of the message)
      
      Returns
      -------------
      url_stripped_message: (string)
        the string represtation of the message without any url links
      """
      temp_message = message.content
      regex_pattern = '(http|ftp|https|media):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])'
      temp_message = re.sub(regex_pattern, '', temp_message)
      return temp_message
    
    async def cleanup(self, guild):
      """ clean up the voice_client player in the server"""
      try:
        await guild.voice_client.disconnect()
      except AttributeError:
        pass
    
      try:
        # delete the ttsVoicePlayer instance in specific guild
        del self.ttsVoicePlayers[guild.id]
      except KeyError:
        pass
    




    

    
    
   
    


