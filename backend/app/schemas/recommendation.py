from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class StudyPlanPhase(BaseModel):
    phase: str
    topic: str
    priority: str  # "high" | "medium" | "low"
    objective: str
    recommended_hours: int = 10


class LearningResource(BaseModel):
    title: str
    type: str  # "documentation" | "practice" | "video" | "cheatsheet"
    url: str
    topics: list[str] = []
    description: str


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    study_plan: list[StudyPlanPhase]
    resources: list[LearningResource]
    generated_at: datetime

