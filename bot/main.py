from config import Config
import argparse
from text_base.search_getter import get_searcher
from aiogram import Bot, Dispatcher, executor, types
from nn.ASR_getter import get_asr
from datetime import datetime
import pandas as pd

config = None
token_path = "token.txt"
with open(token_path, "r") as f:
    token = f.read()
parser = argparse.ArgumentParser()
parser.add_argument("--database_path")
parser.add_argument("--index_path")
parser.add_argument("--test", action="store_true", default=False)

args = parser.parse_args()
config = Config(
    database_path=args.database_path,
    index_path=args.index_path,
    test=args.test
)
error_audio = "Извините, это аудио не может быть обработано"
error_document = "Извините, этот документ не может быть обработан"
searcher = get_searcher(config)
asr = get_asr(config)
bot = Bot(token=token)
dp = Dispatcher(bot)
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


async def handle_voice(message: types.Message, func, error_message):
    name = str(datetime.now())
    name = name[:10] + name[11:]
    await func(destination_file="./oga/" + name)
    asr_response = asr.transcribe("./oga/" + name)
    if asr_response == "-":
        await message.answer_sticker(sticker_SenyaError)
        await message.answer(error_message)
    else:
        search_response = searcher.find(asr_response).documents
        await message.answer(asr_response)
        await message.answer(search_response)
        await send_text(message, search_response[0])


async def help(message: types.Message):
    await message.answer("Если ты мне пришлёшь: \n" \
                         "Текст/аудио-сообщение - получишь наиболее вероятный превод песни\n" \
                         "/top5 - 5 наиболее вероятных переводов предыдущего запроса")


async def send_text(message: types.Message, song_path):
    song = pd.read_csv(song_path, delimiter='ÿ')
    await message.answer(song)


@dp.message_handler(content_types=[types.ContentType.STICKER])
async def sticker(message: types.Message):
    await message.answer_sticker(message.sticker.file_id)
    await message.answer(message.sticker.file_id)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer_sticker(sticker_SenyaHi)
    await help(message)


@dp.message_handler(commands=["help"])
async def hell(message: types.Message):
    await message.answer_sticker(sticker_SenyaHelp)
    await help(message)


@dp.message_handler(commands=["top5"])
async def top5(message: types.Message):
    await message.answer("5")


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
    text_response = message.text
    search_response = searcher.find(text_response).documents
    await send_text(message, search_response[0])


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)  # do long polling