"""
Database blueprint.

These endpoints are used for CRUD operations on databases.
"""

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4

from quart import Blueprint
from quart_schema import validate_request, validate_response

blueprint = Blueprint("v1/databases", __name__, url_prefix="/api/v1/databases")


class DialectEnum(StrEnum):
    sqlite = "sqlite"


@dataclass
class Database:
    uuid: UUID
    dialect: DialectEnum
    name: str
    description: str


@dataclass
class DatabaseIn:
    dialect: DialectEnum
    name: str
    description: str
    uuid: UUID | None = None


@dataclass
class DatabasesResponse:
    result: list[Database]


@dataclass
class DatabaseResponse:
    result: Database


@blueprint.route("/", methods=["GET"])
@validate_response(DatabasesResponse)
async def get_databases() -> DatabasesResponse:
    return DatabasesResponse(result=[])


@blueprint.route("/", methods=["POST"])
@validate_request(DatabaseIn)
@validate_response(DatabaseResponse)
async def create_database(data: DatabaseIn) -> DatabaseResponse:
    return DatabaseResponse(
        result=Database(
            uuid=data.uuid or uuid4(),
            dialect=data.dialect,
            name=data.name,
            description=data.description,
        )
    )
