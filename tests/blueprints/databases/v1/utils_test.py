"""
Tests for the utils module.
"""

from quart import Quart
from pytest_mock import MockerFixture

from byodb.blueprints.databases.v1.utils import (
    get_database_size,
    get_database_not_found_error,
)
from byodb.errors import ErrorResponse, ErrorHeaders


async def test_get_database_size(mocker: MockerFixture, app: Quart) -> None:
    """
    Test the `get_database_size` function.
    """
    Path = mocker.patch("byodb.blueprints.databases.v1.utils.Path")
    Path().__truediv__().stat().st_size = 1234

    async with app.app_context():
        result = get_database_size("some-uuid")

    assert result == 1234


async def test_get_database_not_found_error(app: Quart) -> None:
    """
    Test the `get_database_not_found_error` function.
    """
    async with app.app_context():
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
