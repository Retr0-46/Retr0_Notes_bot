from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command

import speech_recognition as sr

import asyncio
import logging
import sys
import os
import subprocess

token = '7308225129:AAF8fzDai0tDHxdPv7v0L8KRPJDzuD2FWgo'
pref = '/'

r = sr.Recognizer()

dp = Dispatcher()

data = {}


@dp.message()
async def get_voice(msg: Message):
    name = f'{msg.from_user.id}.wav'
    await msg.bot.download(file=msg.voice.file_id, destination=name)
    namew = f'w-{msg.from_user.id}.wav'
    subprocess.call(['ffmpeg', '-i', name, namew])
    v = sr.AudioFile(namew)
    with v as source:
        #r.adjust_for_ambient_noise(source)
        audio = r.record(source)
        result = r.recognize_google(audio, language='ru')
    await msg.reply(f'{result}')
    os.remove(name)
    os.remove(namew)


@dp.message(Command('start', prefix=pref))
async def start(mg: Message):
    data.update({mg.from_user.id: []})
    await mg.answer(f'Рад тебя видеть!\nЯ - бот, который поможет тебе в твоих повседневных вещах.')


async def main():
    bot = Bot(token=token)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())