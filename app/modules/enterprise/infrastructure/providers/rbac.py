from functools import wraps
from fastapi import Depends, HTTPException, status
from typing import Dict, Any
from app.modules.enterprise.domain.entities.permissions import ROLE_PERMISSIONS

def has_permission(role: str, permission: str) -> bool:
    """Verifies if the role holds the requested permission claim."""
    perms = ROLE_PERMISSIONS.get(role, set())
    return permission in perms

def requires_permission(permission: str):
    """
    Decorator mapping permission validation checks on async operations.
    Inspects keyword arguments for 'current_user' context.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication credentials not found."
                )
            
            # Access user role (defaulting to user)
            role = getattr(current_user, "role", "user")
            if not has_permission(role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Operation requires permission claim: '{permission}'"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class APIKeyValidator:
    def __init__(self):
        # In-memory mapped keys for service/internal system auth checks
        self._keys = {
            "admin-api-key-999": {"role": "ADMIN", "scopes": ["*"]},
            "mlops-key-888": {"role": "MLOPS_ENGINEER", "scopes": ["manage_models"]}
        }

    def validate_key(self, api_key: str) -> Dict[str, Any]:
        if api_key not in self._keys:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API Key credentials."
            )
        return self._keys[api_key]
