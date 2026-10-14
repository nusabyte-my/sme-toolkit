"""
Smoke tests for token billing API endpoints
"""
import pytest
from httpx import AsyncClient

from app.main import app
from app.database import get_db
from app.auth import get_current_user


@pytest.mark.asyncio
async def test_get_balance_returns_200_with_balance(client: AsyncClient):
    """GET /api/v1/tokens/balance returns 200 with balance field"""
    app.dependency_overrides[get_current_user] = lambda: "test-user"

    response = await client.get("/api/v1/tokens/balance")

    app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "balance" in data["data"]


@pytest.mark.asyncio
async def test_consume_tokens_returns_402_when_insufficient(client: AsyncClient):
    """POST /api/v1/tokens/consume returns 402 when balance too low"""
    app.dependency_overrides[get_current_user] = lambda: "test-user"

    response = await client.post(
        "/api/v1/tokens/consume",
        json={"amount": 999999, "service_type": "text_llm"},
    )

    app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 402
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_add_tokens_returns_200_with_balance(client: AsyncClient):
    """POST /api/v1/tokens/add returns 200 with new balance"""
    app.dependency_overrides[get_current_user] = lambda: "test-user"

    response = await client.post(
        "/api/v1/tokens/add",
        json={"amount": 500, "source": "testing"},
    )

    app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    data = response.json()
    assert data.get("success")
    assert "balance" in data


@pytest.mark.asyncio
async def test_consume_tokens_returns_400_on_invalid_service(client: AsyncClient):
    """POST /api/v1/tokens/consume returns 400 for bad service_type"""
    app.dependency_overrides[get_current_user] = lambda: "test-user"

    response = await client.post(
        "/api/v1/tokens/consume",
        json={"amount": 10, "service_type": "nonexistent_service"},
    )

    app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_packages_returns_packages(client: AsyncClient):
    """GET /api/v1/subscription/packages returns package list"""
    response = await client.get("/api/v1/subscription/packages")

    assert response.status_code == 200
    data = response.json()
    assert "packages" in data
    assert len(data["packages"]) > 0
