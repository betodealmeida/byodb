"""
Fixtures for testing BYODB.
"""

import pytest
from quart import Quart, testing

from byodb.main import create_app, init_db


@pytest.fixture(name="current_app")
async def app(tmpdir) -> Quart:
    """
    Create and configure a new app instance for each test.
    """
    test_app = create_app(
        {
            "DATABASE": str(tmpdir.join("byodb.sqlite")),
            "STORAGE": str(tmpdir.join("storage")),
            "SERVER_NAME": "byodb.net",
        },
    )
    await init_db(test_app)

    if not tmpdir.join("storage").exists():
        tmpdir.join("storage").mkdir()

    yield test_app


@pytest.fixture
async def client(current_app: Quart) -> testing.QuartClient:
    """
    A test client for the app.
    """
    async with current_app.test_client() as test_client:
        yield test_client


@pytest.fixture
async def runner(current_app: Quart):
    """
    A test runner for the app's Click commands.
    """
    return current_app.test_cli_runner()
