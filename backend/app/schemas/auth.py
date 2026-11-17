from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Payload for student registration."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(min_length=2, max_length=100)


class UserLoginRequest(BaseModel):
    """Payload for student login."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Optional payload for refresh token when cookies are not used."""

    refresh_token: str | None = None


class UserProfileSummary(BaseModel):
    """Nested user profile details."""

    model_config = ConfigDict(from_attributes=True)

    full_name: str
    phone: str | None = None
    college: str | None = None
    branch: str | None = None
    graduation_year: int | None = None
    cgpa: float | None = None
    skills: list[str] = []
    bio: str | None = None


class UserGoalsSummary(BaseModel):
    """Nested user placement goals."""

    model_config = ConfigDict(from_attributes=True)

    target_roles: list[str] = []
    target_companies: list[str] = []
    target_ctc_lpa: float | None = None
    preferred_locations: list[str] = []


class UserResponse(BaseModel):
    """User account response representation."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    role: str
    is_active: bool
    profile: UserProfileSummary | None = None
    goals: UserGoalsSummary | None = None


class TokenResponse(BaseModel):
    """Authentication response returning access token."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes
    user: UserResponse



class RegisterResponse(BaseModel):
    """Registration response returning immediate authentication token and user details."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    role: str
    is_active: bool
    profile: UserProfileSummary | None = None
    goals: UserGoalsSummary | None = None

    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900
    user: UserResponse
