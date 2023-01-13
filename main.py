import os

import aiofiles
import orjson
from aiohttp import ClientSession
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

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
async def spotify_get_images(request: Request, data: Data):
    if len(data.id) != 22:
        return Response(orjson.dumps({"error": {"message": "Invalid ID"}}), 400, media_type="application/json")
    data, status = await spotify.get_images(data.id, data.type)
    return Response(orjson.dumps(data), status, media_type="application/json")


if DEBUG:
    import uvicorn
    uvicorn.run(app)
