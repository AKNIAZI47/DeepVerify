"""Role-based access control."""
from typing import List, Set
from enum import Enum

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    MODERATE = "moderate"
    ADMIN = "admin"

ROLE_PERMISSIONS = {
    Role.USER: {Permission.READ, Permission.WRITE},
    Role.MODERATOR: {Permission.READ, Permission.WRITE, Permission.MODERATE},
    Role.ADMIN: {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.MODERATE, Permission.ADMIN}
}

def has_permission(user_role: str, required_permission: str) -> bool:
    role = Role(user_role)
    permission = Permission(required_permission)
    return permission in ROLE_PERMISSIONS.get(role, set())
