from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.interview import (
    InterviewAnswerRequest,
    InterviewAnswerResponse,
    InterviewSessionOut,
    InterviewStartRequest,
)
from app.services import interview_service

router = APIRouter(prefix="/interview", tags=["Mock Interview"])


@router.post("/start", response_model=InterviewSessionOut, status_code=status.HTTP_201_CREATED)
async def start_mock_interview(
    payload: InterviewStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewSessionOut:
    """Initialize a mock interview and generate the opening question."""
    session = await interview_service.start_interview(
        db,
        user_id=current_user.id,
        interview_type=payload.interview_type,
        topic=payload.topic,
    )
    return InterviewSessionOut.model_validate(session)


@router.get("/history", response_model=list[InterviewSessionOut])
async def get_interview_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[InterviewSessionOut]:
    """List all previous mock interview sessions for current student."""
    sessions = await interview_service.get_interview_history(db, current_user.id)
    return [InterviewSessionOut.model_validate(s) for s in sessions]


@router.get("/{session_id}", response_model=InterviewSessionOut)
async def get_interview_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewSessionOut:
    """Get status, questions, answers, and feedback for an interview session."""
    session = await interview_service.get_interview_session(db, current_user.id, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found",
        )
    return InterviewSessionOut.model_validate(session)


@router.post("/{session_id}/answer", response_model=InterviewAnswerResponse)
async def submit_interview_answer(
    session_id: str,
    payload: InterviewAnswerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewAnswerResponse:
    """Submit an answer to the current question and receive feedback and next question."""
    try:
        result = await interview_service.submit_answer(
            db,
            user_id=current_user.id,
            session_id=session_id,
            answer=payload.answer,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return InterviewAnswerResponse(**result)

