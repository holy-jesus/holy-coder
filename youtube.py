import asyncio
import os
import glob

from yt_dlp import YoutubeDL


async def delete_file(filenames: list[str]):
    await asyncio.sleep(3600)
    for filename in filenames:
        if os.path.exists(filename):
            os.remove(filename)
    

def match_filter(info_dict, *, incomplete: bool):
    if info_dict.get("is_live", False):
        return "ITS A STREAM!!!!"
    return None


def download_video(loop: asyncio.AbstractEventLoop, video_id: str, audio_only: int):
    format = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4"
    postprocessors = []
    if audio_only:
        format = "bestaudio[ext=m4a]"
        postprocessors.append({"key": "FFmpegVideoConvertor", "preferedformat": "mp3"})

    ydl_options = {
        "outtmpl": {"default": "%(id)s.%(ext)s"},
        "paths": {"home": "/tmp/youtube/", "temp": "/tmp/youtube/"},
        "format": format,
        "postprocessors": postprocessors,
        "match_filter": match_filter,
        "concurrent_fragment_downloads": 5,
    }
    with YoutubeDL(ydl_options) as ydl:
        ydl.download(["https://www.youtube.com/watch?v=" + video_id])
    ext = {0: "mp4", 1: "mp3"}.get(audio_only, None)
    file = f"/tmp/youtube/{video_id}.{ext}"
    with open(f"{file}.done", "w") as f:
        ...
    loop.create_task(delete_file([file, file + ".done"]))
