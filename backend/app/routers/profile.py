from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UserGoalsSummary, UserProfileSummary, UserResponse
from app.schemas.profile import GoalsUpdateRequest, ProfileUpdateRequest
from app.services.profile_service import update_goals, update_profile

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Fetch profile and goals for the currently authenticated student."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserProfileSummary)
async def update_my_profile(
    payload: ProfileUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserProfileSummary:
    """Update personal and academic profile details."""
    updated = await update_profile(db, current_user.id, payload)
    return UserProfileSummary.model_validate(updated)


@router.get("/goals", response_model=UserGoalsSummary)
async def get_my_goals(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserGoalsSummary:
    """Fetch career and placement goals for the current student."""
    if not current_user.goals:
        return UserGoalsSummary()
    return UserGoalsSummary.model_validate(current_user.goals)


@router.put("/goals", response_model=UserGoalsSummary)
async def update_my_goals(
    payload: GoalsUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserGoalsSummary:
    """Update target placement roles, companies, CTC, and locations."""
    updated = await update_goals(db, current_user.id, payload)
    return UserGoalsSummary.model_validate(updated)

