import pytest
from quart import Quart, testing
from quart.ctx import AppContext

from byodb import create_app


@pytest.fixture
async def app(tmpdir) -> Quart:
    """
    Create and configure a new app instance for each test.
    """
    app: Quart = create_app(
        {
            "DATABASE": str(tmpdir.join("byodb.sqlite")),
            "STORAGE": str(tmpdir.join("storage")),
            "SERVER_NAME": "byodb.net",
        }
    )

    yield app


@pytest.fixture
async def client(app: Quart) -> testing.QuartClient:
    """
    A test client for the app.
    """
    async with app.test_client() as test_client:
        yield test_client


@pytest.fixture
async def runner(app: Quart):
    """
    A test runner for the app's Click commands.
    """
    return app.test_cli_runner()
