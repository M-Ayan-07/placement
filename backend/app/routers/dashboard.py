from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.dashboard import ActivityItem, DashboardSummary
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardSummary:
    """Retrieve full dashboard statistics and placement readiness score."""
    return await dashboard_service.get_dashboard_summary(db, current_user)


@router.get("/activities", response_model=list[ActivityItem])
async def get_user_activities(
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ActivityItem]:
    """Retrieve recent placement preparation activities for the student."""
    return await dashboard_service.get_user_activities(db, current_user.id, limit=limit)

