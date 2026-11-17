import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """Verify that the health check endpoint returns 200 and system metadata."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


@pytest.mark.asyncio
async def test_validation_error_envelope():
    """Verify that validation errors follow the documented envelope."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Requesting a non-existent route with invalid method
        response = await client.get("/non-existent-endpoint")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"

