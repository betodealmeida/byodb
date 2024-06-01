"""
Main BYODB application.
"""

import asyncio
from pathlib import Path

import aiosqlite
from dotenv import dotenv_values
from quart import Quart, Response, redirect, url_for
from quart_auth import QuartAuth, Unauthorized
from quart_schema import QuartSchema

from byodb.blueprints.auth.v1 import api as auth_v1
from byodb.blueprints.databases.v1 import api as databases_v1
from byodb.blueprints.queries.v1 import api as queries_v1

quart_schema = QuartSchema()
quart_auth = QuartAuth()
auth_manager.user_class = User


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
    quart_auth.init_app(app)

    # blueprints
    app.register_blueprint(auth_v1.blueprint)
    app.register_blueprint(databases_v1.blueprint)
    app.register_blueprint(queries_v1.blueprint)

    # error handlers
    @app.errorhandler(Unauthorized)
    async def redirect_to_login(_: Exception) -> Response:
        """
        Redirect to login.
        """
        return redirect(url_for("auth/v1.login"))

    return app


async def init_db(app: Quart) -> None:
    """
    Create tables.
    """
    async with aiosqlite.connect(app.config["DATABASE"]) as db:
        with open(Path(app.root_path) / "schema.sql", encoding="utf-8") as file_:
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
