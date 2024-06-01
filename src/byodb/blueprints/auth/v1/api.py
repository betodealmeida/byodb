"""
Login/logout endpoint.
"""

from quart import Blueprint

blueprint = Blueprint("auth/v1", __name__, url_prefix="/api/auth/v1")
