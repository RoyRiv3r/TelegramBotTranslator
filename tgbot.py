import telebot
import requests
import time
import json
import base64
import io

# Text-topeech variables
T2S_ENDPOINT = 'https://texttospeech.googleapis.com/v1beta1/text:synthesize?key='
T2S_APIKEY = ''
API_TOKEN = ''
DEEPL_API_KEY = ''
TARGET_LANGUAGE = 'lang'  # Set your desired target language here
OWNER_IDS = []

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept": "*/*",
    "Accept-Language": "en-GB,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "text/plain;charset=UTF-8",
    "Origin": "https://www.gstatic.com",
    "Connection": "keep-alive",
    "Referer": "https://www.gstatic.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "DNT": "1",
    "Sec-GPC": "1"
}


payload = {
    "input": {
        "text": ""
    },
    "voice": {
        "languageCode": "en-US",
        "name": "en-US-Neural2-F"
    },
    "audioConfig": {
        "audioEncoding": "LINEAR16",
        "pitch": 0,
        "speakingRate": 1,
        "effectsProfileId": [
            "small-bluetooth-speaker-class-device"
        ]
    }
}




bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['tts'])
def speak(message):
    if message.from_user.id not in OWNER_IDS:
        return

    if message.reply_to_message:
        if message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            bot.reply_to(message, 'Please reply to a text message with the /speak command.')
            return
    else:
        bot.reply_to(message, 'Please reply to a text message with the /speak command.')
        return

    log_interaction(message.from_user.id, message.from_user.first_name, 'speak', text, time.time())

    audio = text_to_speech(text)
    if audio:
        bot.send_voice(message.chat.id, audio)
    else:
        bot.reply_to(message, 'Text-to-speech conversion failed. Please try again.')

# Update the available_commands list
available_commands = [
    '/start - Start the bot',
    '/help - Get a list of available commands',
    '/info - Get information about the bot',
    '/status - Check the bot status',
    '/hello - Say hello to the bot',
    '/speak - Generate text-to-speech audio for a message (reply to a message with this command)'
]

def translate_text(text, target_lang):
    url = 'https://api-free.deepl.com/v2/translate' #put pro api if you have premium api key
    headers = {'Authorization': f'DeepL-Auth-Key {DEEPL_API_KEY}'}
    data = {'text': text, 'target_lang': target_lang}
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        translated_text = response.json()['translations'][0]['text']
        return translated_text
    else:
        return None
def text_to_speech(text):
    ssml_text = '<speak>' + text.replace('\n', '<break time="500ms"/>') + '</speak>'
    payload["input"] = {"ssml": ssml_text}
    response = requests.post(T2S_ENDPOINT + T2S_APIKEY, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        response_data = response.json()
        audio_content = base64.b64decode(response_data['audioContent'])
        return io.BytesIO(audio_content)
    else:
        print(f"Text-to-speech API call failed with status code {response.status_code}. Response text:")
        print(response.text)
        return None

def log_interaction(user_id, user_name, command, message_text, timestamp):
  print(
    f'User {user_name} (ID: {user_id}) used command {command} with message "{message_text}" at {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))}'
  )

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in OWNER_IDS:
        return
    log_interaction(message.from_user.id, message.from_user.first_name, 'start', '', time.time())
    response = 'Welcome! This is a simple Telegram bot.\n\nAvailable commands:\n' + '\n'.join(available_commands)
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['help'])
def help(message):
    if message.from_user.id not in OWNER_IDS:
        return
    log_interaction(message.from_user.id, message.from_user.first_name, 'help', '', time.time())
    response = 'This bot supports the following commands:\n' + '\n'.join(available_commands)
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['info'])
def info(message):
    if message.from_user.id not in OWNER_IDS:
        return
    log_interaction(message.from_user.id, message.from_user.first_name, 'info', '', time.time())
    bot.send_message(message.chat.id, 'This Telegram bot is created using the pyTelegramBotAPI library.')

@bot.message_handler(commands=['status'])
def status(message):
    if message.from_user.id not in OWNER_IDS:
        return
    log_interaction(message.from_user.id, message.from_user.first_name, 'status', '', time.time())
    bot.send_message(message.chat.id, 'The bot is up and running!')

@bot.message_handler(commands=['hello'])
def hello(message):
    if message.from_user.id not in OWNER_IDS:
        return
    log_interaction(message.from_user.id, message.from_user.first_name, 'hello', '', time.time())
    bot.send_message(message.chat.id, 'Hello there! I hope you\'re having a great day!')


@bot.message_handler(content_types=['text', 'photo', 'video'])
def auto_translate(message):
    if message.from_user.id not in OWNER_IDS:
        return

    if message.photo and message.caption:
        text = message.caption
    elif message.video and message.caption:
        text = message.caption
    elif message.text:
        text = message.text
    else:
        return

    log_interaction(message.from_user.id, message.from_user.first_name, 'auto_translate', text, time.time())

    translated_text = translate_text(text, TARGET_LANGUAGE)

    if translated_text:
        bot.reply_to(message, translated_text)
    else:
        bot.reply_to(message, 'Translation failed. Please check the target language and try again.')

if __name__ == '__main__':
    print('Bot started...')
    bot.polling()
