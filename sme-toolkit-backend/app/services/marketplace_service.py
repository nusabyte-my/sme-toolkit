import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class MarketplaceService:
    def __init__(self):
        # Configuration for each platform (would come from settings/env in real app)
        self.configs = {
            "shopee": {
                "auth_url": "https://partner.shopeemobile.com/api/v2/shop/auth_partner",
                "client_id": "mock_shopee_client_id",
                "redirect_uri": "http://localhost:8000/api/v1/sales/auth/shopee/callback"
            },
            "lazada": {
                "auth_url": "https://auth.lazada.com/oauth/authorize",
                "client_id": "mock_lazada_client_id",
                "redirect_uri": "http://localhost:8000/api/v1/sales/auth/lazada/callback"
            },
            "tiktok": {
                "auth_url": "https://services.tiktokshop.com/open/authorize",
                "client_id": "mock_tiktok_client_id",
                "redirect_uri": "http://localhost:8000/api/v1/sales/auth/tiktok/callback"
            }
        }

    def get_auth_url(self, platform: str) -> str:
        """Generate OAuth authorization URL for the platform"""
        config = self.configs.get(platform.lower())
        if not config:
            raise ValueError(f"Unsupported platform: {platform}")
        
        state = uuid.uuid4().hex
        
        # Construct URL based on platform specifics
        # This is a simplified/mocked version compliant with standard OAuth2 patterns
        base_url = config["auth_url"]
        client_id = config["client_id"]
        redirect_uri = config["redirect_uri"]
        
        return f"{base_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&state={state}"

    async def exchange_code_for_token(self, platform: str, code: str, shop_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        MOCKED implementation.
        """
        # In a real implementation, this would make a POST request to the platform's token endpoint
        # import httpx
        # response = await httpx.post(...)
        
        # Mock response
        return {
            "access_token": f"mock_access_token_{platform}_{uuid.uuid4().hex[:8]}",
            "refresh_token": f"mock_refresh_token_{platform}_{uuid.uuid4().hex[:8]}",
            "expires_in": 86400, # 24 hours
            "shop_id": shop_id or f"shop_{uuid.uuid4().hex[:6]}",
            "shop_name": f"My {platform.capitalize()} Shop"
        }

    async def refresh_token(self, platform: str, refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired access token"""
        return {
            "access_token": f"new_mock_access_token_{platform}_{uuid.uuid4().hex[:8]}",
            "expires_in": 86400
        }

    def map_order_data(self, platform: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map platform-specific order data to our unified model"""
        # This would handle the differences between Shopee, Lazada, etc. JSON structures
        # Mock implementation returning standard format
        return {
            "platform": platform,
            "external_id": raw_data.get("order_sn") or raw_data.get("order_id"),
            "amount": float(raw_data.get("total_amount") or raw_data.get("price", 0)),
            "currency": raw_data.get("currency", "USD"),
            "status": raw_data.get("status", "completed"),
            "transaction_date": datetime.utcnow(), # Parse actual date in real impl
            "customer_info": {
                "name": raw_data.get("buyer_username")
            }
        }

marketplace_service = MarketplaceService()
