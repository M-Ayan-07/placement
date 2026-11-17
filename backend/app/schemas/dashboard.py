from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ReadinessBreakdown(BaseModel):
    profile_score: int = Field(ge=0, le=100)
    assessment_score: int = Field(ge=0, le=100)
    resume_score: int = Field(ge=0, le=100)
    interview_score: int = Field(ge=0, le=100)
    composite_readiness_score: int = Field(ge=0, le=100)
    readiness_level: str


class ActivityItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    activity_type: str
    description: str | None = None
    created_at: datetime
    metadata_json: dict[str, Any] = Field(default_factory=dict, alias="metadata")


class DashboardSummary(BaseModel):
    full_name: str
    email: str
    target_role: str | None = None
    target_companies: list[str] = []
    target_ctc_lpa: float | None = None
    readiness: ReadinessBreakdown
    total_tests_completed: int
    assessment_average: int | None = None
    best_ats_score: int | None = None
    total_interviews_completed: int
    interview_average: int | None = None
    weak_topics: list[str] = []
    recent_activities: list[ActivityItem] = []

