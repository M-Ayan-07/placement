import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_assessments_workflow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login student
        await client.post(
            "/api/v1/auth/register",
            json={"email": "exam_student@campus.edu", "password": "Password123!", "full_name": "Rohan Verma"},
        )
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "exam_student@campus.edu", "password": "Password123!"},
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Browse categories
        cat_res = await client.get("/api/v1/assessments/categories", headers=headers)
        assert cat_res.status_code == 200
        cat_data = cat_res.json()["categories"]
        assert "aptitude" in cat_data
        assert "technical" in cat_data

        # 2. Start a test session for DSA
        start_payload = {
            "category": "technical",
            "subcategory": "dsa",
            "num_questions": 3,
        }
        start_res = await client.post("/api/v1/assessments/sessions/start", headers=headers, json=start_payload)
        assert start_res.status_code == 200
        start_data = start_res.json()
        session_id = start_data["session_id"]
        questions = start_data["questions"]
        assert len(questions) > 0
        assert "correct_option" not in questions[0]  # Verify answer is not leaked

        # 3. Submit responses
        answers = []
        for q in questions:
            # Pick option 0 for all
            answers.append({"question_id": q["id"], "selected_option": 0})

        submit_payload = {
            "answers": answers,
            "time_taken_seconds": 95,
        }
        submit_res = await client.post(
            f"/api/v1/assessments/sessions/{session_id}/submit",
            headers=headers,
            json=submit_payload,
        )
        assert submit_res.status_code == 200
        result_data = submit_res.json()
        assert "score" in result_data
        assert "percentage" in result_data
        assert "weak_topics" in result_data
        assert len(result_data["breakdown"]) == len(questions)
        # Breakdown includes explanation and correct option
        assert "explanation" in result_data["breakdown"][0]
        assert "correct_option" in result_data["breakdown"][0]

        # 4. Fetch result details
        fetch_res = await client.get(f"/api/v1/assessments/sessions/{session_id}/result", headers=headers)
        assert fetch_res.status_code == 200
        assert fetch_res.json()["session_id"] == session_id

        # 5. Verify history
        hist_res = await client.get("/api/v1/assessments/history", headers=headers)
        assert hist_res.status_code == 200
        history = hist_res.json()
        assert len(history) >= 1
        assert history[0]["session_id"] == session_id

