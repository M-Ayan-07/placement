from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation_service import (
    generate_student_recommendations,
    get_latest_recommendation,
)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/latest", response_model=RecommendationResponse)
async def get_my_recommendations(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RecommendationResponse:
    """Fetch the latest preparation roadmap and curated resources (auto-generates if none exist)."""
    rec = await get_latest_recommendation(db, user_id=current_user.id)
    if not rec:
        rec = await generate_student_recommendations(db, user_id=current_user.id)
    return rec


@router.post("/generate", response_model=RecommendationResponse)
async def regenerate_recommendations(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RecommendationResponse:
    """Regenerate personalized study plan and learning resources based on latest test results."""
    return await generate_student_recommendations(db, user_id=current_user.id)

