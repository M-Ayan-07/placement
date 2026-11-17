from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with work factor 12.

    Args:
        password: Plain text password string.

    Returns:
        Bcrypt hashed password string.
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored bcrypt hash.

    Args:
        plain_password: Plain text candidate password.
        hashed_password: Stored bcrypt hash string.

    Returns:
        True if the password matches, False otherwise.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def create_access_token(subject: str, role: str, expires_delta: timedelta | None = None) -> str:
    """Generate a signed short-lived JWT access token.

    Args:
        subject: User UUID string.
        role: User role (e.g. 'student', 'admin').
        expires_delta: Optional custom lifetime duration.

    Returns:
        Signed JWT string.
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": now,
        "jti": secrets.token_hex(8),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token.

    Args:
        token: JWT string.

    Returns:
        Decoded token payload dict.

    Raises:
        jwt.PyJWTError: If signature is invalid or token is expired.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def generate_refresh_token() -> str:
    """Generate a high-entropy cryptographically secure random token string.

    Returns:
        64-byte urlsafe token string.
    """
    return secrets.token_urlsafe(64)


def hash_refresh_token(raw_token: str) -> str:
    """Compute the SHA-256 hash of a raw refresh token for safe database persistence.

    Args:
        raw_token: Plain refresh token string.

    Returns:
        Hex-encoded SHA-256 digest string.
    """
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

