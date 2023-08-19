import asyncio

import requests
import yt_dlp
import eyed3
from eyed3.id3.frames import ImageFrame
from aiofiles import os
from fastapi import BackgroundTasks, APIRouter, Request
from fastapi.responses import FileResponse, JSONResponse

from main import limiter, templates, get_language
from connection import db

PATH = "/tmp/youtube/"
InvalidID = JSONResponse({"error": {"message": "Invalid ID"}}, 400)
InvalidType = JSONResponse({"error": {"message": "Invalid type"}}, 400)


async def update_db(info):
    await db.youtube.update_one({"_id": info["_id"]}, {"$set": info})


async def delete(video_id):
    await asyncio.sleep(3600)
    info = await db.youtube.find_one_and_delete({"_id": video_id})
    if info["status"] and await os.path.exists(info["path"]):
        await os.remove(info["path"])


def match_filter(info_dict, *, incomplete: bool):
    if info_dict.get("is_live", False):
        return "It's stream, skipping"
    return None


def download_video(loop: asyncio.AbstractEventLoop, info):
    downloadable = True
    video_id = info["_id"]
    audio_only = info["type"]
    ext = {0: "mp4", 1: "mp3"}.get(audio_only)
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
            video_info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}")
            title = video_info["title"]
            downloadable = not video_info["is_live"]
    except Exception:
        downloadable = False
    if downloadable:
        info["status"] = True
        info["path"] = PATH + f"{video_id}.{ext}"
        info["filename"] = f"{title}.{ext}"
        if audio_only:
            add_metadata(info, video_info)
    else:
        info["status"] = None
    loop.create_task(update_db(info))
    loop.create_task(delete(video_id))


def remove_useless_text(string: str):
    USELESS = ("video", "music", "audio", "official", "hd", "lyric")
    idx = -1
    while True:
        idx = string.find("(", idx + 1)
        if idx == -1:
            break
        another_open_bracket = string.find("(", idx + 1)
        closing_bracket = string.find(")", idx + 1)
        if closing_bracket == -1 or (
            another_open_bracket != -1 and another_open_bracket < closing_bracket
        ):
            break
        if all(
            word.lower().replace("(", "").replace(")", "") in USELESS
            for word in string[idx : closing_bracket + 1].split()
        ):
            string = string[0:idx] + string[closing_bracket + 1 : len(string) + 1]
    return string.strip()


def get_artist_and_title(video_info: dict):
    title = remove_useless_text(video_info.get("fulltitle", video_info["title"]))
    if " - " in title:
        return title.split(" - ", 1)
    return video_info["channel"], title


def add_metadata(info: dict, video_info: dict):
    try:
        audio = eyed3.load(info["path"])
        if (audio.tag == None):
            audio.initTag()
        response = requests.get(video_info["thumbnail"])
        artist, title = get_artist_and_title(video_info)
        audio.tag.title = title
        audio.tag.artist = artist
        audio.tag.images.set(ImageFrame.FRONT_COVER, response.content, 'image/jpeg')
        audio.tag.save()
    except Exception as e:
        print(e)

youtube = APIRouter()


@youtube.get("/youtube")
async def youtube_index(request: Request, id: str = None, type: int = None):
    if id is None:
        T = get_language(request)
        return templates.TemplateResponse(
            "index.html", {"request": request, "window": "youtube", "T": T}
        )
    elif len(id) != 11:
        return InvalidID
    elif type not in (0, 1):
        return InvalidType
    video = await db.youtube.find_one({"_id": id, "type": type})
    if not video:
        return InvalidID
    else:
        if video["status"]:
            return JSONResponse(video["filename"])
        return JSONResponse(video["status"])


@youtube.post("/youtube")
@limiter.limit("2/minute")
async def youtube_post(request: Request, data: dict, backgroud_tasks: BackgroundTasks):
    if data["type"] not in (0, 1):
        return InvalidType
    elif len(data["id"]) != 11:
        return InvalidID
    video = await db.youtube.find_one({"_id": data["id"], "type": data["type"]})
    if not video:
        loop = asyncio.get_event_loop()
        info = {
            "_id": data["id"],
            "type": data["type"],
            "status": False,
            "path": None,
            "filename": None,
        }
        backgroud_tasks.add_task(download_video, loop, info)
        await db.youtube.update_one({"_id": data["id"]}, {"$set": info}, upsert=True)
        return JSONResponse(False)
    else:
        if video["status"]:
            return JSONResponse(video["filename"])
        return JSONResponse(video["status"])


@youtube.get("/youtube/{filename}")
async def youtube_download(id: str, type: int, filename: str):
    if type not in (0, 1):
        return InvalidType
    elif len(id) != 11:
        return InvalidID
    else:
        video = await db.youtube.find_one({"_id": id, "type": type})
        if not video:
            return InvalidID
        elif video["status"]:
            return FileResponse(video["path"], filename=video["filename"])
        else:
            return InvalidID
