import os
import asyncio
import subprocess
import uuid
import yt_dlp

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


def has_audio(path: str) -> bool:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            path,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode == 0 and "audio" in result.stdout


def save_cookies():
    cookies = os.getenv("TIKTOK_COOKIES")
    if not cookies:
        return None

    path = "cookies.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(cookies)

    return path


def download_tiktok(url, filename, cookies_path=None):
    base_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"
        ),
        "Referer": "https://www.tiktok.com/",
    }

    # TikTok отдаёт пары форматов *-0 (видео+звук) и *-1 (только видео).
    # С cookies yt-dlp часто берёт *-1; fallback best[ext=mp4] — тоже без звука.
    strategies = [
        {"format": "download/b[vcodec=h264]/b"},
        {"format": "b[vcodec^=h264]/best[acodec!=none]"},
        {"format": "bestvideo*+bestaudio/bestvideo+bestaudio"},
    ]

    cookie_attempts = []
    if cookies_path:
        cookie_attempts.append(cookies_path)
    cookie_attempts.append(None)

    last_error = None

    for cookies in cookie_attempts:
        for s in strategies:
            try:
                ydl_opts = {
                    "outtmpl": filename,
                    "merge_output_format": "mp4",
                    "noplaylist": True,
                    "quiet": True,
                    "http_headers": base_headers,
                    "format_sort": ["hasaud", "vcodec:h264", "res"],
                    **s,
                }

                if cookies:
                    ydl_opts["cookiefile"] = cookies

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                if (
                    os.path.exists(filename)
                    and os.path.getsize(filename) > 1000
                    and has_audio(filename)
                ):
                    return True

                if os.path.exists(filename):
                    os.remove(filename)

            except Exception as e:
                last_error = e
                if os.path.exists(filename):
                    os.remove(filename)

    raise last_error or RuntimeError("Не удалось скачать видео со звуком")


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Пришли ссылку на TikTok 👇")


@dp.message(F.text)
async def handler(message: Message):
    url = message.text.strip()

    if "tiktok.com" not in url:
        await message.answer("Это не TikTok ссылка ❌")
        return

    status = await message.answer("⏬ Скачиваю видео...")

    filename = f"{uuid.uuid4()}.mp4"
    cookies_path = save_cookies()

    try:
        loop = asyncio.get_event_loop()

        await loop.run_in_executor(
            None,
            download_tiktok,
            url,
            filename,
            cookies_path
        )

        video = FSInputFile(filename)
        await message.answer_video(video=video)

    except Exception as e:
        await message.answer(f"Ошибка:\n{e}")

    finally:
        if os.path.exists(filename):
            os.remove(filename)

        if cookies_path and os.path.exists(cookies_path):
            os.remove(cookies_path)

        await status.delete()


async def main():
    print("BOT STARTED", flush=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())