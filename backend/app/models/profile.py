from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class StudentProfile(Base, TimestampMixin):
    """Academic and personal profile details for a student."""

    __tablename__ = "student_profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    college: Mapped[str | None] = mapped_column(String(150), nullable=True)
    branch: Mapped[str | None] = mapped_column(String(100), nullable=True)
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cgpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped[User] = relationship("User", back_populates="profile")


class PlacementGoal(Base, TimestampMixin):
    """Student's target career goals, companies, and roles."""

    __tablename__ = "placement_goals"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    target_roles: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    target_companies: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    target_ctc_lpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    preferred_locations: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="goals")

