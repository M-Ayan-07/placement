from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import PlacementGoal, StudentProfile
from app.models.user import User
from app.schemas.profile import GoalsUpdateRequest, ProfileUpdateRequest


class ProfileError(Exception):
    """Domain exception for profile operations."""
    pass


async def get_user_with_profile(db: AsyncSession, user_id: str) -> User | None:
    """Fetch user ORM including profile and goals."""
    stmt = (
        select(User)
        .options(selectinload(User.profile), selectinload(User.goals))
        .where(User.id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_profile(
    db: AsyncSession, user_id: str, payload: ProfileUpdateRequest
) -> StudentProfile:
    """Update student academic profile details.

    Args:
        db: Active async database session.
        user_id: ID of the authenticated student.
        payload: Fields to update.

    Returns:
        Updated StudentProfile ORM instance.
    """
    stmt = select(StudentProfile).where(StudentProfile.user_id == user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    if not profile:
        profile = StudentProfile(user_id=user_id, full_name="Student", skills=[])
        db.add(profile)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile


async def update_goals(
    db: AsyncSession, user_id: str, payload: GoalsUpdateRequest
) -> PlacementGoal:
    """Update student career and placement targets.

    Args:
        db: Active async database session.
        user_id: ID of the authenticated student.
        payload: Fields to update.

    Returns:
        Updated PlacementGoal ORM instance.
    """
    stmt = select(PlacementGoal).where(PlacementGoal.user_id == user_id)
    result = await db.execute(stmt)
    goals = result.scalar_one_or_none()

    if not goals:
        goals = PlacementGoal(
            user_id=user_id,
            target_roles=[],
            target_companies=[],
            preferred_locations=[],
        )
        db.add(goals)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goals, field, value)

    await db.commit()
    await db.refresh(goals)
    return goals

