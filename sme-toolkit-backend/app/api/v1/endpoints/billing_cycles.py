"""
Subscription Billing Cycles FastAPI Router for SME OS V2.
Handles multi-cycle pricing calculation (Monthly, Bi-Yearly 15% OFF, Yearly 30% OFF) and FPX/Stripe Checkout sessions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.services.subscription_billing import SubscriptionBillingEngine

router = APIRouter()
billing_engine = SubscriptionBillingEngine()


class CalculatePriceRequest(BaseModel):
    tier: str = Field(..., description="Tier name: 'sme', 'sme_plus', 'enterprise'")
    cycle: str = Field("yearly", description="Billing cycle: 'monthly', 'bi_yearly', 'yearly'")


class CheckoutSessionRequest(BaseModel):
    tier: str = Field(...)
    cycle: str = Field("yearly")
    user_email: str = Field(..., description="Customer email address")


@router.get("/plans-myr", summary="Get Full Multi-Cycle Pricing Matrix in MYR")
async def get_plans_matrix():
    """Returns full pricing matrix for Monthly, Bi-Yearly (15% OFF), and Yearly (30% OFF) plans"""
    return billing_engine.get_full_pricing_matrix()


@router.post("/calculate-price", summary="Calculate Subscription Plan Price & Savings")
async def calculate_price(req: CalculatePriceRequest):
    """Calculates effective monthly rate, total billing amount, and MYR savings"""
    return billing_engine.calculate_plan_price(req.tier, req.cycle)


@router.post("/checkout", summary="Create FPX / Card Payment Checkout Session")
async def create_checkout(req: CheckoutSessionRequest):
    """Generates a checkout session link for FPX Online Banking and Card payments"""
    return billing_engine.create_checkout_session(
        tier=req.tier,
        cycle=req.cycle,
        user_email=req.user_email
    )
