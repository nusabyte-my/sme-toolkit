import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_marketplace_auth_flow(async_client: AsyncClient, db_session: AsyncSession):
    # 1. Get Auth URL
    response = await async_client.get("/api/v1/sales/auth/shopee/url")
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "https://partner.shopeemobile.com" in data["url"]

    # 2. Simulate Callback
    # We need to authenticate first or mock user
    # The async_client fixture should handle auth if set up correctly or we use a dependency override
    
    # For now, let's assume the client is authenticated as "test_user"
    
    callback_response = await async_client.get(
        "/api/v1/sales/auth/shopee/callback",
        params={"code": "mock_code", "shop_id": "12345"}
    )
    # It should redirect
    assert callback_response.status_code == 307
    
    # 3. Check Connections
    conn_response = await async_client.get("/api/v1/sales/connections")
    assert conn_response.status_code == 200
    conns = conn_response.json()
    assert len(conns) > 0
    assert conns[0]["platform"] == "shopee"
    assert conns[0]["status"] == "active"

@pytest.mark.asyncio
async def test_disconnect_marketplace(async_client: AsyncClient):
    # Disconnect
    response = await async_client.delete("/api/v1/sales/connections/shopee")
    assert response.status_code == 200
    
    # Verify
    conn_response = await async_client.get("/api/v1/sales/connections")
    conns = conn_response.json()
    assert len(conns) == 0
