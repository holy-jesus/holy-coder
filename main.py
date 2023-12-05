from os import getcwd
import glob

from aiofiles import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from translation import TRANSLATION

DEBUG = __name__ == "__main__"
BASE_PATH = getcwd()

async def delete_all_temp_files():
    for file in glob.glob("/tmp/youtube/*"):
        await os.remove(file)


async def lifespan(_):
    await db.drop_collection("youtube")
    try:
        if (await os.path.exists("/tmp/youtube/")):
            await delete_all_temp_files()
        else:
            await os.mkdir("/tmp/youtube/")
    except Exception:
        pass
    yield
    await db.drop_collection("youtube")
    await delete_all_temp_files()

app = FastAPI(title="holy-coder", redoc_url=None, docs_url=None, debug=DEBUG, routes=[], lifespan=lifespan)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

templates = Jinja2Templates(directory="templates")

def get_language(request: Request):
    language = request.cookies.get("language", None)
    if not language:
        accept_language = request.headers.get("accept-language", None)
        if not accept_language:
            return TRANSLATION["EN"]
        splitted = accept_language.split(",")
        for language in splitted:
            if language.startswith("en"):
                return TRANSLATION["EN"]
            elif language.startswith("ru"):
                return TRANSLATION["RU"]
        return TRANSLATION["EN"]
    elif language in ("ru", "en"):
        return TRANSLATION[language.upper()]


try:
    from mounts import youtube, spotify
    from connection import db
except ImportError:
    from .mounts import youtube, spotify
    from .connection import db


@app.exception_handler(404)
async def NotFound(request: Request, exc):
    return RedirectResponse("/")


@app.get("/")
async def index(request: Request):
    T = get_language(request)
    return templates.TemplateResponse("index.html", {"request": request, "window": "main", "T": T})


@app.get("/youtube/")
async def youtube_redirect():
    return RedirectResponse("/youtube")


@app.get("/spotify/")
async def youtube_redirect():
    return RedirectResponse("/spotify")


app.mount("/static", StaticFiles(directory="./static"), name="static")
app.include_router(youtube)
app.include_router(spotify)

if DEBUG:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0")
