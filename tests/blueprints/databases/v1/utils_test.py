"""
Tests for the utils module.
"""

from uuid import uuid4

from pytest_mock import MockerFixture
from quart import Quart

from byodb.blueprints.databases.v1.utils import (
    get_database_not_found_error,
    get_database_size,
)
from byodb.errors import ErrorHeaders, ErrorResponse


async def test_get_database_size(mocker: MockerFixture, current_app: Quart) -> None:
    """
    Test the `get_database_size` function.
    """
    # pylint: disable=invalid-name, unnecessary-dunder-call
    Path = mocker.patch("byodb.blueprints.databases.v1.utils.Path")
    Path().__truediv__().stat().st_size = 1234

    async with current_app.app_context():
        result = get_database_size(uuid4())

    assert result == 1234


async def test_get_database_not_found_error(current_app: Quart) -> None:
    """
    Test the `get_database_not_found_error` function.
    """
    async with current_app.app_context():
        response, status_code, headers = get_database_not_found_error("some-uuid")

    assert response == ErrorResponse(
        type="https://byodb.net/errors/RFC7807/database-not-found",
        title="Database not found",
        status=404,
        detail='The database with uuid "some-uuid" does not exist.',
        instance="https://byodb.net/api/databases/v1/some-uuid",
    )
    assert status_code == 404
    assert headers == ErrorHeaders(content_type="application/problem+json")
