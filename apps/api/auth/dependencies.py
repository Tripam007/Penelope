"""
PENELOPE Backend - Auth Dependencies & RBAC
Provides JWT authentication verification and role-based access control (RBAC).
Allowed roles: citizen, tourist, authority, responder, ngo, admin.
"""

from typing import List, Callable
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select

from apps.api.database import get_db
from apps.api.models import User
from apps.api.auth.security import decode_jwt_token

security_bearer = HTTPBearer(auto_error=False)

ALLOWED_ROLES = {"citizen", "tourist", "authority", "responder", "ngo", "admin"}


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> User:
    token = None
    if credentials:
        token = credentials.credentials
    else:
        # Check Authorization header directly or query/cookie
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
        elif "access_token" in request.cookies:
            token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_jwt_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_role(*roles: str) -> Callable:
    """
    RBAC dependency factory.
    Example usage:
        @router.post("/dispatch-alert", dependencies=[Depends(require_role("authority", "admin"))])
    """
    valid_roles = set(roles)

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: action requires one of the following roles: {', '.join(sorted(valid_roles))}. Current role is '{current_user.role}'."
            )
        return current_user

    return role_checker

