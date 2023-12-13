"""
RFC7807 errors.
"""

from dataclasses import dataclass


@dataclass
class ErrorResponse:
    """
    A problem detail as defined in RFC 7807.

    See https://www.rfc-editor.org/rfc/rfc7807.
    """

    type: str
    title: str
    status: int
    detail: str
    instance: str


@dataclass
class ErrorHeaders:
    """
    Headers for an error response.
    """

    content_type: str = "application/problem+json"


FullErrorResponse = tuple[ErrorResponse, int, ErrorHeaders]
