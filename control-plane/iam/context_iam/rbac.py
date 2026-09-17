"""RBAC — deny-by-default permission matrix."""

from __future__ import annotations

from enum import Enum

from context_iam.identity import Principal


class Permission(str, Enum):
    SKILLS_READ = "skills:read"
    SKILLS_PUBLISH = "skills:publish"
    PRIMITIVES_RUN = "primitives:run"
    USAGE_READ = "usage:read"
    TENANTS_MANAGE = "tenants:manage"
    POLICIES_MANAGE = "policies:manage"
    SCIM_MANAGE = "scim:manage"
    AUDIT_READ = "audit:read"
    APPROVALS_MANAGE = "approvals:manage"
    EVAL_RUN = "eval:run"
    EVAL_READ = "eval:read"
    TENANT_SELF = "tenant:self"


ROLE_PERMISSIONS: dict[str, frozenset[Permission]] = {
    "viewer": frozenset(
        {Permission.SKILLS_READ, Permission.USAGE_READ, Permission.AUDIT_READ, Permission.EVAL_READ}
    ),
    "author": frozenset(
        {
            Permission.SKILLS_READ,
            Permission.SKILLS_PUBLISH,
            Permission.USAGE_READ,
            Permission.AUDIT_READ,
            Permission.EVAL_RUN,
            Permission.EVAL_READ,
        }
    ),
    "operator": frozenset(
        {
            Permission.SKILLS_READ,
            Permission.PRIMITIVES_RUN,
            Permission.USAGE_READ,
            Permission.AUDIT_READ,
            Permission.EVAL_RUN,
            Permission.EVAL_READ,
        }
    ),
    "admin": frozenset(Permission),
    "tenant-admin": frozenset(
        {
            Permission.SKILLS_READ,
            Permission.USAGE_READ,
            Permission.TENANT_SELF,
        }
    ),
}


def role_permissions(role: str) -> frozenset[Permission]:
    return ROLE_PERMISSIONS.get(role, frozenset())


def permissions_for_principal(principal: Principal) -> frozenset[Permission]:
    perms: set[Permission] = set()
    for role in principal.roles:
        perms.update(role_permissions(role))
    return frozenset(perms)


def authorize(principal: Principal, permission: Permission | str) -> bool:
    """Deny-by-default authorization check."""
    if isinstance(permission, str):
        try:
            permission = Permission(permission)
        except ValueError:
            return False
    return permission in permissions_for_principal(principal)


OPERATION_PERMISSIONS: dict[str, Permission] = {
    "skills:read": Permission.SKILLS_READ,
    "skills:publish": Permission.SKILLS_PUBLISH,
    "primitives:run": Permission.PRIMITIVES_RUN,
    "usage:read": Permission.USAGE_READ,
    "tenants:manage": Permission.TENANTS_MANAGE,
    "policies:manage": Permission.POLICIES_MANAGE,
    "scim:manage": Permission.SCIM_MANAGE,
    "audit:read": Permission.AUDIT_READ,
    "approvals:manage": Permission.APPROVALS_MANAGE,
    "eval:run": Permission.EVAL_RUN,
    "eval:read": Permission.EVAL_READ,
    "tenant:self": Permission.TENANT_SELF,
}


def authorize_operation(principal: Principal, operation: str) -> bool:
    perm = OPERATION_PERMISSIONS.get(operation)
    if perm is None:
        return False
    return authorize(principal, perm)
