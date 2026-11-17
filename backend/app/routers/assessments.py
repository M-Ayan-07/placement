from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.assessment import (
    CategoriesResponse,
    SessionResultResponse,
    SessionStartResponse,
    StartSessionRequest,
    SubmitSessionRequest,
)
from app.services.assessment_service import (
    get_assessment_categories,
    get_session_result_details,
    get_user_history,
    start_assessment_session,
    submit_assessment_session,
)

router = APIRouter(prefix="/assessments", tags=["Assessments"])


@router.get("/categories", response_model=CategoriesResponse)
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CategoriesResponse:
    """Browse available diagnostic test categories and subcategories."""
    return await get_assessment_categories(db)


@router.post("/sessions/start", response_model=SessionStartResponse)
async def start_session(
    payload: StartSessionRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SessionStartResponse:
    """Initialize a timed test session and obtain randomized questions."""
    return await start_assessment_session(
        db,
        user_id=current_user.id,
        category=payload.category,
        subcategory=payload.subcategory,
        num_questions=payload.num_questions,
    )


@router.post("/sessions/{session_id}/submit", response_model=SessionResultResponse)
async def submit_session(
    session_id: str,
    payload: SubmitSessionRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SessionResultResponse:
    """Submit test responses, calculate score, and identify weak topics."""
    try:
        return await submit_assessment_session(
            db,
            user_id=current_user.id,
            session_id=session_id,
            answers=payload.answers,
            time_taken_seconds=payload.time_taken_seconds,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(e)},
        ) from e


@router.get("/sessions/{session_id}/result", response_model=SessionResultResponse)
async def get_session_result(
    session_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SessionResultResponse:
    """Retrieve detailed breakdown of answers and explanations for a completed session."""
    try:
        return await get_session_result_details(db, user_id=current_user.id, session_id=session_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(e)},
        ) from e


@router.get("/history")
async def list_history(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[dict]:
    """Retrieve history of all test attempts by the current student."""
    return await get_user_history(db, user_id=current_user.id)

