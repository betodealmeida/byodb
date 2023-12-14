"""
Models for queries.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass
class QueryCreate:
    """
    Model for creating a query.
    """

    database_uuid: UUID
    submitted_query: str


@dataclass
class QueryResults:
    """
    Model for query results.
    """

    columns: list[str]
    rows: list[tuple[Any, ...]]


@dataclass
class Query:
    """
    Base model for a query.
    """

    database_uuid: UUID

    submitted_query: str
    executed_query: str

    submitted: datetime
    started: datetime
    finished: datetime

    results: QueryResults


@dataclass
class QueryResponse:
    """
    An API response for a query.
    """

    result: Query
