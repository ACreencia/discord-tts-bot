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

## Configuration
Inside the `config` folder, there is a .env file. Edit the .env file in an editor of your choosing, and edit the file with your own Discord Token and ElevenLabs Api key/Token. If you don't know how to generate your Discord Token and/or your ElevenLabs API key, you can follow a guide on how to create it [here](https://github.com/ACreencia/discord-tts-bot/wiki)


## Limitations
The TTS Bot utilizes a free account for ElevenLabs, which means that the monthly character request limit may be limited, and this additionally means it cannot handle more than 2 [concurrent requests](https://help.elevenlabs.io/hc/en-us/articles/14312733311761-How-many-requests-can-I-make-and-can-I-increase-it) at a time (3 or more requests in a very short time frame will not go through, and it will slowly generate the tts instead of being near real-time). If you use your own ElevenLabs API key and your account has higher permissions/a subscription, you will not be limited to these limitations



## Usage
Here's a list of all the commands for the bot:

| Command      | Alias   |   Description   | Example usage |
|--------------|---------|---------------|----------|
| !join        | None    |  Joins the current voice channel of the user who sent the command | !join |
| !listen      | None | Begin listening to this specific discord username for tts messages | !listen |
| !stop | None | stops listening to this specific discord username for tts messages | !stop |
| !leave | None | Bot leaves the current voice channel it is in | !leave |
| !change <voice_id> | None | changes your tts voice to <voice_id>.  | !change pvleJogO6ysv81iuFFgp |
| !usage   | !use, !idk, !? | displays a help message with all the available commands | !usage |




