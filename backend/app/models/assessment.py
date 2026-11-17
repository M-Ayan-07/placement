from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Assessment(Base, TimestampMixin):
    """Question bank item for aptitude or technical tests."""

    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # "aptitude" | "technical"
    subcategory: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g. "quantitative", "dsa"
    question: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list[str]] = mapped_column(JSON, nullable=False)  # e.g. ["O(1)", "O(n)", "O(log n)", "O(n^2)"]
    correct_option: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-indexed
    difficulty: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # "easy"|"medium"|"hard"
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)


class TestSession(Base):
    """A student's attempt at an assessment test."""

    __tablename__ = "test_sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    subcategory: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    time_taken_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="in_progress", nullable=False)  # "in_progress" | "completed"
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    responses: Mapped[list[TestResponse]] = relationship(
        "TestResponse",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class TestResponse(Base):
    """Student's answer to an individual question in a test session."""

    __tablename__ = "test_responses"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("test_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    selected_option: Mapped[int] = mapped_column(Integer, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    time_taken_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    session: Mapped[TestSession] = relationship("TestSession", back_populates="responses")
    assessment: Mapped[Assessment] = relationship("Assessment")

