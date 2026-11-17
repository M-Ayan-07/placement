from __future__ import annotations

from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.profile import PlacementGoal, StudentProfile
from app.models.user import RefreshToken, User
from app.schemas.auth import UserRegisterRequest


class AuthError(Exception):
    """Base domain exception for authentication errors."""
    pass


class DuplicateEmailError(AuthError):
    """Raised when registering an email that already exists."""
    pass


class InvalidCredentialsError(AuthError):
    """Raised when email or password do not match."""
    pass


class TokenError(AuthError):
    """Raised when refresh token is invalid, expired, or revoked."""
    pass


async def register_user(db: AsyncSession, payload: UserRegisterRequest) -> User:
    """Register a new student user and create their initial profile stub.

    Args:
        db: Active async database session.
        payload: Registration details.

    Returns:
        The newly created User ORM instance.

    Raises:
        DuplicateEmailError: If the email address is already in use.
    """
    existing = await db.execute(select(User).where(User.email == payload.email.lower()))
    if existing.scalar_one_or_none():
        raise DuplicateEmailError("An account with this email address already exists.")

    user = User(
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
        role="student",
        is_active=True,
    )
    db.add(user)
    await db.flush()

    # Create associated student profile and goal stubs
    profile = StudentProfile(
        user_id=user.id,
        full_name=payload.full_name,
        skills=[],
    )
    goals = PlacementGoal(
        user_id=user.id,
        target_roles=[],
        target_companies=[],
        preferred_locations=[],
    )
    db.add(profile)
    db.add(goals)

    await db.commit()
    await db.refresh(user, ["profile", "goals"])
    return user


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> tuple[User, str, str]:
    """Verify credentials, create a fresh access token, and record a new refresh token.

    Args:
        db: Active async database session.
        email: User email.
        password: Plain text password.

    Returns:
        Tuple of (User, access_token, raw_refresh_token).

    Raises:
        InvalidCredentialsError: If email or password is incorrect.
    """
    stmt = (
        select(User)
        .options(selectinload(User.profile), selectinload(User.goals))
        .where(User.email == email.lower())
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError("Invalid email or password.")

    if not user.is_active:
        raise InvalidCredentialsError("Account is currently disabled.")

    access_token = create_access_token(subject=user.id, role=user.role)
    raw_refresh = generate_refresh_token()
    token_hash = hash_refresh_token(raw_refresh)

    refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False,
    )
    db.add(refresh_record)
    await db.commit()

    return user, access_token, raw_refresh


async def rotate_refresh_token(db: AsyncSession, raw_token: str) -> tuple[str, str]:
    """Rotate an existing refresh token: verify, revoke, and issue a fresh pair.

    Args:
        db: Active async database session.
        raw_token: Raw incoming refresh token string.

    Returns:
        Tuple of (new_access_token, new_raw_refresh_token).

    Raises:
        TokenError: If token is expired, invalid, or was already revoked.
    """
    token_hash = hash_refresh_token(raw_token)
    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()

    if not record:
        raise TokenError("Refresh token not found.")

    # Replay breach detection: If token was already revoked, revoke all tokens in family
    if record.revoked:
        await db.execute(
            select(RefreshToken).where(RefreshToken.user_id == record.user_id)
        )
        record.revoked = True
        await db.commit()
        raise TokenError("Revoked token reused. Session family invalidated.")

    now = datetime.now(timezone.utc)
    # Ensure timezone awareness for comparison
    expires_at = record.expires_at if record.expires_at.tzinfo else record.expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now:
        raise TokenError("Refresh token has expired.")

    # Mark old token as revoked
    record.revoked = True

    # Fetch user for role
    user_stmt = select(User).where(User.id == record.user_id)
    user = (await db.execute(user_stmt)).scalar_one_or_none()
    if not user or not user.is_active:
        raise TokenError("Associated user is inactive or not found.")

    # Issue new pair
    new_access_token = create_access_token(subject=user.id, role=user.role)
    new_raw_refresh = generate_refresh_token()
    new_hash = hash_refresh_token(new_raw_refresh)

    new_record = RefreshToken(
        user_id=user.id,
        token_hash=new_hash,
        expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False,
    )
    db.add(new_record)
    await db.commit()

    return new_access_token, new_raw_refresh


async def revoke_refresh_token(db: AsyncSession, raw_token: str) -> None:
    """Revoke a refresh token on logout.

    Args:
        db: Active async database session.
        raw_token: Raw token to revoke.
    """
    token_hash = hash_refresh_token(raw_token)
    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()

    if record:
        record.revoked = True
        await db.commit()

