import os
from typing import TYPE_CHECKING

from motor.motor_asyncio import AsyncIOMotorClient
import dotenv

if TYPE_CHECKING:
    from motor import core

dotenv.load_dotenv(os.path.expanduser("~/.env"))

db: "core.Database" = AsyncIOMotorClient(
    os.getenv("mongodb_link"), connect=False
).holy_coder
