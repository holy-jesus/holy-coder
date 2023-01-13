import os

from aiohttp import ClientSession
import aiofiles
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


try:
    from spotify import Spotify
except ImportError:
    from .spotify import Spotify

DEBUG = __name__ == "__main__"
BASE_PATH = os.getcwd()
TEMPLATES_PATH = BASE_PATH + "/static/html/"


class Data(BaseModel):
    id: str
    type: str


app = FastAPI(debug=DEBUG)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.mount("/static", StaticFiles(directory="./static"), name="static")


async def open_template(filename: str):
    file = await aiofiles.open(TEMPLATES_PATH + filename, "r")
    content = await file.read()
    await file.close()
    return content


@app.on_event("startup")
async def startup_event():
    global spotify
    spotify = Spotify(ClientSession())
    await spotify.get_token()
    # await spotify.get_internal_client_token()
    # await spotify.get_internal_authorization()

@app.on_event("shutdown")
async def shutdown_event():
    await spotify.session.close()

@app.get("/", response_class=HTMLResponse)
async def index():
    return await open_template("index.html")


@app.get("/spotify", response_class=HTMLResponse)
async def spotify_page():
    return await open_template("spotify.html")


@app.post("/spotify")
@limiter.limit("5/minute")
async def spotify_post(request: Request, data: Data):
    images = await spotify.get_images(data.id, data.type)
    return images


if DEBUG:
    import uvicorn
    uvicorn.run(app)
