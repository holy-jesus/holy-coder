from os import getcwd
import glob

import aiofiles
from aiofiles import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


try:
    from mounts import youtube, spotify
    from connection import db
except ImportError:
    from .mounts import youtube, spotify
    from .connection import db

DEBUG = __name__ == "__main__"
BASE_PATH = getcwd()
TEMPLATES_PATH = BASE_PATH + "/static/html/"


main = FastAPI(
    title="holy-coder", redoc_url=None, docs_url=None, debug=DEBUG, routes=[]
)


async def open_template(filename: str):
    async with aiofiles.open(TEMPLATES_PATH + filename, "r") as f:
        content = await f.read()
    return content


async def delete_all_temp_files():
    for file in glob.glob("/tmp/youtube/*"):
        await os.remove(file)


@main.on_event("startup")
async def startup_event():
    await db.drop_collection("youtube")
    if await os.path.exists("/tmp/youtube/"):
        await delete_all_temp_files()
    else:
        await os.mkdir("/tmp/youtube/")


@main.on_event("shutdown")
async def shutdown_event():
    await db.drop_collection("youtube")
    await delete_all_temp_files()


@main.get("/")
async def index():
    return HTMLResponse(await open_template("index.html"))


main.mount("/static", StaticFiles(directory="./static"), name="static")
main.mount("/youtube", youtube)
main.mount("/spotify", spotify)

if DEBUG:
    import uvicorn

    uvicorn.run(main, host="0.0.0.0")
