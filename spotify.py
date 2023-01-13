import os
from base64 import b64encode
from random import choice
from time import time

from aiohttp import ClientSession
import orjson
from bs4 import BeautifulSoup
from cache import AsyncTTL
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.env"))

SPOTIFY_APP_VERSION = "1.2.3.1014.g0e1c4b4e"
CHROME_USER_AGENT = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
]
FIREFOX_USER_AGENT = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.1; rv:108.0) Gecko/20100101 Firefox/108.0",
    "Mozilla/5.0 (X11; Linux i686; rv:108.0) Gecko/20100101 Firefox/108.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:108.0) Gecko/20100101 Firefox/108.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0",
]
OPERA_USER_AGENT = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 OPR/94.0.4606.65",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 OPR/94.0.4606.65",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 OPR/94.0.4606.65",
]


def get_random_user_agent():
    browser = choice((CHROME_USER_AGENT, FIREFOX_USER_AGENT, OPERA_USER_AGENT))
    return choice(browser)


class Spotify:
    def __init__(self, session: ClientSession) -> None:
        self.session: ClientSession = session
        self.official_api = {"token": "", "expires": 0}
        self.internal_api = {
            "client-id": "",
            "authorization": "",
            "authorization-expires": 0,
            "client-token": "",
            "client-token-expires": 0,
        }
        self.official_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.internal_headers = {
            "Accept-Language": "en-US,en;q=0.5",
            "Origin": "https://open.spotify.com",
            "Referer": "https://open.spotify.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "TE": "trailers",
            "User-Agent": get_random_user_agent(),
        }
        self.internal_headers.update(
            {
                "app-platform": "WebPlayer",
                "spotify-app-version": SPOTIFY_APP_VERSION,
                "Origin": "https://open.spotify.com",
                "Referer": "https://open.spotify.com/",
            }
        )

    async def get_token(self):
        basic = b64encode(
            f"{os.getenv('holy_coder_spotify_client_id')}:{os.getenv('holy_coder_spotify_client_secret')}".encode(
                "ascii"
            )
        ).decode("ascii")
        response = await self.session.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {basic}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "client_credentials"},
        )
        json = await response.json(loads=orjson.loads)
        self.official_api["token"] = json["access_token"]
        self.official_api["expires"] = time() + json["expires_in"]
        self.official_headers["Authorization"] = f"Bearer {self.official_api['token']}"

    async def get_internal_authorization(self):
        response = await self.session.get(
            "https://open.spotify.com/user/spotify", headers=self.internal_headers
        )
        soup = BeautifulSoup(await response.text(), "lxml")
        raw_js = soup.find("script", {"id": "session"}).get_text()
        session_info = orjson.loads(raw_js)
        self.internal_api["authorization"] = session_info["accessToken"]
        self.internal_api["authorization-expires"] = (
            session_info["accessTokenExpirationTimestampMs"] / 1000
        )
        self.internal_api["client-id"] = session_info["clientId"]

    async def get_internal_client_token(self):
        if (
            not self.internal_api["authorization"]
            or time() >= self.internal_api["authorization-expires"]
        ):
            await self.get_internal_authorization()
        headers = self.internal_headers.copy()
        headers["content-type"] = "application/json"
        headers["Accept"] = "application/json"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Origin"] = "https://open.spotify.com"
        headers["Referer"] = "https://open.spotify.com/"
        post_data = {
            "client_data": {
                "client_version": SPOTIFY_APP_VERSION,
                "client_id": self.internal_api["client-id"],
                "js_sdk_data": {
                    "device_brand": "unknown",
                    "device_model": "desktop",
                    "os": "Linux",
                    "os_version": "unknown",
                },
            }
        }
        response = await self.session.post(
            "https://clienttoken.spotify.com/v1/clienttoken",
            headers=headers,
            json=post_data,
        )
        text = await response.text()
        token_info = orjson.loads(text)
        self.internal_api["client-token"] = token_info["granted_token"]["token"]
        self.internal_api["client-token-expires"] = time() + int(
            token_info["granted_token"]["refresh_after_seconds"]
        )

    @AsyncTTL(time_to_live=86400, maxsize=512)
    async def get_images(self, id: str, type: str):
        if type in ("track", "album", "playlist", "user"):
            if not self.official_api["token"] or time() >= self.official_api["expires"]:
                await self.get_token()
            headers = self.official_headers.copy()
            headers["Authorization"] = f"Bearer {self.official_api['token']}"
            json = await self._make_request(
                f"https://api.spotify.com/v1/{type}s/{id}",
                headers=headers,
                params={"fields": "images"} if type == "playlist" else None,
            )
            if "error" in json:
                return json
            elif type == "track":
                return {"data": json["album"]["images"]}
            return {"data": json["images"]}
        else:
            if (
                not self.internal_api["client-token"]
                or time() >= self.internal_api["client-token-expires"]
            ):
                await self.get_internal_client_token()
            if (
                not self.internal_api["authorization"]
                or time() >= self.internal_api["authorization-expires"]
            ):
                await self.get_internal_authorization()
            variables = {"uri": f"spotify:artist:{id}", "locale": ""}
            extensions = {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "0b84fdc8c874d3020a119be614b8f0ee0f08c69c1c37aeb0a8b17758f63ef7fe",
                }
            }
            params = {
                "operationName": "queryArtistOverview",
                "variables": orjson.dumps(variables).decode("utf-8"),
                "extensions": orjson.dumps(extensions).decode("utf-8"),
            }
            headers = self.internal_headers.copy()
            headers["authorization"] = f"Bearer {self.internal_api['authorization']}"
            headers["client-token"] = self.internal_api["client-token"]
            json = await self._make_request(
                f"https://api-partner.spotify.com/pathfinder/v1/query",
                headers=headers,
                params=params,
            )
            visuals = json["data"]["artistUnion"]["visuals"]
            images = []
            for i in visuals["gallery"]["items"]:
                for source in i["sources"]:
                    images.append(source)
            images += visuals["avatarImage"]["sources"]
            images += visuals["headerImage"]["sources"]
            return {"data": images}

    async def _make_request(self, url: str, headers: dict, params: dict | None = None):
        response = await self.session.get(
            url,
            headers=headers,
            params=params,
        )
        return await response.json(loads=orjson.loads)
