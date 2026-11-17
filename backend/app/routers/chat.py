from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.chat import (
    ChatMessageOut,
    ChatSessionCreate,
    ChatSessionOut,
    SendMessageRequest,
    SendMessageResponse,
)
from app.services import chat_service

router = APIRouter(prefix="/chat", tags=["Chatbot"])


@router.get("/sessions", response_model=list[ChatSessionOut])
async def list_chat_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ChatSessionOut]:
    """Retrieve all chat sessions for the logged-in student."""
    sessions = await chat_service.get_user_sessions(db, current_user.id)
    return [ChatSessionOut.model_validate(s) for s in sessions]


@router.post("/sessions", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    payload: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatSessionOut:
    """Start a new chat session."""
    session = await chat_service.create_session(db, current_user.id, title=payload.title)
    return ChatSessionOut.model_validate(session)


@router.get("/sessions/{session_id}", response_model=ChatSessionOut)
async def get_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatSessionOut:
    """Get a specific chat session with its full message history."""
    session = await chat_service.get_session_by_id(db, current_user.id, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )
    return ChatSessionOut.model_validate(session)


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def post_message(
    session_id: str,
    payload: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SendMessageResponse:
    """Send a student message and receive the AI coach's reply."""
    try:
        user_msg, assistant_msg = await chat_service.send_message(
            db, current_user.id, session_id, payload.content
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return SendMessageResponse(
        user_message=ChatMessageOut.model_validate(user_msg),
        assistant_message=ChatMessageOut.model_validate(assistant_msg),
    )

