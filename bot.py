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

    file_id = str(uuid.uuid4())
    filename = f"{file_id}.mp4"

    # ВАЖНО: правильная сборка видео + аудио
    ydl_opts = {
        "outtmpl": filename,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True
    }

    try:
        loop = asyncio.get_event_loop()

        # yt-dlp блокирующий → уводим в thread
        def download_video():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        await loop.run_in_executor(None, download_video)

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