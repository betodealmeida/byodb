"""
Tests for the queries API.
"""

from uuid import UUID

from freezegun import freeze_time
from pytest_mock import MockerFixture
from quart import Quart


async def test_create_query(mocker: MockerFixture, app: Quart) -> None:
    """
    Test the `create_query` endpoint.
    """
    mocker.patch(
        "byodb.blueprints.databases.v1.api.uuid4",
        return_value=UUID("92cdeabd-8278-43ad-871d-0214dcb2d12e"),
    )

    test_client = app.test_client()

    with freeze_time("2023-01-01"):
        await test_client.post(
            "/api/v1/databases/",
            json={
                "dialect": "sqlite",
                "name": "test_db",
                "description": "A simple database",
            },
        )

    with freeze_time("2023-01-01"):
        response = await test_client.post(
            "/api/v1/queries/",
            json={
                "database_uuid": "92cdeabd-8278-43ad-871d-0214dcb2d12e",
                "submitted_query": "SELECT 42",
            },
        )

    assert response.status_code == 201
    payload = await response.json
    assert payload == {
        "result": {
            "database_uuid": "92cdeabd-8278-43ad-871d-0214dcb2d12e",
            "executed_query": "SELECT 42",
            "finished": "2023-01-01T00:00:00Z",
            "results": {"columns": ["42"], "rows": [[42]]},
            "started": "2023-01-01T00:00:00Z",
            "submitted": "2023-01-01T00:00:00Z",
            "submitted_query": "SELECT 42",
        }
    }


async def test_create_query_invalid_database(app: Quart) -> None:
    """
    Test the `create_query` endpoint with an invalid database UUID.
    """
    test_client = app.test_client()

    with freeze_time("2023-01-01"):
        response = await test_client.post(
            "/api/v1/queries/",
            json={
                "database_uuid": "92cdeabd-8278-43ad-871d-0214dcb2d12e",
                "submitted_query": "SELECT 42",
            },
        )

    assert response.status_code == 422
    payload = await response.json
    assert payload == {
        "detail": 'The database with uuid "92cdeabd-8278-43ad-871d-0214dcb2d12e" does not exist.',
        "instance": "https://byodb.net/api/v1/databases/92cdeabd-8278-43ad-871d-0214dcb2d12e",
        "status": 422,
        "title": "Invalid database UUID",
        "type": "https://byodb.net/errors/RFC7807/invalid-database-uuid",
    }
