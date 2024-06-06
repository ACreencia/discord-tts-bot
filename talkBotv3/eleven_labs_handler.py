#==========================
# eleven_labs_handler.py
# Author: Alex C.
#
#==========================



from bot_setup import ELEVEN_LABS_API_KEY
from random import randrange
from elevenlabs.client import AsyncElevenLabs
from elevenlabs import save

temp_file_name = "tts_voice_line.mp3"

class ElevenLabsHandler():
  """ elevenlabs Handler that controls the tts api calls to elevenlabs api. does NOT play the generated mp3 file. Creates an association with user and voice"""
  
  __slots__ = ('_elevenlabs_client', '_voiceIDs') 
# elevenlabs built in async client to automate api calls


  def __init__(self):
    #self._elevenlabsClient = elevenlabsClient
    self._elevenlabs_client = AsyncElevenLabs(api_key=ELEVEN_LABS_API_KEY)
    self._voiceIDs = self.get_en_voice_list()

    
 
  async def get_en_voice_list(self):
    """
      gets a list of all voices from elevenlabs that have the english language label
      Parameters
      --------------------
        None
      
      RETURNS:
      eng_voices (list)       : List of Voice Objects (from elevenlabs python documentation) that are english based
      
    """
    
    eng_voices =  []
    response = self._elevenlabs_client.voices.get_all()
    for voice_filter in response:     # voice_filter is a tuple that holds (voice, VoiceList{VoiceObject(),..})
      for voices in voice_filter[1]:  # access the inner VoiceObjects within VoiceList
        if (voices.fine_tuning.language == "en"):
          eng_voices.append(voices)
    return await eng_voices


  async def get_rand_en_voice(self):
    """
    generates a random english voice_id 
    """
    return await (self._voiceIDs[randrange(1,len(self._voiceIDs))])

  

  async def generate_tts_mp3(self, response_message, voice_id_choice):
    """
    generates an mp3 file with the words (response_message), and the specific voice from (voice_id_choice).

    Parameters
    ------------
    response_message: (string)
      The words that will be said in the tts message
    
    voice_id_choice: (voice_id_choice)
      The elevenlabs voice_id of the desired voice for tts
    
    """
    audio_stream = await self._elevenlabs_client.generate(
        text = response_message,
        model="eleven_monolingual_v1",
        voice = voice_id_choice,
    )
    # need to async wait for all bytes of generated voice file
    out = b''
    async for chunk in audio_stream:
      out += chunk
    save(out, temp_file_name)