from __future__ import annotations

import io
import json
import logging
import os
import re
from datetime import datetime, timezone
import docx
import pdfplumber
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import ActivityLog
from app.models.resume import Resume
from app.schemas.resume import (
    ResumeAnalysisResponse,
    ResumeListItem,
    ResumeUploadResponse,
    SectionScores,
)
from app.services.ai_service import ai_service
from app.services.prompts import RESUME_ANALYSIS_PROMPT, RESUME_EXTRACTION_PROMPT
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)

ROLE_KEYWORD_BENCHMARKS: dict[str, list[str]] = {
    "software engineer": [
        "Data Structures", "Algorithms", "Git", "REST APIs", "SQL", "Unit Testing",
        "CI/CD", "Object-Oriented Programming", "System Design", "Docker", "Python", "Java",
    ],
    "backend developer": [
        "FastAPI", "PostgreSQL", "REST APIs", "Microservices", "Docker", "Redis",
        "ORM", "Database Design", "Authentication", "Unit Testing", "Async Programming", "Git",
    ],
    "frontend developer": [
        "React", "TypeScript", "JavaScript", "HTML5", "CSS3", "Tailwind CSS",
        "Next.js", "State Management", "Responsive Design", "REST APIs", "Git", "Performance Optimization",
    ],
    "data analyst": [
        "SQL", "Python", "Pandas", "NumPy", "Tableau", "Power BI",
        "Excel", "Data Visualization", "Statistical Analysis", "Data Cleaning", "Business Intelligence",
    ],
    "full stack developer": [
        "React", "Node.js", "TypeScript", "Python", "SQL", "MongoDB",
        "REST APIs", "Docker", "Git", "Tailwind", "Authentication", "Cloud Services",
    ],
}


def extract_raw_text(file_path: str, ext: str) -> str:
    """Extract plain text from PDF or DOCX file."""
    text_content = ""
    try:
        if ext == "pdf":
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
            except Exception as pdf_err:
                logger.info("Structured PDF parsing fallback for %s: %s", file_path, pdf_err)
                # Resilient fallback: extract ASCII printable text streams
                with open(file_path, "rb") as f:
                    raw_bytes = f.read()
                    text_content = re.sub(r"[^\x20-\x7E\n]", " ", raw_bytes.decode("latin1", errors="ignore"))
        elif ext == "docx":
            doc = docx.Document(file_path)
            for p in doc.paragraphs:
                if p.text:
                    text_content += p.text + "\n"
    except Exception as e:
        logger.error("Error reading file %s: %s", file_path, e)
    return text_content.strip()


def heuristic_ats_evaluation(raw_text: str, target_role: str) -> dict:
    """Fallback deterministic ATS scoring when AI provider is offline or quota reached."""
    text_lower = raw_text.lower()
    role_key = target_role.lower().strip()

    # Find closest benchmark or default to software engineer
    benchmark_keywords = ROLE_KEYWORD_BENCHMARKS.get("software engineer", [])
    for role_pattern, kw_list in ROLE_KEYWORD_BENCHMARKS.items():
        if role_pattern in role_key or role_key in role_pattern:
            benchmark_keywords = kw_list
            break

    found_keywords = [kw for kw in benchmark_keywords if re.search(r"\b" + re.escape(kw.lower()) + r"\b", text_lower)]
    missing_keywords = [kw for kw in benchmark_keywords if kw not in found_keywords]

    # Check common resume structural sections
    has_skills = bool(re.search(r"\b(skills|technical competencies|technologies)\b", text_lower))
    has_projects = bool(re.search(r"\b(projects|academic projects|personal projects)\b", text_lower))
    has_experience = bool(re.search(r"\b(experience|internships|work history)\b", text_lower))
    has_education = bool(re.search(r"\b(education|academics|b\.tech|bachelor)\b", text_lower))

    section_scores = {
        "skills": 85 if has_skills else 40,
        "projects": 80 if has_projects else 35,
        "experience": 75 if has_experience else 50,
        "education": 90 if has_education else 60,
    }

    # Keyword match ratio
    keyword_ratio = (len(found_keywords) / max(len(benchmark_keywords), 1))
    ats_score = int(min(98, max(42, (keyword_ratio * 50) + (sum(section_scores.values()) / 4 * 0.5))))
    role_fit = int(min(95, max(38, keyword_ratio * 100)))

    strengths = []
    if found_keywords:
        strengths.append(f"Demonstrates relevant competencies: {', '.join(found_keywords[:4])}.")
    if has_projects:
        strengths.append("Includes practical project experience applicable to entry-level roles.")
    if has_education:
        strengths.append("Clear educational background structure.")

    weaknesses = []
    if missing_keywords:
        weaknesses.append(f"Missing key ATS benchmark keywords for {target_role}: {', '.join(missing_keywords[:4])}.")
    if not has_experience:
        weaknesses.append("No formal internship or work experience section detected.")

    suggestions = [
        f"Incorporate missing industry keywords such as {', '.join(missing_keywords[:3])} into project descriptions.",
        "Quantify project outcomes with concrete metrics (e.g. 'reduced latency by 20%', 'serves 500+ daily requests').",
        "Ensure bullet points start with strong action verbs (Architected, Developed, Engineered, Optimized).",
    ]

    return {
        "ats_score": ats_score,
        "role_fit_percentage": role_fit,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "ats_keywords_missing": missing_keywords,
        "suggestions": suggestions,
        "section_scores": section_scores,
        "parsed_skills": found_keywords,
    }


async def process_and_analyze_resume(
    db: AsyncSession,
    user_id: str,
    file_content: bytes,
    original_filename: str,
    target_role: str,
) -> ResumeAnalysisResponse:
    """Save resume file, extract text, run AI/ATS analysis, and record database entry."""
    # 1. Save file safely
    relative_path, file_size = await storage_service.save_file(
        content=file_content,
        original_filename=original_filename,
        student_id=user_id,
    )
    abs_path = storage_service.get_absolute_path(relative_path)
    ext = original_filename.lower().rsplit(".", 1)[-1]

    # 2. Extract plain text
    raw_text = extract_raw_text(abs_path, ext)

    # 3. Perform Analysis (AI provider or intelligent heuristic fallback)
    analysis_data = None
    if raw_text and len(raw_text) > 50:
        try:
            # Attempt AI structured analysis
            prompt = RESUME_ANALYSIS_PROMPT.format(
                target_role=target_role,
                parsed_json=json.dumps({"text_snippet": raw_text[:3000]}),
            )
            ai_result = await ai_service.generate_structured(prompt)
            if isinstance(ai_result, dict) and "ats_score" in ai_result:
                analysis_data = ai_result
                # Ensure parsed_skills key
                if "parsed_skills" not in analysis_data:
                    analysis_data["parsed_skills"] = ai_result.get("strengths", [])[:5]
        except Exception as e:
            logger.warning("AI resume analysis failed (%s), falling back to rule-based ATS evaluation.", e)

    if not analysis_data:
        analysis_data = heuristic_ats_evaluation(raw_text or original_filename, target_role)

    ats_score = int(analysis_data.get("ats_score", 70))
    role_fit = int(analysis_data.get("role_fit_percentage", 65))
    sec_scores_dict = analysis_data.get("section_scores", {})
    sec_scores = SectionScores(
        skills=int(sec_scores_dict.get("skills", 75)),
        projects=int(sec_scores_dict.get("projects", 70)),
        experience=int(sec_scores_dict.get("experience", 65)),
        education=int(sec_scores_dict.get("education", 80)),
    )

    # 4. Save to database
    resume = Resume(
        user_id=user_id,
        file_path=relative_path,
        original_filename=original_filename,
        file_size_bytes=file_size,
        target_role=target_role,
        parsed_data={"raw_text_length": len(raw_text)},
        ai_suggestions=analysis_data,
        ats_score=ats_score,
        status="done",
    )
    db.add(resume)

    # 5. Log activity
    activity = ActivityLog(
        user_id=user_id,
        activity_type="resume_scanned",
        metadata_json={
            "resume_id": resume.id,
            "target_role": target_role,
            "ats_score": ats_score,
            "filename": original_filename,
        },
    )
    db.add(activity)

    await db.commit()
    await db.refresh(resume)

    return ResumeAnalysisResponse(
        resume_id=resume.id,
        original_filename=original_filename,
        target_role=target_role,
        ats_score=ats_score,
        role_fit_percentage=role_fit,
        strengths=analysis_data.get("strengths", []),
        weaknesses=analysis_data.get("weaknesses", []),
        ats_keywords_missing=analysis_data.get("ats_keywords_missing", []),
        suggestions=analysis_data.get("suggestions", []),
        section_scores=sec_scores,
        parsed_skills=analysis_data.get("parsed_skills", []),
        uploaded_at=resume.uploaded_at,
        status="done",
    )


async def get_user_resumes(db: AsyncSession, user_id: str) -> list[ResumeListItem]:
    """Retrieve history of uploaded resumes for current student."""
    stmt = select(Resume).where(Resume.user_id == user_id).order_by(Resume.uploaded_at.desc())
    res = await db.execute(stmt)
    records = res.scalars().all()
    return [ResumeListItem.model_validate(r) for r in records]


async def get_resume_analysis(db: AsyncSession, user_id: str, resume_id: str) -> ResumeAnalysisResponse | None:
    """Retrieve full analysis of a specific resume scan."""
    stmt = select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
    res = await db.execute(stmt)
    resume = res.scalar_one_or_none()
    if not resume:
        return None

    analysis_data = resume.ai_suggestions or {}
    sec_scores_dict = analysis_data.get("section_scores", {})
    sec_scores = SectionScores(
        skills=int(sec_scores_dict.get("skills", 75)),
        projects=int(sec_scores_dict.get("projects", 70)),
        experience=int(sec_scores_dict.get("experience", 65)),
        education=int(sec_scores_dict.get("education", 80)),
    )

    return ResumeAnalysisResponse(
        resume_id=resume.id,
        original_filename=resume.original_filename,
        target_role=resume.target_role,
        ats_score=resume.ats_score or 70,
        role_fit_percentage=int(analysis_data.get("role_fit_percentage", 65)),
        strengths=analysis_data.get("strengths", []),
        weaknesses=analysis_data.get("weaknesses", []),
        ats_keywords_missing=analysis_data.get("ats_keywords_missing", []),
        suggestions=analysis_data.get("suggestions", []),
        section_scores=sec_scores,
        parsed_skills=analysis_data.get("parsed_skills", []),
        uploaded_at=resume.uploaded_at,
        status=resume.status,
    )


async def get_safe_file_path(db: AsyncSession, user_id: str, resume_id: str) -> tuple[str, str]:
    """Verify student ownership and return (absolute_file_path, original_filename)."""
    stmt = select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
    res = await db.execute(stmt)
    resume = res.scalar_one_or_none()
    if not resume:
        raise FileNotFoundError("Resume record not found.")

    abs_path = storage_service.get_absolute_path(resume.file_path)
    return abs_path, resume.original_filename
