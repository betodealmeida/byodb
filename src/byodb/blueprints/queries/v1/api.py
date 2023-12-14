"""
Queries blueprint.
"""

from datetime import datetime, timezone
from pathlib import Path

import aiosqlite
from quart import Blueprint, current_app, url_for
from quart_schema import validate_request, validate_response

from byodb.db import get_db
from byodb.errors import ErrorHeaders, ErrorResponse, FullErrorResponse

from .models import Query, QueryCreate, QueryResponse, QueryResults

blueprint = Blueprint("queries/v1", __name__, url_prefix="/api/queries/v1")


@blueprint.route("/", methods=["POST"])
@validate_request(QueryCreate)
@validate_response(QueryResponse, 201)
@validate_response(ErrorResponse, 422, ErrorHeaders)
async def create_query(
    data: QueryCreate,
) -> tuple[QueryResponse, int] | FullErrorResponse:
    """
    Create and run a new query.
    """
    submitted = datetime.now(timezone.utc)
    uuid = str(data.database_uuid)

    # check that DB exists; in the future, return 401/403 instead
    async with get_db() as db:
        async with db.execute(
            "SELECT 1 FROM database WHERE uuid = ?",
            (uuid,),
        ) as cursor:
            row = await cursor.fetchone()
    if not row:
        return (
            ErrorResponse(
                type="https://byodb.net/errors/RFC7807/invalid-database-uuid",
                title="Invalid database UUID",
                status=422,
                detail=f'The database with uuid "{uuid}" does not exist.',
                instance=url_for(
                    "databases/v1.get_database",
                    uuid=uuid,
                    _external=True,
                    _scheme="https",
                ),
            ),
            422,
            ErrorHeaders(content_type="application/problem+json"),
        )

    path = Path(current_app.config["STORAGE"]) / uuid
    async with aiosqlite.connect(path) as db:
        started = datetime.now(timezone.utc)
        async with db.execute(data.submitted_query) as cursor:
            rows = await cursor.fetchall()
            columns = [column[0] for column in cursor.description]

        await db.commit()

    finished = datetime.now(timezone.utc)

    return (
        QueryResponse(
            result=Query(
                database_uuid=data.database_uuid,
                submitted_query=data.submitted_query,
                executed_query=data.submitted_query,
                submitted=submitted,
                started=started,
                finished=finished,
                results=QueryResults(columns=columns, rows=rows),
            ),
        ),
        201,
    )
