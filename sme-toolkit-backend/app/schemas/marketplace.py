from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MarketplaceConnectionBase(BaseModel):
    platform: str
    shop_id: Optional[str] = None
    shop_name: Optional[str] = None
    status: str

class MarketplaceConnectionCreate(MarketplaceConnectionBase):
    access_token: str
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None

class MarketplaceConnectionResponse(MarketplaceConnectionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AuthUrlResponse(BaseModel):
    url: str
    state: str

class MarketplaceCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None
    shop_id: Optional[str] = None
