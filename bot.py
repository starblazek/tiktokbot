import os
import asyncio
import uuid
import yt_dlp

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


def save_cookies():
    """Создаём cookies.txt из Railway variable"""
    cookies = os.getenv("TIKTOK_COOKIES")

    if not cookies:
        return None

    path = "cookies.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(cookies)

    return path


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Пришли ссылку на TikTok 👇")


@dp.message(F.text)
async def download(message: Message):
    url = message.text.strip()

    if "tiktok.com" not in url:
        await message.answer("Это не TikTok ссылка ❌")
        return

    status = await message.answer("⏬ Скачиваю видео...")

    filename = f"{uuid.uuid4()}.mp4"

    cookies_path = save_cookies()

    ydl_opts = {
        "outtmpl": filename,
        "quiet": False,
        "noplaylist": True,
        "dump_single_json": True,
    }

    try:
        loop = asyncio.get_event_loop()

        def run_download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        await loop.run_in_executor(None, run_download)

        if not os.path.exists(filename):
            await message.answer("Не удалось скачать видео 😢")
            return

        video = FSInputFile(filename)
        await message.answer_video(video=video)

    except Exception as e:
        await message.answer(f"Ошибка:\n{str(e)}")

    finally:
        if os.path.exists(filename):
            os.remove(filename)

        if cookies_path and os.path.exists(cookies_path):
            os.remove(cookies_path)

        await status.delete()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())