from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth import (
    RefreshTokenRequest,
    RegisterResponse,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import (
    DuplicateEmailError,
    InvalidCredentialsError,
    TokenError,
    authenticate_user,
    register_user,
    revoke_refresh_token,
    rotate_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def set_refresh_cookie(response: Response, raw_token: str) -> None:
    """Helper to attach the secure HttpOnly refresh token cookie."""
    response.set_cookie(
        key="refresh_token",
        value=raw_token,
        httponly=True,
        secure=settings.SECURE_COOKIES,
        samesite="strict",
        path=f"{settings.API_V1_PREFIX}/auth/refresh",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegisterRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RegisterResponse:
    """Register a new student account, immediately logging them in and establishing refresh cookie."""
    try:
        await register_user(db, payload)
        auth_user, access_token, raw_refresh = await authenticate_user(db, payload.email, payload.password)
        set_refresh_cookie(response, raw_refresh)

        user_out = UserResponse.model_validate(auth_user)
        return RegisterResponse(
            id=auth_user.id,
            email=auth_user.email,
            role=auth_user.role,
            is_active=auth_user.is_active,
            profile=user_out.profile,
            goals=user_out.goals,
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_out,
        )
    except DuplicateEmailError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "DUPLICATE_EMAIL", "message": str(e)},
        ) from e


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLoginRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Authenticate with email and password, establishing an HttpOnly refresh cookie."""
    try:
        user, access_token, raw_refresh = await authenticate_user(db, payload.email, payload.password)
        set_refresh_cookie(response, raw_refresh)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": str(e)},
        ) from e


@router.post("/refresh")
async def refresh_tokens_endpoint(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    body: RefreshTokenRequest | None = None,
    refresh_token_cookie: Annotated[str | None, Cookie(alias="refresh_token")] = None,
) -> dict[str, str | int]:
    """Rotate tokens using the HttpOnly cookie (or JSON body fallback)."""
    raw_token = refresh_token_cookie or (body.refresh_token if body else None)
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "TOKEN_INVALID", "message": "Refresh token cookie or payload missing."},
        )

    try:
        new_access, new_refresh = await rotate_refresh_token(db, raw_token)
        set_refresh_cookie(response, new_refresh)

        return {
            "access_token": new_access,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
    except TokenError as e:
        response.delete_cookie(
            key="refresh_token",
            path=f"{settings.API_V1_PREFIX}/auth/refresh",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "TOKEN_EXPIRED", "message": str(e)},
        ) from e


@router.post("/logout")
async def logout(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    body: RefreshTokenRequest | None = None,
    refresh_token_cookie: Annotated[str | None, Cookie(alias="refresh_token")] = None,
) -> dict[str, str]:
    """Revoke active refresh token and clear the HttpOnly cookie."""
    raw_token = refresh_token_cookie or (body.refresh_token if body else None)
    if raw_token:
        await revoke_refresh_token(db, raw_token)

    response.delete_cookie(
        key="refresh_token",
        path=f"{settings.API_V1_PREFIX}/auth/refresh",
    )
    return {"message": "Logged out successfully"}

