"""
Database blueprint.

These endpoints are used for CRUD operations on databases.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

import aiosqlite
from quart import Blueprint, url_for
from quart_schema import validate_request, validate_response

blueprint = Blueprint("v1/databases", __name__, url_prefix="/api/v1/databases")


@dataclass
class ErrorResponse:
    """
    A problem detail as defined in RFC 7807.

    See https://www.rfc-editor.org/rfc/rfc7807.
    """

    type: str
    title: str
    status: int
    detail: str
    instance: str


@dataclass
class ErrorHeaders:
    """
    Headers for an error response.
    """

    content_type: str = "application/problem+json"


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
    # size_in_bytes: int

    @staticmethod
    def from_row(row: aiosqlite.Row) -> "Database":
        return Database(
            uuid=UUID(row["uuid"]),
            dialect=DialectEnum(row["dialect"]),
            name=row["name"],
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]),
            last_modified_at=datetime.fromisoformat(row["last_modified_at"]),
        )


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
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT uuid, dialect, name, description, created_at, last_modified_at "
            "FROM database"
        ) as cursor:
            async for row in cursor:
                result.append(Database.from_row(row))

    return DatabasesResponse(result=result)


@blueprint.route("/<uuid>", methods=["GET"])
@validate_response(DatabaseResponse)
@validate_response(ErrorResponse, 404, ErrorHeaders)
async def get_database(uuid: str) -> DatabaseResponse:
    """
    List a given database.
    """
    # XXX create_app
    from byodb import app

    async with aiosqlite.connect(app.config["DATABASE"]) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT uuid, dialect, name, description, created_at, last_modified_at "
            "FROM database WHERE uuid = ?",
            (uuid,),
        ) as cursor:
            row = await cursor.fetchone()

            if row is None:
                return (
                    ErrorResponse(
                        type="https://byodb.net/problems/database-not-found",
                        title="Database not found",
                        status=404,
                        detail=f"The database with uuid {uuid} does not exist.",
                        instance=url_for("v1/databases.get_database", uuid=uuid),
                    ),
                    404,
                    {"Content-Type": "application/problem+json"},
                )

            return DatabasesResponse(result=Database.from_row(row))


@blueprint.route("/<uuid:uuid>", methods=["DELETE"])
async def delete_database(uuid: UUID) -> tuple[str, int]:
    """
    Delete a given databases.
    """
    # XXX create_app
    from byodb import app

    async with aiosqlite.connect(app.config["DATABASE"]) as db:
        await db.execute(
            "DELETE FROM database WHERE uuid = ?",
            (str(uuid),),
        )
        await db.commit()

    # 403, 404
    return "", 204


@blueprint.route("/", methods=["POST"])
@validate_request(DatabaseIn)
@validate_response(DatabaseResponse, 201)
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

    return (
        DatabaseResponse(
            result=Database(
                uuid=uuid,
                dialect=data.dialect,
                name=data.name,
                description=data.description,
                created_at=created_at,
                last_modified_at=last_modified_at,
            )
        ),
        201,
    )
