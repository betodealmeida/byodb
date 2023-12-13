from contextlib import asynccontextmanager

import aiosqlite
from quart import current_app


@asynccontextmanager
async def get_db() -> aiosqlite.Connection:
    async with aiosqlite.connect(current_app.config["DATABASE"]) as db:
        db.row_factory = aiosqlite.Row
        yield db
