from __future__ import annotations

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import ActivityLog
from app.models.assessment import TestSession
from app.models.interview import InterviewSession
from app.models.profile import PlacementGoal, StudentProfile
from app.models.resume import Resume
from app.models.user import User
from app.schemas.dashboard import ActivityItem, DashboardSummary, ReadinessBreakdown

logger = logging.getLogger(__name__)


async def get_dashboard_summary(db: AsyncSession, user: User) -> DashboardSummary:
    """Calculate aggregated metrics and weighted placement readiness score."""
    # 1. Profile and Placement Goals
    prof_res = await db.execute(select(StudentProfile).where(StudentProfile.user_id == user.id))
    profile = prof_res.scalar_one_or_none()

    goal_res = await db.execute(select(PlacementGoal).where(PlacementGoal.user_id == user.id))
    goal = goal_res.scalar_one_or_none()

    # Calculate Profile Completeness (0-100)
    profile_score = 0
    if profile:
        profile_score += 40
        if profile.skills and len(profile.skills) > 0:
            profile_score += 30
        if profile.college or profile.branch:
            profile_score += 15
    if goal:
        profile_score += 15
    profile_score = min(profile_score, 100)

    # 2. Assessment Tests
    tests_res = await db.execute(
        select(TestSession).where(
            TestSession.user_id == user.id,
            TestSession.status == "completed",
        )
    )
    completed_tests = list(tests_res.scalars().all())
    total_tests_completed = len(completed_tests)

    assessment_average: int | None = None
    all_weak_topics: set[str] = set()

    if completed_tests:
        percentages = [
            int(round((t.score / t.max_score * 100)))
            for t in completed_tests
            if t.max_score and t.max_score > 0 and t.score is not None
        ]
        if percentages:
            assessment_average = int(round(sum(percentages) / len(percentages)))
        for t in completed_tests:
            if t.max_score > 0 and (t.score / t.max_score) < 0.7:
                all_weak_topics.add(t.subcategory.replace("_", " ").title())

    assessment_score = assessment_average if assessment_average is not None else 0

    # 3. Resumes
    resumes_res = await db.execute(select(Resume).where(Resume.user_id == user.id))
    resumes = list(resumes_res.scalars().all())

    best_ats_score: int | None = None
    if resumes:
        ats_scores = [r.ats_score for r in resumes if r.ats_score is not None]
        if ats_scores:
            best_ats_score = max(ats_scores)

    resume_score = best_ats_score if best_ats_score is not None else 0

    # 4. Mock Interviews
    interviews_res = await db.execute(
        select(InterviewSession).where(
            InterviewSession.user_id == user.id,
            InterviewSession.status == "completed",
        )
    )
    completed_interviews = list(interviews_res.scalars().all())
    total_interviews_completed = len(completed_interviews)

    interview_average: int | None = None
    if completed_interviews:
        int_scores = [i.score for i in completed_interviews if i.score is not None]
        if int_scores:
            interview_average = int(round(sum(int_scores) / len(int_scores)))

    interview_score = interview_average if interview_average is not None else 0

    # 5. Weighted Readiness Score Calculation
    # Weights: Profile 15%, Assessments 35%, Resume 25%, Mock Interviews 25%
    composite = round(
        0.15 * profile_score
        + 0.35 * assessment_score
        + 0.25 * resume_score
        + 0.25 * interview_score
    )
    composite = max(0, min(100, int(composite)))

    if composite >= 80:
        readiness_level = "Placement Ready"
    elif composite >= 60:
        readiness_level = "Proficient"
    elif composite >= 40:
        readiness_level = "Developing"
    else:
        readiness_level = "Needs Preparation"

    readiness = ReadinessBreakdown(
        profile_score=profile_score,
        assessment_score=assessment_score,
        resume_score=resume_score,
        interview_score=interview_score,
        composite_readiness_score=composite,
        readiness_level=readiness_level,
    )

    # 6. Recent Activity Logs
    act_res = await db.execute(
        select(ActivityLog)
        .where(ActivityLog.user_id == user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
    )
    activities = list(act_res.scalars().all())

    activity_items = [
        ActivityItem(
            id=a.id,
            activity_type=a.activity_type,
            description=a.description or a.activity_type.replace("_", " ").title(),
            created_at=a.created_at,
            metadata=a.metadata_json or {},
        )
        for a in activities
    ]

    full_name = profile.full_name if profile and profile.full_name else user.email.split("@")[0].title()

    target_role = goal.target_roles[0] if goal and goal.target_roles else None

    return DashboardSummary(
        full_name=full_name,
        email=user.email,
        target_role=target_role,
        target_companies=goal.target_companies if goal else [],
        target_ctc_lpa=goal.target_ctc_lpa if goal else None,
        readiness=readiness,
        total_tests_completed=total_tests_completed,
        assessment_average=assessment_average,
        best_ats_score=best_ats_score,
        total_interviews_completed=total_interviews_completed,
        interview_average=interview_average,
        weak_topics=sorted(list(all_weak_topics)),
        recent_activities=activity_items,
    )


async def get_user_activities(db: AsyncSession, user_id: str, limit: int = 20) -> list[ActivityItem]:
    """Fetch chronological activity feed for a student."""
    res = await db.execute(
        select(ActivityLog)
        .where(ActivityLog.user_id == user_id)
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
    )
    activities = list(res.scalars().all())
    return [
        ActivityItem(
            id=a.id,
            activity_type=a.activity_type,
            description=a.description or a.activity_type.replace("_", " ").title(),
            created_at=a.created_at,
            metadata=a.metadata_json or {},
        )
        for a in activities
    ]
