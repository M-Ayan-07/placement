from __future__ import annotations

import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity import ActivityLog
from app.models.assessment import Assessment, TestResponse, TestSession
from app.models.profile import PlacementGoal, StudentProfile
from app.models.recommendation import Recommendation
from app.models.resume import Resume
from app.models.user import User
from app.schemas.recommendation import LearningResource, RecommendationResponse, StudyPlanPhase
from app.services.ai_service import ai_service
from app.services.prompts import RECOMMENDATION_PROMPT

logger = logging.getLogger(__name__)

CURATED_CORE_RESOURCES: list[dict] = [
    {
        "title": "NeetCode 150 - Core LeetCode Patterns",
        "type": "practice",
        "url": "https://neetcode.io/practice",
        "topics": ["DSA", "Arrays", "Binary Search", "Trees", "Dynamic Programming"],
        "description": "Essential coding interview patterns with clean video breakdowns and structured difficulty progression.",
    },
    {
        "title": "Striver's SDE Sheet & A2Z DSA Course",
        "type": "practice",
        "url": "https://takeuforward.org/strivers-a2z-dsa-course/strivers-a2z-dsa-course-sheet-2/",
        "topics": ["DSA", "System Design", "Graph Algorithms"],
        "description": "Complete placement roadmap covering topic-wise coding problems asked in tier-1 product companies.",
    },
    {
        "title": "Gate Smashers - Operating Systems & DBMS Core",
        "type": "video",
        "url": "https://www.youtube.com/@GateSmashers",
        "topics": ["Operating Systems", "DBMS", "Computer Networks"],
        "description": "Concise university and campus recruitment explanations for process scheduling, deadlocks, and SQL normalization.",
    },
    {
        "title": "IndiaBIX - Quantitative & Logical Aptitude",
        "type": "practice",
        "url": "https://www.indiabix.com/aptitude/questions-and-answers/",
        "topics": ["Quantitative", "Logical Deduction", "Probability", "Time & Work"],
        "description": "Standard multiple-choice screening problems modeled after TCS NQT, Infosys, and Cognizant screening rounds.",
    },
    {
        "title": "System Design Primer by Donne Martin",
        "type": "documentation",
        "url": "https://github.com/donnemartin/system-design-primer",
        "topics": ["System Design", "Scalability", "Microservices", "Caching"],
        "description": "Open-source comprehensive guide to architecting large-scale systems and backend architectures.",
    },
    {
        "title": "SQLZoo Interactive SQL Tutorial",
        "type": "practice",
        "url": "https://sqlzoo.net/",
        "topics": ["SQL", "DBMS", "Joins", "Aggregation"],
        "description": "Interactive browser exercises covering complex joins, subqueries, and grouping for database interviews.",
    },
]


def build_curated_plan(weak_topics: list[str], target_role: str, target_companies: list[str]) -> tuple[list[dict], list[dict]]:
    """Synthesize structured roadmap and curated resources for student context."""
    study_plan = []

    # Phase 1: Weak Topics & Foundations
    if weak_topics:
        study_plan.append({
            "phase": "Phase 1 (Week 1-2)",
            "topic": f"Master Weak Screening Areas ({', '.join(weak_topics[:3])})",
            "priority": "high",
            "objective": f"Eliminate diagnostic gaps in {', '.join(weak_topics[:3])} through 30 targeted practice problems.",
            "recommended_hours": 15,
        })
    else:
        study_plan.append({
            "phase": "Phase 1 (Week 1-2)",
            "topic": "Core Data Structures & Screening Aptitude",
            "priority": "high",
            "objective": "Consolidate array manipulation, hash maps, sliding windows, and quantitative speed drills.",
            "recommended_hours": 12,
        })

    # Phase 2: Role-Specific Coding
    study_plan.append({
        "phase": "Phase 2 (Week 3-4)",
        "topic": f"{target_role} Technical Competencies",
        "priority": "high",
        "objective": f"Deep dive into standard algorithmic patterns and architecture required by {', '.join(target_companies[:2]) if target_companies else 'target tech companies'}.",
        "recommended_hours": 18,
    })

    # Phase 3: Core CS & Mock Simulations
    study_plan.append({
        "phase": "Phase 3 (Week 5-6)",
        "topic": "CS Fundamentals & Mock Interview Execution",
        "priority": "medium",
        "objective": "Review Operating Systems, DBMS ACID guarantees, and execute 3 live technical + behavioural mock rounds.",
        "recommended_hours": 14,
    })

    # Filter resources relevant to weak topics or general
    resources = list(CURATED_CORE_RESOURCES)
    return study_plan, resources


async def generate_student_recommendations(
    db: AsyncSession, user_id: str
) -> RecommendationResponse:
    """Analyze student history and generate or update their personalized preparation plan."""
    # 1. Fetch user profile and goals
    user_stmt = (
        select(User)
        .options(selectinload(User.profile), selectinload(User.goals))
        .where(User.id == user_id)
    )
    user_res = await db.execute(user_stmt)
    user = user_res.scalar_one_or_none()

    branch = user.profile.branch if user and user.profile and user.profile.branch else "Computer Science"
    graduation_year = user.profile.graduation_year if user and user.profile and user.profile.graduation_year else 2026
    skills = user.profile.skills if user and user.profile else []
    target_roles = user.goals.target_roles if user and user.goals and user.goals.target_roles else ["Software Engineer"]
    target_companies = user.goals.target_companies if user and user.goals and user.goals.target_companies else ["Tech Companies"]

    # 2. Extract weak topics from test sessions
    resp_stmt = (
        select(TestResponse)
        .join(TestSession)
        .options(selectinload(TestResponse.assessment))
        .where(TestSession.user_id == user_id, TestResponse.is_correct == False)
        .limit(20)
    )
    resp_res = await db.execute(resp_stmt)
    incorrect_responses = resp_res.scalars().all()

    weak_topics_set = set()
    for r in incorrect_responses:
        if r.assessment and r.assessment.tags:
            for t in r.assessment.tags:
                weak_topics_set.add(t)
    weak_topics = list(weak_topics_set)

    # 3. Check resume gaps
    resume_stmt = select(Resume).where(Resume.user_id == user_id).order_by(Resume.uploaded_at.desc()).limit(1)
    resume_res = await db.execute(resume_stmt)
    latest_resume = resume_res.scalar_one_or_none()
    if latest_resume and latest_resume.ai_suggestions:
        missing_kw = latest_resume.ai_suggestions.get("ats_keywords_missing", [])
        for kw in missing_kw[:3]:
            weak_topics.append(f"{kw} (Resume Gap)")

    # 4. Generate with AI or Fallback
    study_plan = None
    resources = None

    try:
        prompt = RECOMMENDATION_PROMPT.format(
            branch=branch,
            graduation_year=graduation_year,
            target_roles=", ".join(target_roles),
            target_companies=", ".join(target_companies),
            skills=", ".join(skills) if skills else "General CS fundamentals",
            weak_areas=", ".join(weak_topics) if weak_topics else "None recorded yet (preliminary diagnostic stage)",
        )
        ai_output = await ai_service.generate_structured(prompt)
        if isinstance(ai_output, dict) and "study_plan" in ai_output:
            study_plan = ai_output.get("study_plan", [])
            resources = ai_output.get("resources", [])
    except Exception as e:
        logger.warning("AI recommendation generation failed (%s), generating curated plan.", e)

    if not study_plan or not resources:
        study_plan, resources = build_curated_plan(
            weak_topics=weak_topics,
            target_role=target_roles[0] if target_roles else "Software Engineer",
            target_companies=target_companies,
        )

    # 5. Persist
    rec = Recommendation(
        user_id=user_id,
        study_plan=study_plan,
        resources=resources,
        generated_at=datetime.now(timezone.utc),
    )
    db.add(rec)

    # 6. Log Activity
    activity = ActivityLog(
        user_id=user_id,
        activity_type="recommendation_generated",
        metadata_json={
            "phases_count": len(study_plan),
            "target_role": target_roles[0] if target_roles else "Software Engineer",
        },
    )
    db.add(activity)

    await db.commit()
    await db.refresh(rec)

    parsed_plan = [StudyPlanPhase(**p) for p in study_plan]
    parsed_resources = [LearningResource(**r) for r in resources]

    return RecommendationResponse(
        id=rec.id,
        user_id=rec.user_id,
        study_plan=parsed_plan,
        resources=parsed_resources,
        generated_at=rec.generated_at,
    )


async def get_latest_recommendation(
    db: AsyncSession, user_id: str
) -> RecommendationResponse | None:
    """Retrieve the latest recommendation record for the user, or None."""
    stmt = (
        select(Recommendation)
        .where(Recommendation.user_id == user_id)
        .order_by(Recommendation.generated_at.desc())
        .limit(1)
    )
    res = await db.execute(stmt)
    rec = res.scalar_one_or_none()

    if not rec:
        return None

    parsed_plan = [StudyPlanPhase(**p) for p in rec.study_plan]
    parsed_resources = [LearningResource(**r) for r in rec.resources]

    return RecommendationResponse(
        id=rec.id,
        user_id=rec.user_id,
        study_plan=parsed_plan,
        resources=parsed_resources,
        generated_at=rec.generated_at,
    )

