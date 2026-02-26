"""Admin module."""
from .user_manager import get_user_manager
from .content_moderator import get_content_moderator

__all__ = ["get_user_manager", "get_content_moderator"]
