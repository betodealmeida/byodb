"""
Main BYODB application.
"""

from dataclasses import dataclass

from importlib.metadata import version
from quart import Quart
from quart_schema import QuartSchema, validate_response

from byodb.blueprints import databases

app = Quart(__name__)
app.register_blueprint(databases.blueprint)

QuartSchema(app)


@dataclass
class HealthCheck:
    status: str
    version: str


@app.get("/health")
@validate_response(HealthCheck)
async def health() -> HealthCheck:
    """
    Application health check.
    This endpoint is used to check the health and version of the application.
    """
    return HealthCheck(status="OK", version=version("byodb"))


def run() -> None:
    """
    Main app.
    """
    app.run()
