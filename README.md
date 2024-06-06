# discord-tts-bot
## A Python discord bot that utilizes ElevenLabs api to give users different voices.

### Description
This is a Python Discord TTS (text-to-speech) bot that uses the ElevenLabs AI API to generate higher-quality speech from text messages sent in any given Discord server. This is especially helpful for those users who don't want to speak but want to be included in the conversation! This bot does not utilize an audio stream, but creates temporary mp3 files that are
then deleted once all voice lines are played, reducing the required overhead.




### Requirements
- Python 3.6
- ffmpeg
  

### Installation
```
git clone https://github.com/ACreencia/discord-tts-bot.git
pip install -r requirements.txt
pip install ffmpeg-python
```


### Limitations
The TTS Bot utilizes a free account for ElevenLabs, which means that the monthly character request limit may be limited, and this additionally means it cannot handle more than 2 concurrent requests at a time (3 or more requests in a very short time frame will not go through, and it will slowly generate the tts instead of being near real-time).


