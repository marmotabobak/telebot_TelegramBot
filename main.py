import os

import yaml
import telebot
from pydub import AudioSegment
import speech_recognition


with open('bot.yml', 'r') as f:
    config = yaml.safe_load(f.read())

bot = telebot.TeleBot(token=config['bot_api_key'])


def oga2wav(filename: str) -> str:
    new_filename = filename.replace('.oga', 'wav')
    audio = AudioSegment.from_file(file=filename)
    audio.export(out_f=new_filename, format='wav')
    return new_filename


def recognize_speech(oga_filename: str) -> str:
    wav_filename = oga2wav(filename=oga_filename)
    recognizer = speech_recognition.Recognizer()

    with speech_recognition.WavFile(wav_filename) as source:
        wav_audio = recognizer.record(source=source)

    text = recognizer.recognize_google(audio_data=wav_audio, language='ru')

    if os.path.exists(path=oga_filename):
        os.remove(path=oga_filename)

    if os.path.exists(path=wav_filename):
        os.remove(path=wav_filename)

    return text


def download_file(file_id):
    global bot

    file_info = bot.get_file(file_id=file_id)
    downloaded_file = bot.download_file(file_path=file_info.file_path)
    filename = file_id + file_info.file_path
    filename = filename.replace('/', '_')
    with open(filename, 'wb') as f:
        f.write(downloaded_file)
    return filename


@bot.message_handler(commands=['start'])
def say_hi(message: telebot.types.Message) -> None:
    bot.send_message(chat_id=message.chat.id, text=f'Hi, {message.from_user.first_name}!')


@bot.message_handler(content_types=['voice'])
def transcript(message: telebot.types.Audio) -> None:
    filename = download_file(file_id=message.voice.file_id)
    text = recognize_speech(oga_filename=filename)
    bot.send_message(chat_id=message.chat.id, text=text)


bot.polling()




