"""API dependencies"""

from app.core.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_superuser,
    oauth2_scheme
)

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "oauth2_scheme"
]

