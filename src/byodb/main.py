"""
Main BYODB application.
"""

import asyncio
from pathlib import Path

import aiosqlite
from dotenv import dotenv_values
from quart import Quart
from quart_schema import QuartSchema

from byodb.blueprints.databases.v1 import api as databases_v1
from byodb.blueprints.queries.v1 import api as queries_v1 


quart_schema = QuartSchema()


def create_app(test_config: dict[str, str] | None = None) -> Quart:
    """
    Initialize the app, with extensions and blueprints.
    """
    app = Quart(__name__)

    # configuration
    app.config.update(dotenv_values(".env"))
    if test_config:
        app.config.from_mapping(test_config)

    # extensions
    quart_schema.init_app(app)

    # blueprints
    app.register_blueprint(databases_v1.blueprint)
    app.register_blueprint(queries_v1.blueprint)

    return app


async def init_db(app: Quart) -> None:
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
    app = create_app()
    asyncio.run(init_db(app))


def run() -> None:
    """
    Main app.
    """
    app = create_app()
    app.run()
