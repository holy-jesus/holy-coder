import asyncio
from os import getcwd

import aiofiles
import yt_dlp
from aiofiles import os
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


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
    ext = {0: "mp4", 1: "mp3"}.get(audio_only, None)
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
    loop.create_task(update_db(info))
    loop.create_task(delete(video_id))


DEBUG = __name__ == "__main__"
BASE_PATH = getcwd()
TEMPLATES_PATH = BASE_PATH + "/static/html/"


app = FastAPI(
    redoc_url=None,
    docs_url=None,
)
app.mount("/static", StaticFiles(directory="./static"), name="static")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


async def open_template(filename: str):
    async with aiofiles.open(TEMPLATES_PATH + filename, "r") as f:
        content = await f.read()
    return content


@app.get("/")
async def youtube(id: str = None, type: int = None):
    if id is None:
        return HTMLResponse(await open_template("youtube.html"))
    elif type not in (0, 1):
        return InvalidType
    video = await db.youtube.find_one({"_id": id, "type": type})
    if not video:
        return InvalidID
    else:
        return JSONResponse(video["status"])


@app.post("/")
@limiter.limit("2/minute")
async def youtube_post(
    request: Request, data: dict, backgroud_tasks: BackgroundTasks
):
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
        return JSONResponse(video["status"])


@app.get("/download")
async def youtube_download(id: str, type: int):
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
