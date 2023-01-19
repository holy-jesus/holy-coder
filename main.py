import asyncio
from os import getcwd
import glob

import aiofiles
from aiofiles import os
import orjson
from aiohttp import ClientSession
from fastapi import BackgroundTasks, FastAPI, Request, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

try:
    from spotify import Spotify
    from youtube import download_video
except ImportError:
    from .spotify import Spotify
    from .youtube import download_video

DEBUG = __name__ == "__main__"
BASE_PATH = getcwd()
TEMPLATES_PATH = BASE_PATH + "/static/html/"


class SpotifyInfo(BaseModel):
    id: str
    type: str


class YoutubeInfo(BaseModel):
    id: str
    type: int  # 0: For video, 1: For audio_only


app = FastAPI(
    title="holy-coder",
    redoc_url=None,
    docs_url=None,
    debug=DEBUG,
)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.mount("/static", StaticFiles(directory="./static"), name="static")


async def open_template(filename: str):
    async with aiofiles.open(TEMPLATES_PATH + filename, "r") as f:
        content = await f.read()
    return content

async def read_status_file(id: str, type: int):
    async with aiofiles.open(f"/tmp/youtube/{id}{type}", "rb") as f:
        json = orjson.loads(await f.read())
    return json

async def delete_all_temp_files():
    for file in glob.glob("/tmp/youtube/*"):
        await os.remove(file)


@app.on_event("startup")
async def startup_event():
    global spotify
    spotify = Spotify(ClientSession())
    await delete_all_temp_files()
    if not await os.path.exists("/tmp/youtube/"):
        await os.mkdir("/tmp/youtube/")


@app.on_event("shutdown")
async def shutdown_event():
    await spotify.session.close()
    await delete_all_temp_files()


@app.get("/", response_class=HTMLResponse)
async def index():
    return await open_template("index.html")


@app.get("/spotify", response_class=HTMLResponse)
async def spotify_page():
    return await open_template("spotify.html")


@app.post("/spotify")
@limiter.limit("5/minute")
async def spotify_get_images(request: Request, data: SpotifyInfo):
    if len(data.id) != 22:
        return Response(
            orjson.dumps({"error": {"message": "Invalid ID"}}),
            400,
            media_type="application/json",
        )
    data, status = await spotify.get_images(data.id, data.type)
    return Response(orjson.dumps(data), status, media_type="application/json")


@app.get("/youtube")
async def youtube(id: str = None, type: int = None):
    status_file = f"/tmp/youtube/{id}{type}"
    status_file_exists = await os.path.exists(status_file)
    if id is None:
        return HTMLResponse(await open_template("youtube.html"))
    elif type not in (0, 1):
        return Response(
            orjson.dumps({"error": {"message": "Invalid type"}}),
            400,
            media_type="application/json",
        )
    elif not status_file_exists:
        return Response(
            orjson.dumps({"error": {"message": "Invalid ID"}}),
            400,
            media_type="application/json",
        )
    else:
        info = await read_status_file(id, type)
        return Response(orjson.dumps(info["status"]), media_type="application/json")


@app.post("/youtube")
@limiter.limit("2/minute")
async def youtube_post(
    request: Request, data: YoutubeInfo, backgroud_tasks: BackgroundTasks
):
    status_file = f"/tmp/youtube/{data.id}{data.type}"
    status_file_exists = await os.path.exists(status_file)
    if data.type not in (0, 1):
        return Response(
            orjson.dumps({"error": {"message": "Invalid type"}}),
            400,
            media_type="application/json",
        )
    elif not status_file_exists:
        loop = asyncio.get_event_loop()
        backgroud_tasks.add_task(download_video, loop, data.id, data.type)
        return Response(orjson.dumps(False), media_type="application/json")
    else:
        info = await read_status_file(data.id, data.type)
        return Response(orjson.dumps(info["status"]), media_type="application/json")


@app.get("/youtube/download")
async def youtube_download(id: str, type: int):
    status_file = f"/tmp/youtube/{id}{type}"
    status_file_exists = await os.path.exists(status_file)
    if type not in (0, 1):
        return Response(
            orjson.dumps({"error": {"message": "Invalid type"}}),
            400,
            media_type="application/json",
        )
    elif not status_file_exists:
        return Response(
            orjson.dumps({"error": {"message": "Invalid ID"}}),
            400,
            media_type="application/json",
        )
    else:
        info = await read_status_file(id, type)
        if info["status"]:
            return FileResponse(
                info["path"],
                filename=info["filename"]
            )
        else:
            return Response(
                orjson.dumps({"error": {"message": "Invalid ID"}}),
                400,
                media_type="application/json",
            )
    


if DEBUG:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0")


"""
Добавить отдельное окошко для ошибок, сделать это окошко в функцию которая принимает текст ошибки и элемент данного окна, в котором произошла ошибка.
Красиво, удобно круто 
"""
