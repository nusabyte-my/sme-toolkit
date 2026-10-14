"""QuickWins & BYOK Agent Management Endpoint"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
import uuid
import datetime

router = APIRouter()

# Memory state for demo BYOK and QuickWin executions
_BYOK_VAULT: Dict[str, Dict[str, str]] = {
    "default": {
        "primary_provider": "gemini",
        "gemini_key": "AIzaSy_MOCK_GEMINI_KEY",
        "deepseek_key": "sk_MOCK_DEEPSEEK_KEY",
        "openai_key": "sk-proj-MOCK_OPENAI_KEY",
        "groq_key": "gsk_MOCK_GROQ_KEY"
    }
}

_EXECUTED_QUICKWINS: List[Dict[str, Any]] = []


class BYOKRequest(BaseModel):
    user_id: str = "default"
    primary_provider: str = Field(default="gemini", description="Selected primary LLM provider (gemini, deepseek, openai, groq, fiqstr)")
    api_keys: Dict[str, str] = Field(default_factory=dict, description="Dictionary of provider -> API key")


class ExecuteQuickWinRequest(BaseModel):
    category: str = Field(..., description="Business sub-category: ecommerce, fnb, services, saas, logistics")
    quickwin_id: str = Field(..., description="ID of the quickwin recipe to trigger")
    target_audience_count: int = Field(default=50, description="Target customer segment count")
    discount_percentage: Optional[int] = Field(default=10, description="Optional discount or voucher %")


@router.get("/categories")
async def get_quickwin_categories():
    """Return list of business sub-categories and pre-configured quickwin recipes with estimated MYR ROI."""
    return {
        "success": True,
        "categories": [
            {
                "id": "ecommerce",
                "name": "E-Commerce & Online Retail",
                "icon": "ShoppingBag",
                "description": "Shopee, TikTok Shop, Lazada & Direct Webstores",
                "quickwins": [
                    {
                        "id": "cart_abandonment_recovery",
                        "title": "Automated Cart Abandonment Winback",
                        "channel": "WhatsApp Bot",
                        "estimated_conversion_lift": "+28%",
                        "estimated_monthly_revenue_myr": 4200,
                        "description": "Auto-pings buyers who dropped off checkout within 15 mins with a custom 5% voucher code.",
                        "recommended_tier": "SME_PLUS"
                    },
                    {
                        "id": "cross_sell_bundle",
                        "title": "Post-Purchase Bundle Upsell",
                        "channel": "Telegram & Web",
                        "estimated_conversion_lift": "+18%",
                        "estimated_monthly_revenue_myr": 3100,
                        "description": "Auto-recommends matching accessories right after an order is confirmed.",
                        "recommended_tier": "SME"
                    }
                ]
            },
            {
                "id": "fnb",
                "name": "F&B & Retail Stores",
                "icon": "Utensils",
                "description": "Restaurants, Cafes, Cloud Kitchens & Local Retail",
                "quickwins": [
                    {
                        "id": "google_review_booster",
                        "title": "5-Star Google Review Booster",
                        "channel": "WhatsApp SMS",
                        "estimated_conversion_lift": "+45% Reviews",
                        "estimated_monthly_revenue_myr": 2500,
                        "description": "Sends a friendly WhatsApp message 1 hour post-meal/visit inviting a 5-star review in exchange for a free drink on next visit.",
                        "recommended_tier": "SME"
                    },
                    {
                        "id": "rainy_day_promo",
                        "title": "Dynamic Weather/Rainy Day Flash Sale",
                        "channel": "Social Media & WhatsApp",
                        "estimated_conversion_lift": "+35%",
                        "estimated_monthly_revenue_myr": 1800,
                        "description": "Triggers 15% off delivery discount when local rain alerts occur in Klang Valley/Penang/JB.",
                        "recommended_tier": "SME_PLUS"
                    }
                ]
            },
            {
                "id": "services",
                "name": "Professional Services & B2B",
                "icon": "Briefcase",
                "description": "Agencies, Consultants, Accounting, Legal & Contractors",
                "quickwins": [
                    {
                        "id": "instant_quotation_bot",
                        "title": "Instant WhatsApp AI Quotation Draft",
                        "channel": "WhatsApp & Email",
                        "estimated_conversion_lift": "+40%",
                        "estimated_monthly_revenue_myr": 8500,
                        "description": "BANT-qualifies leads on WhatsApp and generates an instant formal PDF quote in MYR.",
                        "recommended_tier": "SME_PLUS"
                    },
                    {
                        "id": "lapsed_client_reactivation",
                        "title": "Dormant Client Audit & Reactivation",
                        "channel": "Email & WhatsApp",
                        "estimated_conversion_lift": "+15%",
                        "estimated_monthly_revenue_myr": 6200,
                        "description": "Scans past client database (>90 days inactive) and sends a personalized complimentary business health check.",
                        "recommended_tier": "ENTERPRISE"
                    }
                ]
            }
        ]
    }


@router.get("/active-tips")
async def get_active_sales_tips():
    """Return live active tips with pulsing urgency badges for immediate sales optimization."""
    return {
        "success": True,
        "tips": [
            {
                "id": "tip_flash_sale",
                "title": "🔥 Active Flash Sale Opportunity",
                "category": "E-Commerce",
                "urgency": "HIGH",
                "pulse": True,
                "message": "Cart abandonment peak detected (14 pending carts in last 2 hours). Trigger WhatsApp Broadcast now to recover an estimated RM 1,850.",
                "action_label": "Trigger Flash Broadcast Now",
                "quickwin_id": "cart_abandonment_recovery"
            },
            {
                "id": "tip_review_booster",
                "title": "⭐ Google Review Velocity",
                "category": "Customer Satisfaction",
                "urgency": "MEDIUM",
                "pulse": True,
                "message": "28 customers completed purchases today. Auto-send 5-star Google review invitations via WhatsApp.",
                "action_label": "Launch Review Booster",
                "quickwin_id": "google_review_booster"
            },
            {
                "id": "tip_byok_routing",
                "title": "⚡ BYOK Cost Optimization",
                "category": "System Performance",
                "urgency": "LOW",
                "pulse": False,
                "message": "Switching primary LLM routing to DeepSeek-V3 for low-tier queries can lower monthly token expense by 62%.",
                "action_label": "Configure BYOK Vault",
                "quickwin_id": "byok_routing"
            }
        ]
    }


@router.post("/execute")
async def execute_quickwin(req: ExecuteQuickWinRequest):
    """Execute a selected QuickWin automation recipe."""
    execution_id = f"qw-{uuid.uuid4().hex[:8]}"
    estimated_revenue = req.target_audience_count * 45  # Average ticket RM45
    
    record = {
        "execution_id": execution_id,
        "category": req.category,
        "quickwin_id": req.quickwin_id,
        "status": "ACTIVE_RUNNING",
        "target_audience_count": req.target_audience_count,
        "estimated_impact_myr": estimated_revenue,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "log": f"Initiated {req.quickwin_id} for {req.target_audience_count} audience members. Active bot listening enabled."
    }
    _EXECUTED_QUICKWINS.append(record)
    
    return {
        "success": True,
        "message": f"QuickWin '{req.quickwin_id}' successfully activated!",
        "execution": record
    }


@router.post("/byok-save")
async def save_byok_credentials(payload: BYOKRequest):
    """Save Bring-Your-Own-Key (BYOK) provider credentials."""
    user_id = payload.user_id
    if user_id not in _BYOK_VAULT:
        _BYOK_VAULT[user_id] = {}
        
    _BYOK_VAULT[user_id]["primary_provider"] = payload.primary_provider
    for provider, key in payload.api_keys.items():
        if key.strip():
            _BYOK_VAULT[user_id][f"{provider}_key"] = key
            
    return {
        "success": True,
        "message": f"BYOK configuration saved. Primary provider set to '{payload.primary_provider.upper()}'.",
        "active_providers": list(payload.api_keys.keys())
    }


@router.get("/byok-status")
async def get_byok_status(user_id: str = "default"):
    """Get active BYOK status and connected LLM providers."""
    vault = _BYOK_VAULT.get(user_id, {})
    providers = []
    for k in ["gemini", "deepseek", "openai", "groq", "fiqstr"]:
        if f"{k}_key" in vault:
            providers.append({
                "name": k.upper(),
                "status": "Connected",
                "latency_ms": 140 if k == "groq" else 280,
                "cost_per_1k_myr": "RM 0.002" if k == "deepseek" else "RM 0.008"
            })
            
    return {
        "success": True,
        "primary_provider": vault.get("primary_provider", "gemini").upper(),
        "connected_providers": providers
    }
