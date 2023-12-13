"""
Database models.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import aiosqlite

from byodb.constants import DialectEnum

from .utils import get_database_size


@dataclass
class Database:
    """
    Base model for a database.
    """

    uuid: UUID
    dialect: DialectEnum
    name: str
    description: str
    created_at: datetime
    last_modified_at: datetime
    size_in_bytes: int

    @staticmethod
    def from_row(row: aiosqlite.Row) -> "Database":
        return Database(
            uuid=UUID(row["uuid"]),
            dialect=DialectEnum(row["dialect"]),
            name=row["name"],
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]),
            last_modified_at=datetime.fromisoformat(row["last_modified_at"]),
            size_in_bytes=get_database_size(row["uuid"]),
        )


@dataclass
class DatabaseCreate:
    """
    Payload for creating a new database.
    """

    dialect: DialectEnum
    name: str
    description: str
    uuid: UUID | None = None


@dataclass
class DatabaseUpdate:
    """
    Payload for updating a database.

    Currently only the name and description can be changed. The `last_modified_at`
    attribute is automatically updated. Changing the UUID, dialect, or `created_at` are
    not allowed for consistency.
    """

    name: str | None = None
    description: str | None = None


@dataclass
class DatabasesResponse:
    result: list[Database]


@dataclass
class DatabaseResponse:
    result: Database


@dataclass
class DatabaseDeletedResponse:
    result: str
