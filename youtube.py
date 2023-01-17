import asyncio
import os

from yt_dlp import YoutubeDL


async def delete_file(id: str, type: int, downloaded: dict):
    await asyncio.sleep(3600)
    ext = "mp3" if type else "mp4"
    file = f"/tmp/youtube/{id}.{ext}"
    if os.path.exists(file):
        os.remove(file)
    downloaded[type].pop(id, None)


def match_filter(info_dict, *, incomplete: bool):
    if info_dict.get("is_live", False):
        return "ITS A STREAM!!!!"
    return None


def download_video(
    downloaded: dict, loop: asyncio.AbstractEventLoop, video_id: str, audio_only: int
):
    downloaded[audio_only][video_id] = False
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
    if os.path.exists(f"/tmp/youtube/{video_id}.{'mp3' if audio_only else 'mp4'}"):
        downloaded[audio_only][video_id] = True
    else:
        downloaded[audio_only][video_id] = None
    loop.create_task(delete_file(video_id, audio_only, downloaded))
