from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class InterviewStartRequest(BaseModel):
    interview_type: str = Field(description="'technical' or 'hr'")
    topic: str = Field(min_length=2, max_length=100)


class InterviewExchangeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    turn_order: int
    question: str
    student_answer: str | None = None
    ai_feedback: str | None = None
    score: int | None = None


class InterviewSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    interview_type: str
    topic: str
    score: int | None = None
    overall_feedback: str | None = None
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    exchanges: list[InterviewExchangeOut] = []


class InterviewAnswerRequest(BaseModel):
    answer: str = Field(min_length=10, max_length=5000)


class InterviewAnswerResponse(BaseModel):
    turn_order: int
    score: int
    feedback: str
    strengths: list[str] = []
    improvements: list[str] = []
    model_answer: str
    next_question: str | None = None
    is_complete: bool
    overall_score: int | None = None
    overall_feedback: str | None = None

