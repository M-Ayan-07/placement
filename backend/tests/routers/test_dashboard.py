from __future__ import annotations

import io
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_empty_state(client: AsyncClient):
    # Register and login user
    await client.post(
        "/api/v1/auth/register",
        json={"email": "newstudent@campus.edu", "password": "Password123!", "full_name": "New Candidate"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "newstudent@campus.edu", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch dashboard summary
    res = await client.get("/api/v1/dashboard/summary", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["full_name"] == "New Candidate"
    assert data["email"] == "newstudent@campus.edu"
    assert data["total_tests_completed"] == 0
    assert data["assessment_average"] is None
    assert data["best_ats_score"] is None
    assert data["total_interviews_completed"] == 0
    assert data["readiness"]["composite_readiness_score"] >= 0


@pytest.mark.asyncio
async def test_dashboard_populated_lifecycle(client: AsyncClient):
    # 1. Register & Login
    await client.post(
        "/api/v1/auth/register",
        json={"email": "activeuser@campus.edu", "password": "Password123!", "full_name": "Active Jobseeker"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "activeuser@campus.edu", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Update profile & placement goal
    await client.put(
        "/api/v1/profile/me",
        headers=headers,
        json={
            "phone": "+919876543210",
            "college": "National Institute of Technology",
            "branch": "Computer Science",
            "graduation_year": 2026,
            "cgpa": 8.7,
            "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Data Structures"],
        },
    )
    await client.put(
        "/api/v1/profile/goals",
        headers=headers,
        json={
            "target_roles": ["Backend Software Engineer"],
            "target_companies": ["Google", "Microsoft", "Amazon"],
            "target_ctc_lpa": 18.0,
            "preferred_locations": ["Bengaluru", "Hyderabad"],
        },
    )

    # 3. Take assessment test with 1 question
    start_test = await client.post(
        "/api/v1/assessments/sessions/start",
        headers=headers,
        json={"category": "technical", "subcategory": "Data Structures & Algorithms", "num_questions": 1},
    )
    test_data = start_test.json()
    test_session_id = test_data["session_id"]
    q_id = test_data["questions"][0]["id"]

    await client.post(
        f"/api/v1/assessments/sessions/{test_session_id}/submit",
        headers=headers,
        json={"answers": [{"question_id": q_id, "selected_option": 0}]},
    )

    # 4. Upload resume
    fake_pdf = b"%PDF-1.4\n1 0 obj\n<< /Title (Active Jobseeker Resume) /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    await client.post(
        "/api/v1/resume/upload",
        headers=headers,
        files={"file": ("resume.pdf", io.BytesIO(fake_pdf), "application/pdf")},
        data={"target_role": "Backend Software Engineer"},
    )

    # 5. Complete a mock interview
    start_int = await client.post(
        "/api/v1/interview/start",
        headers=headers,
        json={"interview_type": "technical", "topic": "Data Structures & Algorithms"},
    )
    int_session_id = start_int.json()["id"]

    # Complete 10 turns of interview
    for turn in range(1, 11):
        await client.post(
            f"/api/v1/interview/{int_session_id}/answer",
            headers=headers,
            json={"answer": f"Answer for turn {turn}: We analyze time complexity, space complexity, and state algorithmic trade-offs."},
        )

    # 6. Fetch Dashboard Summary
    dash_res = await client.get("/api/v1/dashboard/summary", headers=headers)
    assert dash_res.status_code == 200
    dash = dash_res.json()

    assert dash["full_name"] == "Active Jobseeker"
    assert dash["target_role"] == "Backend Software Engineer"
    assert dash["target_ctc_lpa"] == 18.0
    assert dash["total_tests_completed"] == 1
    assert dash["assessment_average"] is not None
    assert dash["best_ats_score"] is not None
    assert dash["total_interviews_completed"] == 1
    assert dash["interview_average"] is not None

    # Readiness composite should now reflect full profile, tests, resume, and mock interview
    assert dash["readiness"]["composite_readiness_score"] >= 35
    assert dash["readiness"]["readiness_level"] in ["Developing", "Needs Preparation", "Proficient", "Placement Ready"]
    assert len(dash["recent_activities"]) >= 3


@pytest.mark.asyncio
async def test_dashboard_unauthorized(client: AsyncClient):
    res = await client.get("/api/v1/dashboard/summary")
    assert res.status_code == 401
