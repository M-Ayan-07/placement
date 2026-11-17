from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ResumeUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    resume_id: str
    original_filename: str
    target_role: str
    file_size_bytes: int
    status: str
    uploaded_at: datetime


class SectionScores(BaseModel):
    skills: int = 75
    projects: int = 70
    experience: int = 65
    education: int = 80


class ResumeAnalysisResponse(BaseModel):
    resume_id: str
    original_filename: str
    target_role: str
    ats_score: int
    role_fit_percentage: int
    strengths: list[str]
    weaknesses: list[str]
    ats_keywords_missing: list[str]
    suggestions: list[str]
    section_scores: SectionScores
    parsed_skills: list[str]
    uploaded_at: datetime
    status: str


class ResumeListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    target_role: str
    ats_score: int | None
    status: str
    uploaded_at: datetime
