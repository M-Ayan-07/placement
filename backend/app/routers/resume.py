from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.resume import ResumeAnalysisResponse, ResumeListItem
from app.services.resume_service import (
    get_resume_analysis,
    get_safe_file_path,
    get_user_resumes,
    process_and_analyze_resume,
)
from app.services.storage_service import InvalidFileError

router = APIRouter(prefix="/resume", tags=["Resume"])


@router.post("/upload", response_model=ResumeAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def upload_and_analyze_resume(
    file: UploadFile,
    target_role: Annotated[str, Form()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResumeAnalysisResponse:
    """Upload resume document (PDF or DOCX), parse text, and generate ATS evaluation."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": "Uploaded file must have a filename."},
        )

    content = await file.read()
    try:
        return await process_and_analyze_resume(
            db=db,
            user_id=current_user.id,
            file_content=content,
            original_filename=file.filename,
            target_role=target_role,
        )
    except InvalidFileError as e:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={"code": "UNSUPPORTED_MEDIA_TYPE", "message": str(e)},
        ) from e


@router.get("/list", response_model=list[ResumeListItem])
async def list_resumes(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[ResumeListItem]:
    """List previous resume uploads and ATS scores for the current student."""
    return await get_user_resumes(db, user_id=current_user.id)


@router.get("/{resume_id}", response_model=ResumeAnalysisResponse)
@router.get("/{resume_id}/analysis", response_model=ResumeAnalysisResponse)
async def get_analysis(
    resume_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResumeAnalysisResponse:
    """Retrieve the detailed ATS score and improvement report for a specific scan."""
    result = await get_resume_analysis(db, user_id=current_user.id, resume_id=resume_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Resume record not found."},
        )
    return result


@router.get("/{resume_id}/file")
async def download_resume_file(
    resume_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FileResponse:
    """Download original resume file with authenticated student ownership check."""
    try:
        abs_path, original_filename = await get_safe_file_path(db, user_id=current_user.id, resume_id=resume_id)
        return FileResponse(
            path=abs_path,
            filename=original_filename,
            media_type="application/octet-stream",
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(e)},
        ) from e

