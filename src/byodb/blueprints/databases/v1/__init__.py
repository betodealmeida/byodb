"""
Database blueprint.

These endpoints are used for CRUD operations on databases.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

import aiosqlite
from quart import Blueprint, current_app, url_for
from quart_schema import validate_request, validate_response

from byodb.db import get_db
from byodb.constants import DialectEnum
from byodb.errors import ErrorHeaders, ErrorResponse, FullErrorResponse

blueprint = Blueprint("v1/databases", __name__, url_prefix="/api/v1/databases")


def get_database_size(uuid: UUID) -> int:
    """
    Get the size of a database in bytes.
    """
    path = Path(current_app.config["STORAGE"]) / str(uuid)

    return path.stat().st_size if path.exists() else 0


def get_database_not_found_error(uuid: str) -> FullErrorResponse:
    """
    Build an error response for a 404 on a database.
    """
    return (
        ErrorResponse(
            type="https://byodb.net/errors/RFC7807/database-not-found",
            title="Database not found",
            status=404,
            detail=f'The database with uuid "{uuid}" does not exist.',
            instance=url_for("v1/databases.get_database", uuid=uuid, _external=True),
        ),
        404,
        ErrorHeaders(content_type="application/problem+json"),
    )


@dataclass
class Database:
    """
    Base model for a database.
    """

    uuid: UUID
    dialect: DialectEnum
    name: str
    description: str
    created_at: datetime
    last_modified_at: datetime
    size_in_bytes: int

    @staticmethod
    def from_row(row: aiosqlite.Row) -> "Database":
        return Database(
            uuid=UUID(row["uuid"]),
            dialect=DialectEnum(row["dialect"]),
            name=row["name"],
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]),
            last_modified_at=datetime.fromisoformat(row["last_modified_at"]),
            size_in_bytes=get_database_size(row["uuid"]),
        )


@dataclass
class DatabaseCreate:
    """
    Payload for creating a new database.
    """

    dialect: DialectEnum
    name: str
    description: str
    uuid: UUID | None = None


@dataclass
class DatabaseUpdate:
    """
    Payload for updating a database.

    Currently only the name and description can be changed. The `last_modified_at`
    attribute is automatically updated. Changing the UUID, dialect, or `created_at` are
    not allowed for consistency.
    """

    name: str
    description: str


@dataclass
class DatabasesResponse:
    result: list[Database]


@dataclass
class DatabaseResponse:
    result: Database


@dataclass
class DatabaseDeletedResponse:
    result: str


@blueprint.route("/", methods=["GET"])
@validate_response(DatabasesResponse, 200)
async def get_databases() -> DatabasesResponse:
    """
    List all databases.
    """
    async with get_db() as db:
        async with db.execute("SELECT * FROM database") as cursor:
            rows = await cursor.fetchall()

    return DatabasesResponse(result=[Database.from_row(row) for row in rows])


@blueprint.route("/", methods=["POST"])
@validate_request(DatabaseCreate)
@validate_response(DatabaseResponse, 201)
async def create_database(data: DatabaseCreate) -> tuple[DatabaseResponse, int]:
    """
    Create a new database.
    """
    uuid = data.uuid or uuid4()
    created_at = last_modified_at = datetime.utcnow()

    async with aiosqlite.connect(current_app.config["DATABASE"]) as db:
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
                size_in_bytes=0,
            )
        ),
        201,
    )


@blueprint.route("/<uuid>", methods=["GET"])
@validate_response(DatabaseResponse, 200)
@validate_response(ErrorResponse, 404, ErrorHeaders)
async def get_database(uuid: str) -> DatabaseResponse | FullErrorResponse:
    """
    Show a given database.
    """
    async with get_db() as db:
        async with db.execute(
            "SELECT * FROM database WHERE uuid = ?", (uuid,)
        ) as cursor:
            row = await cursor.fetchone()
            return (
                DatabasesResponse(result=Database.from_row(row))
                if row
                else get_database_not_found_error(uuid)
            )


@blueprint.route("/<uuid>", methods=["PATCH"])
@validate_request(DatabaseUpdate)
@validate_response(DatabaseResponse, 200)
@validate_response(ErrorResponse, 404, ErrorHeaders)
async def update_database(uuid: str, data: DatabaseUpdate) -> DatabaseResponse:
    """
    Update an existing database.
    """
    async with get_db() as db:
        async with db.execute(
            "SELECT * FROM database WHERE uuid = ?", (uuid,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return get_database_not_found_error(uuid)

        # update fields
        name = data.name or row["name"]
        description = data.description or row["description"]
        last_modified_at = datetime.utcnow()

        async with db.execute(
            "UPDATE database SET name = ?, description = ?, last_modified_at = ? "
            "WHERE uuid = ?",
            (name, description, last_modified_at, uuid),
        ):
            await db.commit()

    return DatabaseResponse(
        result=Database(
            uuid=row["uuid"],
            dialect=DialectEnum(row["dialect"]),
            name=name,
            description=description,
            created_at=datetime.fromisoformat(row["created_at"]),
            last_modified_at=last_modified_at,
            size_in_bytes=get_database_size(row["uuid"]),
        )
    )


@blueprint.route("/<uuid>", methods=["DELETE"])
@validate_response(DatabaseDeletedResponse, 204)
@validate_response(ErrorResponse, 404, ErrorHeaders)
@validate_response(ErrorResponse, 500, ErrorHeaders)
async def delete_database(
    uuid: str,
) -> tuple[DatabaseDeletedResponse, int] | FullErrorResponse:
    """
    Delete a given database.
    """
    async with aiosqlite.connect(current_app.config["DATABASE"]) as db:
        await db.execute(
            "DELETE FROM database WHERE uuid = ?",
            (uuid,),
        )
        await db.commit()
        affected_rows = db.total_changes

    if affected_rows == 1:
        return DatabaseDeletedResponse(result="OK"), 204

    if affected_rows > 1:
        return (
            ErrorResponse(
                type="https://byodb.net/errors/RFC7807/multiple-primary-keys",
                title="Multiple primary keys found",
                status=500,
                detail=(
                    "More than one database with the same uuid were found (and "
                    "deleted). This should never happen. I blame the goblins."
                ),
                instance=url_for(
                    "v1/databases.delete_database",
                    uuid=uuid,
                    _external=True,
                ),
            ),
            500,
            ErrorHeaders(content_type="application/problem+json"),
        )

    return get_database_not_found_error(uuid)
