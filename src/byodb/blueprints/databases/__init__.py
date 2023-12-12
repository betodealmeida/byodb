"""
Database blueprint.

These endpoints are used for CRUD operations on databases.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

import aiosqlite
from quart import Blueprint
from quart_schema import validate_request, validate_response

blueprint = Blueprint("v1/databases", __name__, url_prefix="/api/v1/databases")


class DialectEnum(StrEnum):
    sqlite = "sqlite"


@dataclass
class Database:
    uuid: UUID
    dialect: DialectEnum
    name: str
    description: str
    created_at: datetime
    last_modified_at: datetime


@dataclass
class DatabaseIn:
    dialect: DialectEnum
    name: str
    description: str
    uuid: UUID | None = None


@dataclass
class DatabasesResponse:
    result: list[Database]


@dataclass
class DatabaseResponse:
    result: Database


@blueprint.route("/", methods=["GET"])
@validate_response(DatabasesResponse)
async def get_databases() -> DatabasesResponse:
    """
    List all databases.
    """
    # XXX create_app
    from byodb import app

    result = []
    async with aiosqlite.connect(app.config["DATABASE"]) as db:
        async with db.execute(
            "SELECT uuid, dialect, name, description, created_at, last_modified_at "
            "FROM database"
        ) as cursor:
            async for (
                uuid,
                dialect,
                name,
                description,
                created_at,
                last_modified_at,
            ) in cursor:
                result.append(
                    Database(
                        uuid=UUID(uuid),
                        dialect=DialectEnum(dialect),
                        name=name,
                        description=description,
                        created_at=datetime.fromisoformat(created_at),
                        last_modified_at=datetime.fromisoformat(last_modified_at),
                    )
                )

    return DatabasesResponse(result=result)


@blueprint.route("/<uuid:uuid>", methods=["GET"])
@validate_response(DatabaseResponse)
async def get_database(uuid: UUID) -> DatabaseResponse:
    """
    List a given databases.
    """
    # XXX create_app
    from byodb import app

    async with aiosqlite.connect(app.config["DATABASE"]) as db:
        async with db.execute(
            "SELECT uuid, dialect, name, description, created_at, last_modified_at "
            "FROM database WHERE uuid = ?",
            (str(uuid),),
        ) as cursor:
            (
                uuid,
                dialect,
                name,
                description,
                created_at,
                last_modified_at,
            ) = await cursor.fetchone()
            return DatabasesResponse(
                result=Database(
                    uuid=UUID(uuid),
                    dialect=DialectEnum(dialect),
                    name=name,
                    description=description,
                    created_at=datetime.fromisoformat(created_at),
                    last_modified_at=datetime.fromisoformat(last_modified_at),
                )
            )


@blueprint.route("/", methods=["POST"])
@validate_request(DatabaseIn)
@validate_response(DatabaseResponse)
async def create_database(data: DatabaseIn) -> DatabaseResponse:
    """
    Create a database.
    """
    # XXX create_app
    from byodb import app

    uuid = data.uuid or uuid4()
    created_at = last_modified_at = datetime.utcnow()

    async with aiosqlite.connect(app.config["DATABASE"]) as db:
        await db.execute(
            "INSERT INTO database "
            "(uuid, dialect, name, description, created_at, last_modified_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                str(uuid),
                data.dialect,
                data.name,
                data.description,
                created_at,
                last_modified_at,
            ),
        )
        await db.commit()

    return DatabaseResponse(
        result=Database(
            uuid=uuid,
            dialect=data.dialect,
            name=data.name,
            description=data.description,
            created_at=created_at,
            last_modified_at=last_modified_at,
        )
    )
