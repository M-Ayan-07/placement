import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_resume_upload_and_analysis_workflow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register user A
        await client.post(
            "/api/v1/auth/register",
            json={"email": "resume_user@campus.edu", "password": "Password123!", "full_name": "Kavita Rao"},
        )
        login_a = await client.post(
            "/api/v1/auth/login",
            json={"email": "resume_user@campus.edu", "password": "Password123!"},
        )
        token_a = login_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # 1. Reject invalid magic bytes
        fake_file = ("bad.pdf", b"This is not a real PDF file header", "application/pdf")
        res_bad = await client.post(
            "/api/v1/resume/upload",
            headers=headers_a,
            data={"target_role": "Backend Developer"},
            files={"file": fake_file},
        )
        assert res_bad.status_code == 415

        # 2. Upload valid PDF
        sample_pdf_bytes = (
            b"%PDF-1.5\n"
            b"Kavita Rao\n"
            b"Email: resume_user@campus.edu\n"
            b"Skills: Python, FastAPI, PostgreSQL, Docker, Git, REST APIs\n"
            b"Projects: Built Placement Coach API using FastAPI and SQL database with unit testing\n"
            b"Education: B.Tech Computer Science 2026\n"
            b"%%EOF"
        )
        valid_file = ("kavita_resume.pdf", sample_pdf_bytes, "application/pdf")
        res_upload = await client.post(
            "/api/v1/resume/upload",
            headers=headers_a,
            data={"target_role": "Backend Developer"},
            files={"file": valid_file},
        )
        assert res_upload.status_code == 201, res_upload.text
        data = res_upload.json()
        resume_id = data["resume_id"]
        assert data["ats_score"] > 50
        assert data["target_role"] == "Backend Developer"
        assert len(data["strengths"]) > 0
        assert len(data["suggestions"]) > 0

        # 3. List resumes
        res_list = await client.get("/api/v1/resume/list", headers=headers_a)
        assert res_list.status_code == 200
        list_items = res_list.json()
        assert len(list_items) >= 1
        assert list_items[0]["id"] == resume_id

        # 4. Fetch analysis
        res_analysis = await client.get(f"/api/v1/resume/{resume_id}/analysis", headers=headers_a)
        assert res_analysis.status_code == 200
        assert res_analysis.json()["resume_id"] == resume_id

        # 5. Download original file
        res_file = await client.get(f"/api/v1/resume/{resume_id}/file", headers=headers_a)
        assert res_file.status_code == 200
        assert res_file.content.startswith(b"%PDF-")

        # 6. Cross-user isolation: User B cannot access User A's resume
        await client.post(
            "/api/v1/auth/register",
            json={"email": "attacker@campus.edu", "password": "Password123!", "full_name": "User B"},
        )
        login_b = await client.post(
            "/api/v1/auth/login",
            json={"email": "attacker@campus.edu", "password": "Password123!"},
        )
        token_b = login_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        res_cross = await client.get(f"/api/v1/resume/{resume_id}/analysis", headers=headers_b)
        assert res_cross.status_code == 404

