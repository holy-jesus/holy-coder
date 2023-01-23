import asyncio
import orjson

import aiofiles
from aiofiles import os
import yt_dlp


PATH = "/tmp/youtube/"


async def delete_file(status_file):
    async with aiofiles.open(status_file) as f:
        info = orjson.loads(await f.read())
    await asyncio.sleep(3600)
    for filename in [status_file, info["path"]]:
        if not filename:
            continue
        elif await os.path.exists(filename):
            await os.remove(filename)


def match_filter(info_dict, *, incomplete: bool):
    if info_dict.get("is_live", False):
        return "It's stream, skipping"
    return None


def download_video(loop: asyncio.AbstractEventLoop, video_id: str, audio_only: int):
    downloadable = True
    ext = {0: "mp4", 1: "mp3"}.get(audio_only, None)
    info = {"status": False, "path": None, "filename": None}
    status_file = PATH + f"{video_id}{audio_only}"
    with open(status_file, "wb") as f:
        f.write(orjson.dumps(info))
    format = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4"
    postprocessors = []
    if audio_only:
        format = "bestaudio[ext=m4a]"
        postprocessors.append({"key": "FFmpegVideoConvertor", "preferedformat": "mp3"})

    ydl_options = {
        "outtmpl": {"default": "%(id)s.%(ext)s"},
        "paths": {"home": PATH, "temp": PATH},
        "format": format,
        "postprocessors": postprocessors,
        "match_filter": match_filter,
        "concurrent_fragment_downloads": 5,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_options) as ydl:
            a = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}")
            title = a["title"]
            downloadable = not a["is_live"]
    except Exception:
        downloadable = False
    if downloadable:
        info["status"] = True
        info["path"] = PATH + f"{video_id}.{ext}"
        info["filename"] = f"{title}.{ext}"
    else:
        info["status"] = None
    with open(status_file, "wb") as f:
        f.write(orjson.dumps(info))
    loop.create_task(delete_file(status_file))
