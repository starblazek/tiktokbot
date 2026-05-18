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

    ydl_opts = {
        "outtmpl": filename,

        # 🔥 САМОЕ ВАЖНОЕ
        "format": "best[ext=mp4]/best",

        "merge_output_format": "mp4",

        "noplaylist": True,
        "quiet": True,

        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0 Safari/537.36"
            ),
            "Referer": "https://www.tiktok.com/"
        }
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

        await status.delete()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())