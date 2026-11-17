from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SubcategoryInfo(BaseModel):
    name: str
    category: str
    question_count: int
    duration_minutes: int
    description: str


class CategoriesResponse(BaseModel):
    categories: dict[str, list[SubcategoryInfo]]


class StartSessionRequest(BaseModel):
    category: str
    subcategory: str
    num_questions: int = Field(default=10, ge=1, le=20)


class QuestionItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    category: str
    subcategory: str
    question: str
    options: list[str]
    difficulty: str


class SessionStartResponse(BaseModel):
    session_id: str
    category: str
    subcategory: str
    time_limit_minutes: int
    questions: list[QuestionItemOut]


class AnswerItem(BaseModel):
    question_id: str
    selected_option: int  # 0-indexed


class SubmitSessionRequest(BaseModel):
    answers: list[AnswerItem]
    time_taken_seconds: int = 0


class QuestionResultDetail(BaseModel):
    question_id: str
    question: str
    options: list[str]
    selected_option: int
    correct_option: int
    is_correct: bool
    explanation: str | None = None
    tags: list[str] = []


class SessionResultResponse(BaseModel):
    session_id: str
    category: str
    subcategory: str
    score: int
    max_score: int
    percentage: float
    time_taken_seconds: int
    completed_at: datetime
    weak_topics: list[str]
    breakdown: list[QuestionResultDetail]


class AssessmentHistoryItem(BaseModel):
    session_id: str
    category: str
    subcategory: str
    score: int
    max_score: int
    percentage: float
    time_taken_seconds: int
    completed_at: datetime | None
    status: str

