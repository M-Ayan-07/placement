import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_auth_and_profile_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Register a new student
        register_payload = {
            "email": "test_student@campus.edu",
            "password": "Password123!",
            "full_name": "Aarav Sharma",
        }
        res_reg = await client.post("/api/v1/auth/register", json=register_payload)
        assert res_reg.status_code == 201, res_reg.text
        user_data = res_reg.json()
        assert user_data["email"] == "test_student@campus.edu"
        assert user_data["profile"]["full_name"] == "Aarav Sharma"

        # 2. Duplicate registration rejected
        res_dup = await client.post("/api/v1/auth/register", json=register_payload)
        assert res_dup.status_code == 409
        assert res_dup.json()["error"]["code"] == "DUPLICATE_EMAIL"

        # 3. Login with bad password
        res_bad_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "test_student@campus.edu", "password": "WrongPassword"},
        )
        assert res_bad_login.status_code == 401
        assert res_bad_login.json()["error"]["code"] == "INVALID_CREDENTIALS"

        # 4. Login with correct credentials
        res_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "test_student@campus.edu", "password": "Password123!"},
        )
        assert res_login.status_code == 200
        login_data = res_login.json()
        access_token = login_data["access_token"]
        assert access_token is not None
        assert "refresh_token" in res_login.cookies
        refresh_cookie = res_login.cookies["refresh_token"]

        headers = {"Authorization": f"Bearer {access_token}"}

        # 5. Access profile with token
        res_me = await client.get("/api/v1/profile/me", headers=headers)
        assert res_me.status_code == 200
        assert res_me.json()["email"] == "test_student@campus.edu"

        # 6. Unauthenticated profile access fails
        res_unauth = await client.get("/api/v1/profile/me")
        assert res_unauth.status_code == 401

        # 7. Update profile
        update_profile_payload = {
            "college": "IIT Delhi",
            "branch": "Computer Science & Engineering",
            "graduation_year": 2026,
            "cgpa": 8.75,
            "skills": ["Python", "FastAPI", "React", "SQL"],
            "bio": "Aspiring Software Development Engineer.",
        }
        res_update_prof = await client.put(
            "/api/v1/profile/me",
            headers=headers,
            json=update_profile_payload,
        )
        assert res_update_prof.status_code == 200
        prof_data = res_update_prof.json()
        assert prof_data["college"] == "IIT Delhi"
        assert prof_data["cgpa"] == 8.75
        assert "FastAPI" in prof_data["skills"]

        # 8. Update placement goals
        update_goals_payload = {
            "target_roles": ["SDE-1", "Backend Engineer"],
            "target_companies": ["Google", "Microsoft", "Amazon"],
            "target_ctc_lpa": 24.5,
            "preferred_locations": ["Bangalore", "Hyderabad"],
        }
        res_update_goals = await client.put(
            "/api/v1/profile/goals",
            headers=headers,
            json=update_goals_payload,
        )
        assert res_update_goals.status_code == 200
        goals_data = res_update_goals.json()
        assert "SDE-1" in goals_data["target_roles"]
        assert goals_data["target_ctc_lpa"] == 24.5

        # 9. Verify updated profile & goals through GET /profile/me
        res_me_updated = await client.get("/api/v1/profile/me", headers=headers)
        assert res_me_updated.status_code == 200
        me_data = res_me_updated.json()
        assert me_data["profile"]["college"] == "IIT Delhi"
        assert me_data["goals"]["target_ctc_lpa"] == 24.5

        # 10. Refresh token rotation
        client.cookies.set("refresh_token", refresh_cookie)
        res_refresh = await client.post("/api/v1/auth/refresh")
        assert res_refresh.status_code == 200
        new_token_data = res_refresh.json()
        new_access_token = new_token_data["access_token"]
        assert new_access_token != access_token

        # 11. Logout
        res_logout = await client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {new_access_token}"})
        assert res_logout.status_code == 200

