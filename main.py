import asyncio
import os
import glob

import aiofiles
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
BASE_PATH = os.getcwd()
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

downloaded = {0: {}, 1: {}}


async def open_template(filename: str):
    file = await aiofiles.open(TEMPLATES_PATH + filename, "r")
    content = await file.read()
    await file.close()
    return content


def delete_all_temp_files():
    for file in glob.glob("/tmp/youtube/*.mp*"):
        os.remove(file)


@app.on_event("startup")
async def startup_event():
    global spotify
    spotify = Spotify(ClientSession())
    delete_all_temp_files()


@app.on_event("shutdown")
async def shutdown_event():
    await spotify.session.close()
    delete_all_temp_files()


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
    if id is None:
        return HTMLResponse(await open_template("youtube.html"))
    elif type not in downloaded:
        return Response(
            orjson.dumps({"error": {"message": "Invalid type"}}),
            400,
            media_type="application/json",
        )
    elif id in downloaded[type]:
        return Response(
            orjson.dumps(downloaded[type][id]), media_type="application/json"
        )
    else:
        return Response(
            orjson.dumps({"error": {"message": "Invalid ID"}}),
            400,
            media_type="application/json",
        )


@app.post("/youtube")
@limiter.limit("2/minute")
async def youtube_post(request: Request, data: YoutubeInfo, backgroud_tasks: BackgroundTasks):
    if data.type not in downloaded:
        return Response(
            orjson.dumps({"error": {"message": "Invalid type"}}),
            400,
            media_type="application/json",
        )
    elif data.id not in downloaded[data.type]:
        loop = asyncio.get_event_loop()
        backgroud_tasks.add_task(download_video, downloaded, loop, data.id, data.type)
        return Response(orjson.dumps(False), 200, media_type="application/json")
    else:
        return Response(orjson.dumps(downloaded[data.type][data.id]), 200, media_type="application/json")


@app.get("/youtube/download")
async def youtube_download(id: str, type: int):
    if type not in downloaded:
        return Response(
            orjson.dumps({"error": {"message": "Invalid type"}}),
            400,
            media_type="application/json",
        )
    elif id not in downloaded[type]:
        return Response(
            orjson.dumps({"error": {"message": "Invalid ID"}}),
            400,
            media_type="application/json",
        )
    else:
        ext = "mp3" if type else "mp4"
        filename = "audio" if type else "video"
        return FileResponse(
            f"/tmp/youtube/{id}.{ext}",
            filename=f"{filename}.{ext}",
        )


if DEBUG:
    import uvicorn

    uvicorn.run(app)


"""
Добавить отдельное окошко для ошибок, сделать это окошко в функцию которая принимает текст ошибки и элемент данного окна, в котором произошла ошибка.
Красиво, удобно круто 
"""
