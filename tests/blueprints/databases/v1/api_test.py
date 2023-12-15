"""
Tests for the database API.
"""

from uuid import UUID

from freezegun import freeze_time
from pytest_mock import MockerFixture
from quart import Quart
from quart_auth import authenticated_client


@freeze_time("2023-01-01")
async def test_get_databases(mocker: MockerFixture, current_app: Quart) -> None:
    """
    Test the `get_databases` endpoint.
    """
    mocker.patch(
        "byodb.blueprints.databases.v1.api.uuid4",
        return_value=UUID("92cdeabd-8278-43ad-871d-0214dcb2d12e"),
    )

    test_client = current_app.test_client()
    auth_id = "48150b24-92e4-49d4-8c1a-8ca8ec394039"
    async with authenticated_client(test_client, auth_id):
        response = await test_client.get("/api/databases/v1/")
        assert response.status_code == 200
        payload = await response.json
        assert payload == {"result": []}

        await test_client.post(
            "/api/databases/v1/",
            json={
                "dialect": "sqlite",
                "name": "test_db",
                "description": "A simple database",
            },
        )

        response = await test_client.get("/api/databases/v1/")
        assert response.status_code == 200
        payload = await response.json
        assert payload == {
            "result": [
                {
                    "created_at": "2023-01-01T00:00:00Z",
                    "description": "A simple database",
                    "dialect": "sqlite",
                    "last_modified_at": "2023-01-01T00:00:00Z",
                    "name": "test_db",
                    "size_in_bytes": 0,
                    "uuid": "92cdeabd-8278-43ad-871d-0214dcb2d12e",
                },
            ],
        }


@freeze_time("2023-01-01")
async def test_get_database(mocker: MockerFixture, current_app: Quart) -> None:
    """
    Test the `get_database` endpoint.
    """
    mocker.patch(
        "byodb.blueprints.databases.v1.api.uuid4",
        return_value=UUID("92cdeabd-8278-43ad-871d-0214dcb2d12e"),
    )

    test_client = current_app.test_client()
    auth_id = "48150b24-92e4-49d4-8c1a-8ca8ec394039"
    async with authenticated_client(test_client, auth_id):
        await test_client.post(
            "/api/databases/v1/",
            json={
                "dialect": "sqlite",
                "name": "test_db",
                "description": "A simple database",
            },
        )

        response = await test_client.get(
            "/api/databases/v1/92cdeabd-8278-43ad-871d-0214dcb2d12e",
        )
        assert response.status_code == 200
        payload = await response.json
        assert payload == {
            "result": {
                "created_at": "2023-01-01T00:00:00Z",
                "description": "A simple database",
                "dialect": "sqlite",
                "last_modified_at": "2023-01-01T00:00:00Z",
                "name": "test_db",
                "size_in_bytes": 0,
                "uuid": "92cdeabd-8278-43ad-871d-0214dcb2d12e",
            },
        }

        response = await test_client.get("/api/databases/v1/invalid")
        assert response.status_code == 404
        payload = await response.json
        assert payload == {
            "detail": 'The database with uuid "invalid" does not exist.',
            "instance": "https://byodb.net/api/databases/v1/invalid",
            "status": 404,
            "title": "Database not found",
            "type": "https://byodb.net/errors/RFC7807/database-not-found",
        }


@freeze_time("2023-01-01")
async def test_create_database(mocker: MockerFixture, current_app: Quart) -> None:
    """
    Test the `create_databases` endpoint.
    """
    mocker.patch(
        "byodb.blueprints.databases.v1.api.uuid4",
        return_value=UUID("92cdeabd-8278-43ad-871d-0214dcb2d12e"),
    )

    test_client = current_app.test_client()
    auth_id = "48150b24-92e4-49d4-8c1a-8ca8ec394039"
    async with authenticated_client(test_client, auth_id):
        response = await test_client.post(
            "/api/databases/v1/",
            json={
                "dialect": "sqlite",
                "name": "test_db",
                "description": "A simple database",
            },
        )
        assert response.status_code == 201
        payload = await response.json
        assert payload == {
            "result": {
                "created_at": "2023-01-01T00:00:00Z",
                "description": "A simple database",
                "dialect": "sqlite",
                "last_modified_at": "2023-01-01T00:00:00Z",
                "name": "test_db",
                "size_in_bytes": 0,
                "uuid": "92cdeabd-8278-43ad-871d-0214dcb2d12e",
            },
        }


@freeze_time("2023-01-01")
async def test_delete_database(mocker: MockerFixture, current_app: Quart) -> None:
    """
    Test the `delete_database` endpoint.
    """
    mocker.patch(
        "byodb.blueprints.databases.v1.api.uuid4",
        return_value=UUID("92cdeabd-8278-43ad-871d-0214dcb2d12e"),
    )

    test_client = current_app.test_client()
    auth_id = "48150b24-92e4-49d4-8c1a-8ca8ec394039"
    async with authenticated_client(test_client, auth_id):
        await test_client.post(
            "/api/databases/v1/",
            json={
                "dialect": "sqlite",
                "name": "test_db",
                "description": "A simple database",
            },
        )

        response = await test_client.delete(
            "/api/databases/v1/92cdeabd-8278-43ad-871d-0214dcb2d12e",
        )
        assert response.status_code == 204
        payload = await response.json
        assert payload == {"result": "OK"}

        response = await test_client.delete("/api/databases/v1/invalid")
        assert response.status_code == 404
        payload = await response.json
        assert payload == {
            "detail": 'The database with uuid "invalid" does not exist.',
            "instance": "https://byodb.net/api/databases/v1/invalid",
            "status": 404,
            "title": "Database not found",
            "type": "https://byodb.net/errors/RFC7807/database-not-found",
        }


async def test_delete_database_multiple_primary_keys(
    mocker: MockerFixture,
    current_app: Quart,
) -> None:
    """
    Test the error message when multiple databases have the same UUID.

    This should never happen. I don't know why I'm writing this test.
    """
    connection = mocker.AsyncMock()
    db = mocker.AsyncMock()
    db.total_changes = 2
    connection.__aenter__.return_value = db
    mocker.patch(
        "byodb.blueprints.databases.v1.api.aiosqlite.connect",
        return_value=connection,
    )

    test_client = current_app.test_client()
    auth_id = "48150b24-92e4-49d4-8c1a-8ca8ec394039"
    async with authenticated_client(test_client, auth_id):
        response = await test_client.delete(
            "/api/databases/v1/92cdeabd-8278-43ad-871d-0214dcb2d12e",
        )
        assert response.status_code == 500
        payload = await response.json
        assert payload == {
            "detail": (
                "More than one database with the same uuid were found (and deleted). "
                "This should never happen. I blame the goblins."
            ),
            "instance": (
                "http://byodb.net/api/databases/v1/92cdeabd-8278-43ad-871d-0214dcb2d12e"
            ),
            "status": 500,
            "title": "Multiple primary keys found",
            "type": "https://byodb.net/errors/RFC7807/multiple-primary-keys",
        }


@freeze_time("2023-01-01")
async def test_update_database(mocker: MockerFixture, current_app: Quart) -> None:
    """
    Test the `update_database` endpoint.
    """
    mocker.patch(
        "byodb.blueprints.databases.v1.api.uuid4",
        return_value=UUID("92cdeabd-8278-43ad-871d-0214dcb2d12e"),
    )

    test_client = current_app.test_client()
    auth_id = "48150b24-92e4-49d4-8c1a-8ca8ec394039"
    async with authenticated_client(test_client, auth_id):
        await test_client.post(
            "/api/databases/v1/",
            json={
                "dialect": "sqlite",
                "name": "test_db",
                "description": "A simple database",
            },
        )

        with freeze_time("2023-01-02"):
            response = await test_client.patch(
                "/api/databases/v1/92cdeabd-8278-43ad-871d-0214dcb2d12e",
                json={"name": "test"},
            )
        assert response.status_code == 200
        payload = await response.json
        assert payload == {
            "result": {
                "created_at": "2023-01-01T00:00:00Z",
                "description": "A simple database",
                "dialect": "sqlite",
                "last_modified_at": "2023-01-02T00:00:00Z",
                "name": "test",
                "size_in_bytes": 0,
                "uuid": "92cdeabd-8278-43ad-871d-0214dcb2d12e",
            },
        }

        response = await test_client.patch(
            "/api/databases/v1/invalid",
            json={"name": "test"},
        )
        assert response.status_code == 404
        payload = await response.json
        assert payload == {
            "detail": 'The database with uuid "invalid" does not exist.',
            "instance": "https://byodb.net/api/databases/v1/invalid",
            "status": 404,
            "title": "Database not found",
            "type": "https://byodb.net/errors/RFC7807/database-not-found",
        }
