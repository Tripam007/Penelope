"""
PENELOPE Backend - Authentication API Routes
Implements user registration, login with JWT access token + httpOnly refresh cookie,
token refresh, logout, and current user profile inspection.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import select

from apps.api.database import get_db
from apps.api.models import User
from apps.api.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_jwt_token,
    REFRESH_TOKEN_EXPIRE_DAYS
)
from apps.api.auth.dependencies import get_current_user, ALLOWED_ROLES
from apps.api.auth.rate_limiter import auth_rate_limit

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================================
# Schemas
# ============================================================================
class RegisterRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    name: str = Field(..., min_length=2)
    role: str = Field(default="citizen", description="citizen | tourist | authority | responder | ngo | admin")
    org: Optional[str] = None
    region_id: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if "@" not in clean or "." not in clean.split("@")[-1]:
            raise ValueError("Invalid email format")
        return clean


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        return v.strip().lower()


class RefreshRequest(BaseModel):
    refresh_token: Optional[str] = None


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    role: str
    name: str
    org: Optional[str]
    region_id: Optional[str]
    is_active: bool


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in_seconds: int = 900  # 15 minutes
    user: UserProfileResponse


# ============================================================================
# Endpoints
# ============================================================================
@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(auth_rate_limit)
):
    """Register a new user with role and return credentials."""
    clean_email = payload.email.lower().strip()
    role_normalized = "admin" if clean_email == "tripambiswas007@gmail.com" else payload.role.lower().strip()
    if role_normalized not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(sorted(ALLOWED_ROLES))}"
        )

    # Check for existing email
    existing = db.execute(select(User).where(User.email == clean_email)).scalar_one_or_none()
    if existing:
        if clean_email == "tripambiswas007@gmail.com" and existing.role != "admin":
            existing.role = "admin"
            db.commit()
            db.refresh(existing)
            access_token = create_access_token(existing.id, existing.email, existing.role, existing.name)
            refresh_token = create_refresh_token(existing.id)
            return {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in_seconds": 900,
                "user": existing
            }
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists."
        )

    user = User(
        email=clean_email,
        password_hash=hash_password(payload.password),
        name=payload.name.strip(),
        role=role_normalized,
        org=payload.org or ("PENELOPE Directorate - Super Admin" if clean_email == "tripambiswas007@gmail.com" else None),
        region_id=payload.region_id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate tokens
    access_token = create_access_token(user.id, user.email, user.role, user.name)
    refresh_token = create_refresh_token(user.id)

    # Set httpOnly cookie for refresh token (7 days)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        samesite="lax",
        secure=False  # Set True in production HTTPS
    )

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in_seconds": 900,
        "user": user
    }


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(auth_rate_limit)
):
    """Authenticate with email and password. Returns access token and sets httpOnly refresh cookie."""
    user = db.execute(select(User).where(User.email == payload.email.lower().strip())).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact disaster coordinator."
        )

    # Automatically ensure tripambiswas007@gmail.com is Admin
    if user.email == "tripambiswas007@gmail.com" and user.role != "admin":
        user.role = "admin"
        db.commit()
        db.refresh(user)

    access_token = create_access_token(user.id, user.email, user.role, user.name)
    refresh_token = create_refresh_token(user.id)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        samesite="lax",
        secure=False
    )

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in_seconds": 900,
        "user": user
    }


@router.post("/refresh")
def refresh_token_endpoint(
    request: Request,
    response: Response,
    payload: Optional[RefreshRequest] = None,
    db: Session = Depends(get_db)
):
    """Obtain a new 15-minute access token using the 7-day httpOnly refresh token cookie."""
    token = None
    if "refresh_token" in request.cookies:
        token = request.cookies.get("refresh_token")
    elif payload and payload.refresh_token:
        token = payload.refresh_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token cookie or payload provided."
        )

    decoded = decode_jwt_token(token)
    if not decoded or decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        )

    user_id = decoded.get("sub")
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with refresh token no longer exists or is inactive."
        )

    new_access_token = create_access_token(user.id, user.email, user.role, user.name)
    return {
        "access_token": new_access_token,
        "token_type": "Bearer",
        "expires_in_seconds": 900
    }


@router.post("/logout")
def logout(response: Response):
    """Clear httpOnly refresh token cookie and terminate session."""
    response.delete_cookie(key="refresh_token", samesite="lax")
    return {"message": "Logged out successfully."}


@router.get("/me", response_model=UserProfileResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve currently authenticated user profile and active permissions."""
    return current_user

