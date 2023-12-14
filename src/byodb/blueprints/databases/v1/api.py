"""
Database blueprint.

These endpoints are used for CRUD operations on databases.
"""

from datetime import datetime, timezone
from uuid import uuid4

import aiosqlite
from quart import Blueprint, current_app, url_for
from quart_schema import validate_request, validate_response

from byodb.db import get_db
from byodb.constants import DialectEnum
from byodb.errors import ErrorHeaders, ErrorResponse, FullErrorResponse

from .models import (
    Database,
    DatabaseCreate,
    DatabaseDeletedResponse,
    DatabaseResponse,
    DatabaseUpdate,
    DatabasesResponse,
)
from .utils import get_database_not_found_error, get_database_size

blueprint = Blueprint("databases/v1", __name__, url_prefix="/api/databases/v1")


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
    created_at = last_modified_at = datetime.now(timezone.utc)

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
        last_modified_at = datetime.now(timezone.utc)

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
                    "databases/v1.delete_database",
                    uuid=uuid,
                    _external=True,
                ),
            ),
            500,
            ErrorHeaders(content_type="application/problem+json"),
        )

    return get_database_not_found_error(uuid)
