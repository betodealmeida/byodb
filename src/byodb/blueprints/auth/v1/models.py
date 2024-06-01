"""
Auth-related models.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from quart_auth import AuthUser


@dataclass
class User(AuthUser):  # pylint: disable=too-many-instance-attributes
    """
    A user.
    """

    auth_id: UUID
    email: str
    display_name: str
    password: str
    is_active: bool
    is_admin: bool
    last_login_at: datetime

    created_at: datetime
    last_modified_at: datetime

    def __post_init__(self):
        super().__init__(self.auth_id)

    async def load_user_data(self):
        user_data = await db.fetch_user_data(self.auth_id)
        self.email = user_data.get("email", None)
        self.name = user_data.get("name", None)
