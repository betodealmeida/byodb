"""
Database utility functions.
"""

from pathlib import Path
from uuid import UUID

from quart import current_app, url_for

from byodb.errors import ErrorHeaders, ErrorResponse, FullErrorResponse


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
            instance=url_for(
                "v1/databases.get_database",
                uuid=uuid,
                _external=True,
                _scheme="https",
            ),
        ),
        404,
        ErrorHeaders(content_type="application/problem+json"),
    )
