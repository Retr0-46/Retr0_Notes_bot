from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ContentType, File, Message
from aiogram.filters import Command, CommandStart

import PIL
from PIL import Image, ImageDraw, ImageFont

import speech_recognition as sr

from pydub import AudioSegment
import io

import asyncio
import logging
import sys
import os
import subprocess

token = '7308225129:AAF8fzDai0tDHxdPv7v0L8KRPJDzuD2FWgo'
pref = '/'

ft = ImageFont.truetype('Roboto-Regular.ttf', 48)

op_arr = ['вести твой список дел', 'дешифровывать голосовые и аудио', 'создавать мемы (демотиваторы)']

comm_help = {'демотиватор': 'фото + /dem текст',
             'голосовые': 'отправьте голосовое или аудио, далее будет предложен выбор: добавить в список дел или дешифровать'}

comm_help_keys = comm_help.keys()

r = sr.Recognizer()

bot = Bot(token)
dp = Dispatcher()

data = {}

voice_rec = ''


def opportunities(arr: list) -> str:
    ans = ''
    for i, x in enumerate(arr):
        ans += f'\n{i+1}) {x}'
    return ans


# def convert2Waw(bytes):
#     wavBytes = io.BytesIO()
#     bytes.export(wavBytes, format='wav')
#     wavBytes.seek(0)
#     return wavBytes
#
#
# @dp.message(F.voice | F.audio)
# async def voiceHandler(message: types.Message):
#     fileId = message.voice.file_id if message.voice else message.audio.file_id
#     file = await bot.get_file(fileId)
#     fileData = await bot.download_file(file.file_path)
#
#     oggBytes = AudioSegment.from_file(fileData, format='ogg')
#     wavBytes = convert2Waw(oggBytes)
#     rec = sr.Recognizer()
#     with sr.AudioFile(wavBytes) as source:
#         audio = rec.record(source)
#
#     try:
#         text = rec.recognize_google(audio, language='ru-RU')
#         await message.answer(f'{text}')
#     except sr.UnknownValueError:
#         await message.answer('Не удалось распознать речь')
#     except sr.RequestError as e:
#         await message.answer(f'Ошибка: {e}')


@dp.message(F.voice | F.audio)
async def get_voice(msg: Message):
    global voice_rec
    print('Захватил')
    print(msg.content_type)
    if msg.voice:

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Дешифровать",
            callback_data="voice_recognise"), types.InlineKeyboardButton(text='hyina', callback_data='huina')
        )

        name = f'{msg.from_user.id}.wav'
        await msg.bot.download(file=msg.voice.file_id, destination=name)
        namew = f'w{msg.from_user.id}.wav'
        subprocess.call(['ffmpeg', '-i', name, namew])
        v = sr.AudioFile(namew)
        with v as source:
            # r.adjust_for_ambient_noise(source)
            audio = r.record(source)
            voice_rec = r.recognize_google(audio, language='ru')
        await msg.reply(f'что мне с ним сделать?', reply_markup=builder.as_markup())
        os.remove(name)
        os.remove(namew)
    else:
        print('dfsdgfds')
        pass


@dp.callback_query(F.data == 'voice_recognise')
async def send_recognised_voice(callback: types.CallbackQuery):
    await callback.message.answer(f'Распознанный текст:\n{voice_rec}')


@dp.callback_query(F.data == 'huina')
async def send_huina(callback: types.CallbackQuery):
    await callback.message.answer(f'huina')


@dp.message(Command('dem', prefix=pref))
async def dem(message: Message):
    s = message.caption.split(maxsplit=1)[1]

    await message.bot.download(file=message.photo[-1].file_id, destination='1.jpg')

    with Image.open('dem.png') as img:
        img.load()
    with Image.open('1.jpg') as insert:
        insert.load()

    img = img.resize((950, 850))
    img.paste(insert.resize((800, 640)), (75, 46))
    d = ImageDraw.Draw(img)
    d.text((950 // 2, 770), s, fill='white', anchor='ms', font=ft)
    img.save('final.png', 'PNG')

    os.remove('1.jpg')

    await message.answer_photo(types.FSInputFile('final.png'))
    os.remove('final.png')


@dp.message(Command('start', prefix=pref))
async def start(mg: Message):

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='подробнее', callback_data='help'))

    data.update({mg.from_user.id: []})
    await mg.answer(f'Рад тебя видеть!\nЯ - бот, который поможет тебе в твоих повседневных вещах.')
    await mg.answer(f'Вот что я могу: {opportunities(op_arr)}', reply_markup=builder.as_markup())


@dp.callback_query(F.data == 'help')
async def commHelp(callback: types.CallbackQuery):
    names = [x for x in comm_help.keys()]

    builder = InlineKeyboardBuilder()
    for x in names:
        builder.add(types.InlineKeyboardButton(text=x, callback_data=x))
    await callback.message.answer(text='О чем конкретно вы хотели узнать?', reply_markup=builder.as_markup())


@dp.callback_query(F.data.in_(comm_help_keys))
async def help_in(callback: types.CallbackQuery):
    await callback.message.answer(comm_help[callback.data])


async def main():
    bot = Bot(token=token)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())