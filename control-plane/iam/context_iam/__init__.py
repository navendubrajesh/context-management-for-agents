"""Enterprise IAM for context-management-for-agents."""

from context_iam.auth import authenticate_request
from context_iam.config import auth_mode, is_auth_enforced
from context_iam.identity import Principal
from context_iam.rbac import Permission, authorize, role_permissions

__all__ = [
    "Principal",
    "Permission",
    "authenticate_request",
    "authorize",
    "role_permissions",
    "auth_mode",
    "is_auth_enforced",
]
