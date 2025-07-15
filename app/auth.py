"""Authentication utilities for role and group checking."""

from app import auth


def has_role(role):
    """Check if the current user has a specific role."""
    user = auth.get_user()
    return user and role in user.get('roles', [])


def has_group(group):
    """Check if the current user belongs to a specific group."""
    user = auth.get_user()
    return user and group in user.get('groups', [])