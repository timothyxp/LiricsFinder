from config import Config
import argparse
import asyncio
import pytz
from datetime import timedelta
from text_base.search_getter import get_searcher
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from nn.ASR_getter import get_asr
from datetime import datetime
import pandas as pd
from projectUtils import read_song_csv
from database.database import DataBase
from aiogram.utils.callback_data import CallbackData

config = None
token_path = "token.txt"
with open(token_path, "r") as f:
    token = f.read()
parser = argparse.ArgumentParser()
parser.add_argument("--database_path")
parser.add_argument("--index_path")
parser.add_argument("--test", action="store_true", default=False)
query_history = {}
args = parser.parse_args()
config = Config(
    database_path=args.database_path,
    index_path=args.index_path,
    test=args.test,
    user_story_database_path="/home/tim0th/db/database.json"
)
db = dict()
base = DataBase(config.user_story_database_path)
endl = "\n"
message_time_delta = timedelta(seconds=config.user_message_time_delta)
error_audio = "Извините, это аудио не может быть обработано"
error_document = "Извините, этот документ не может быть обработан"
size_error = "Размер отправленного файла слишком большой"
searcher = get_searcher(config)
asr = get_asr(config)
bot = Bot(token=token)
dp = Dispatcher(bot)
top5 = CallbackData("top5", "db_id", "number")
symbols = 3900
sticker_SenyaHelp = "CAACAgIAAxkBAAIBAmOgGKblmyol1Ml3HzOUxUqTZLrZAAK5IgAC6VUFGKhTf2tl6fwtLAQ"
sticker_SenyaMusic = "CAACAgIAAxkBAAN5Y52tuoIT0mE8rt19HKjlslleG0AAArIiAALpVQUYK_iXa_VksY8sBA"
sticker_SenyaError = "CAACAgIAAxkBAAN8Y52twNjVEmXy3MjiLyNuOdNg1KIAArEiAALpVQUY3ngpjigXTOEsBA"
sticker_SenyaHi = "CAACAgIAAxkBAAO3Y6ATgdKixVoCKGZostyyGt9YULkAArwiAALpVQUYvik5UN2abS0sBA"
sticker_SenyaRock = "CAACAgIAAxkBAAOxY6ATdr2IcCO7iWdRJFspEpVCjCEAArsiAALpVQUYuTSrtJi_KwssBA"
sticker_SenyaChef = "CAACAgIAAxkBAAO0Y6ATeZH88meQV03LVxspYWjeEXcAAsAiAALpVQUYM6XhJVrxZ9ksBA"
sticker_SenyaPopcorn = "CAACAgIAAxkBAAPAY6AUO1oVx1usM9ErpLEp5CsLf_8AAsEiAALpVQUYvMSGKKvP0VIsBA"
sticker_SenyaMoney = "CAACAgIAAxkBAAPMY6AUXTtTZjZfUngk9w_kvJcJFd0AAsMiAALpVQUYuFwVqs21-q8sBA"
sticker_SenyaMiB = "CAACAgIAAxkBAAPSY6AUeAHs9k60vyzNbfkSuQwXYTAAAr0iAALpVQUYyteMrHiAHZUsBA"
sticker_SenyaDance = "CAACAgIAAxkBAAPVY6AUzMd_nVFKwkpbjnbPOdJdJpkAArciAALpVQUYpwqwdssJ89EsBA"
sticker_SenyaMinigun = "CAACAgIAAxkBAAPYY6AU8UZDYJQbVMG3i5xs7wXPmRcAArYiAALpVQUY_40FhveUI88sBA"
sticker_SearchAnswer = [sticker_SenyaMusic,
                        sticker_SenyaRock,
                        sticker_SenyaChef,
                        sticker_SenyaPopcorn,
                        sticker_SenyaMoney,
                        sticker_SenyaMiB,
                        sticker_SenyaDance,
                        sticker_SenyaMinigun]


def author_song(song_path):
    s = song_path.split('/')
    a = s[-2].replace('_', ' ')
    a = a[0].upper() + a[1:]
    b = s[-1].replace('_', ' ')
    b = b[0].upper() + b[1:-4]
    return a + " - " + b


def bold(s):
    return "<b>" + str(s) + "</b>"


def italic(s):
    return "<i>" + str(s) + "</i>"


rnan = italic("nan")
enan = bold("nan")


async def handle_voice(message: types.Message, func, error_message):
    name = str(datetime.now())
    name = name[:10] + name[11:]
    b = 0
    if error_message == error_audio:
        b = 1
    last_query = base.get_user_last_query(message.from_user.id, message.chat.id)
    if last_query != 0:
        if datetime.now() < message_time_delta + datetime.strptime(last_query['date_time'], '%Y-%m-%d %H:%M:%S'):
            return
    try:
        await func(destination_file="./oga/" + name, timeout=1)
    except:
        await message.answer_sticker(sticker_SenyaError)
        await message.answer(size_error)
        base.save_log(message.from_user.id, message.chat.id, "-", b, not b, "", "ОШИБКА СКАЧИВАНИЯ")
        return
    asr_response = asr.transcribe("./oga/" + name)
    if asr_response == "-":
        await message.answer_sticker(sticker_SenyaError)
        await message.answer(error_message)
        base.save_log(message.from_user.id, message.chat.id, "-", b, not b, "", "ОШИБКА ASR")
    else:
        search_response = searcher.find(asr_response).documents
        await message.answer(asr_response)
        db[len(db.keys())] = search_response
        await send_text(message, search_response, len(db.keys()) - 1, 0)
        base.save_log(message.from_user.id, message.chat.id, asr_response, b, not b, "", search_response)


async def help(message: types.Message):
    await message.answer("Если ты мне пришлёшь: \n" \
                         "Текст/аудио-сообщение - получишь наиболее вероятный превод песни\n" \
                         "/top5 - 5 наиболее вероятных переводов предыдущего запроса")


async def send_text(message: types.Message, song_paths, db_id_tmp, number_tmp):
    song = read_song_csv(song_paths[number_tmp])
    eng = song["eng"].values.tolist()
    rus = song["rus"].values.tolist()
    out = ""
    out += bold(eng[0]) + endl
    list_out = []
    for i in range(1, len(eng)):
        r = ""
        e = ""
        if len(rus) > i:
            r = italic(rus[i])
            if r == rnan:
                r = ""
            else:
                r += endl
        if len(eng) > i:
            e = bold(eng[i])
            if e == enan:
                e = ""
            else:
                e += endl
        out += e + r + endl
        if len(out) > symbols:
            list_out.append(out)
            out = ""
    if (out != ""):
        list_out.append(out)

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text=author_song(song_paths[0]),
                             callback_data=top5.new(
                                 db_id=db_id_tmp,
                                 number=0
                             )),
        InlineKeyboardButton(text=author_song(song_paths[1]),
                             callback_data=top5.new(
                                 db_id=db_id_tmp,
                                 number=1
                             )),
        InlineKeyboardButton(text=author_song(song_paths[2]),
                             callback_data=top5.new(
                                 db_id=db_id_tmp,
                                 number=2
                             )),
        InlineKeyboardButton(text=author_song(song_paths[3]),
                             callback_data=top5.new(
                                 db_id=db_id_tmp,
                                 number=3
                             )),
        InlineKeyboardButton(text=author_song(song_paths[4]),
                             callback_data=top5.new(
                                 db_id=db_id_tmp,
                                 number=4
                             ))
    )
    for i in range(0, len(list_out) - 1):
        await message.answer(list_out[i], parse_mode='HTML')
    await message.answer(list_out[-1], parse_mode='HTML', reply_markup=markup)


@dp.callback_query_handler(top5.filter())
async def button_press(call: types.CallbackQuery, callback_data: dict):
    db_id = int(callback_data.get('db_id'))
    number = int(callback_data.get('number'))
    await send_text(db[db_id][0], db[db_id][1], db_id, number)


@dp.message_handler(content_types=[types.ContentType.STICKER])
async def sticker(message: types.Message):
    await message.answer_sticker(message.sticker.file_id)
    await message.answer(message.sticker.file_id)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer_sticker(sticker_SenyaHi)
    await help(message)
    base.save_log(message.from_user.id, message.chat.id, "", 0, 0, "/start", "")


@dp.message_handler(commands=["help"])
async def hell(message: types.Message):
    await message.answer_sticker(sticker_SenyaHelp)
    await help(message)



@dp.message_handler(content_types=[types.ContentType.VOICE])
async def voice(message: types.Message):
    await handle_voice(message, message.voice.download, error_audio)


@dp.message_handler(content_types=[types.ContentType.AUDIO])
async def audio(message: types.Message):
    await handle_voice(message, message.audio.download, error_audio)


@dp.message_handler(content_types=[types.ContentType.DOCUMENT])
async def document(message: types.Message):
    await handle_voice(message, message.document.download, error_document)


@dp.message_handler()
async def text(message: types.Message):
    last_query = base.get_user_last_query(message.from_user.id, message.chat.id)
    if last_query != 0:
        if datetime.now() < message_time_delta + datetime.strptime(last_query['date_time'], '%Y-%m-%d %H:%M:%S'):
            return
    text_response = message.text
    search_response = searcher.find(text_response).documents
    db[len(db.keys())] = [message, search_response]
    await send_text(message, search_response, len(db.keys()) - 1, 0)
    base.save_log(message.from_user.id, message.chat.id, text_response, 0, 0, "text", search_response)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)  # do long polling