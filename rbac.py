from enum import Enum
from typing import List, Dict, Set

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"

class Role(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EDITOR = "editor"
    VIEWER = "viewer"

# Define role-permission mappings
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        Permission.READ,
        Permission.WRITE,
        Permission.DELETE,
        Permission.MANAGE_USERS,
        Permission.MANAGE_ROLES
    },
    Role.MANAGER: {
        Permission.READ,
        Permission.WRITE,
        Permission.DELETE,
        Permission.MANAGE_USERS
    },
    Role.EDITOR: {
        Permission.READ,
        Permission.WRITE
    },
    Role.VIEWER: {
        Permission.READ
    }
}

class RBAC:
    def __init__(self):
        self.roles = Role
        self.permissions = Permission

    def has_permission(self, role: str, permission: Permission) -> bool:
        """
        Check if a role has a specific permission
        """
        try:
            role_enum = Role(role)
            return permission in ROLE_PERMISSIONS[role_enum]
        except ValueError:
            return False

    def get_role_permissions(self, role: str) -> Set[Permission]:
        """
        Get all permissions for a specific role
        """
        try:
            role_enum = Role(role)
            return ROLE_PERMISSIONS[role_enum]
        except ValueError:
            return set()

    def is_valid_role(self, role: str) -> bool:
        """
        Check if a role is valid
        """
        try:
            Role(role)
            return True
        except ValueError:
            return False

    def get_all_roles(self) -> List[str]:
        """
        Get list of all available roles
        """
        return [role.value for role in Role]

# Create a global RBAC instance
rbac = RBAC() 