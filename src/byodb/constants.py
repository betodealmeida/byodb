from enum import StrEnum


class DialectEnum(StrEnum):
    """
    Dialects supported by BYODB.

    Currently all exposed databases are SQLite databases, since it's a much simpler
    architecture to support. Eventually, we might want to support different databases
    (eg, Postgres), which would require some kind of negotiation between the application
    and the BYODB instance.

    If we ever support multiple dialects it would be nice to have a requirement that all
    application should support at least SQLite, so that people are not locked out of
    applications because their BYODB instance doesn't support a specific database.
    """

    sqlite = "sqlite"
