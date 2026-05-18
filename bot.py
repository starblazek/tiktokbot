import os
import asyncio
import uuid
import yt_dlp

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Пришли ссылку на TikTok 👇")


@dp.message()
async def download(message: Message):
    url = message.text.strip()

    if "tiktok.com" not in url:
        await message.answer("Это не TikTok ссылка")
        return

    status = await message.answer("Скачиваю видео...")

    file_id = str(uuid.uuid4())
    filename = f"{file_id}.mp4"

    ydl_opts = {
        "outtmpl": filename,
        "format": "mp4",
        "quiet": True,
        "noplaylist": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        video = FSInputFile(filename)
        await message.answer_video(video=video)

    except Exception as e:
        await message.answer(f"Ошибка:\n{e}")

    finally:
        if os.path.exists(filename):
            os.remove(filename)

        await status.delete()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())