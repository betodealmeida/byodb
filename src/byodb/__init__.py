"""
Main BYODB application.
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path

import aiosqlite
from importlib.metadata import version
from quart import Quart
from quart_schema import QuartSchema, validate_response

from byodb.blueprints import databases

app = Quart(__name__)
app.register_blueprint(databases.blueprint)

QuartSchema(app)

app.config.update(
    {
        "DATABASE": Path(app.root_path) / "byodb.sqlite",
    }
)


async def init_db() -> None:
    """
    Create tables.
    """
    async with aiosqlite.connect(app.config["DATABASE"]) as db:
        with open(Path(app.root_path) / "schema.sql", mode="r") as file_:
            await db.executescript(file_.read())
        await db.commit()


def init_db_sync():
    """
    Synchronous wrapper of `init_db` for Poetry.
    """
    asyncio.run(init_db())


@dataclass
class HealthCheck:
    status: str
    version: str


@app.get("/health")
@validate_response(HealthCheck)
async def health() -> HealthCheck:
    """
    Application health check.
    This endpoint is used to check the health and version of the application.
    """
    return HealthCheck(status="OK", version=version("byodb"))


def run() -> None:
    """
    Main app.
    """
    app.run()
