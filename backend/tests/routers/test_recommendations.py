import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_recommendations_workflow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login student
        await client.post(
            "/api/v1/auth/register",
            json={"email": "plan_student@campus.edu", "password": "Password123!", "full_name": "Meera Nair"},
        )
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "plan_student@campus.edu", "password": "Password123!"},
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. First fetch auto-generates recommendations
        res_latest = await client.get("/api/v1/recommendations/latest", headers=headers)
        assert res_latest.status_code == 200, res_latest.text
        data = res_latest.json()
        assert "study_plan" in data
        assert len(data["study_plan"]) >= 2
        assert "resources" in data
        assert len(data["resources"]) >= 3

        # 2. Trigger regenerate
        res_gen = await client.post("/api/v1/recommendations/generate", headers=headers)
        assert res_gen.status_code == 200
        gen_data = res_gen.json()
        assert gen_data["id"] != data["id"]
        assert len(gen_data["study_plan"]) >= 2
        assert gen_data["study_plan"][0]["priority"] in ("high", "medium", "low")

