from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProfileUpdateRequest(BaseModel):
    """Payload for updating student academic details."""

    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str | None = Field(default=None, min_length=2, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    college: str | None = Field(default=None, max_length=150)
    branch: str | None = Field(default=None, max_length=100)
    graduation_year: int | None = Field(default=None, ge=2020, le=2035)
    cgpa: float | None = Field(default=None, ge=0.0, le=10.0)
    skills: list[str] | None = None
    bio: str | None = Field(default=None, max_length=1000)


class GoalsUpdateRequest(BaseModel):
    """Payload for updating target placement companies and roles."""

    model_config = ConfigDict(str_strip_whitespace=True)

    target_roles: list[str] | None = None
    target_companies: list[str] | None = None
    target_ctc_lpa: float | None = Field(default=None, ge=0.0, le=200.0)
    preferred_locations: list[str] | None = None

