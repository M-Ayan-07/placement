from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InterviewSession(Base):
    """Mock interview practice session."""

    __tablename__ = "interview_sessions"

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
    interview_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "technical" | "hr"
    topic: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="in_progress", nullable=False)  # "in_progress" | "completed"
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    exchanges: Mapped[list[InterviewExchange]] = relationship(
        "InterviewExchange",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="InterviewExchange.turn_order",
    )


class InterviewExchange(Base):
    """A single Q&A turn in a mock interview."""

    __tablename__ = "interview_exchanges"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    turn_order: Mapped[int] = mapped_column(Integer, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    student_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    session: Mapped[InterviewSession] = relationship("InterviewSession", back_populates="exchanges")

