import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_quickwin_categories(client: AsyncClient):
    response = await client.get("/api/v1/quickwins/categories")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["categories"]) >= 3
    assert data["categories"][0]["id"] == "ecommerce"


@pytest.mark.asyncio
async def test_get_active_sales_tips(client: AsyncClient):
    response = await client.get("/api/v1/quickwins/active-tips")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["tips"]) >= 2
    assert data["tips"][0]["urgency"] == "HIGH"


@pytest.mark.asyncio
async def test_execute_quickwin(client: AsyncClient):
    payload = {
        "category": "ecommerce",
        "quickwin_id": "cart_abandonment_recovery",
        "target_audience_count": 25,
        "discount_percentage": 5
    }
    response = await client.post("/api/v1/quickwins/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "execution" in data
    assert data["execution"]["quickwin_id"] == "cart_abandonment_recovery"
    assert data["execution"]["estimated_impact_myr"] == 25 * 45


@pytest.mark.asyncio
async def test_byok_save_and_status(client: AsyncClient):
    save_payload = {
        "user_id": "test_user_1",
        "primary_provider": "deepseek",
        "api_keys": {
            "deepseek": "sk_test_deepseek_key_123",
            "openai": "sk_test_openai_key_456"
        }
    }
    save_resp = await client.post("/api/v1/quickwins/byok-save", json=save_payload)
    assert save_resp.status_code == 200
    assert save_resp.json()["success"] is True

    status_resp = await client.get("/api/v1/quickwins/byok-status?user_id=test_user_1")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["success"] is True
    assert status_data["primary_provider"] == "DEEPSEEK"
    assert len(status_data["connected_providers"]) >= 2
