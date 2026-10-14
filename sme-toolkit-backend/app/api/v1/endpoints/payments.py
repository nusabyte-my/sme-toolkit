"""Payment webhooks — converts real payments to token credits"""

import os
import json
import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.services.token_service import TokenService
from app.schemas.tokens import TransactionType
from app.auth import get_current_user, get_admin_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Payments"])

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_...")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:51673")

PACKAGE_MAP = {
    "price_starter_5": {"tokens": 5000, "bonus": 0},
    "price_growth_20": {"tokens": 25000, "bonus": 2500},
    "price_pro_70": {"tokens": 100000, "bonus": 15000},
}


class CheckoutRequest(BaseModel):
    price_id: str


@router.post("/create-checkout-session")
async def create_checkout_session(
    req: CheckoutRequest,
    user_id: str = Depends(get_current_user),
):
    """Creates a Stripe Checkout Session and returns the redirect URL"""
    pkg = PACKAGE_MAP.get(req.price_id)
    if not pkg:
        raise HTTPException(status_code=400, detail=f"Unknown price_id: {req.price_id}")

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY

        session = stripe.checkout.Session.create(
            mode="payment",
            client_reference_id=user_id,
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"{(pkg['tokens'] // 1000)}K Token Pack",
                        "description": f"{pkg['tokens']:,} tokens" + (f" + {pkg['bonus']:,} bonus" if pkg["bonus"] else ""),
                    },
                    "unit_amount": _price_to_cents(req.price_id),
                },
                "quantity": 1,
            }],
            metadata={"price_id": req.price_id},
            success_url=f"{FRONTEND_URL}/billing?session_id={{CHECKOUT_SESSION_ID}}&success=1",
            cancel_url=f"{FRONTEND_URL}/billing?canceled=1",
        )

        return {"url": session.url, "session_id": session.id}

    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Stripe library not installed. Run: pip install stripe"
        )
    except Exception as e:
        logger.error(f"Failed to create Stripe session: {e}")
        raise HTTPException(status_code=502, detail="Payment provider unavailable")


def _price_to_cents(price_id: str) -> int:
    """Maps price_id to unit_amount in cents"""
    prices = {
        "price_starter_5": 500,
        "price_growth_20": 2000,
        "price_pro_70": 7000,
    }
    return prices.get(price_id, 500)


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Receives Stripe checkout.session.completed events and credits tokens"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature")

    event = json.loads(payload)

    if event.get("type") == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("client_reference_id")
        price_id = session.get("metadata", {}).get("price_id")
        payment_id = session.get("id")
        amount_paid = session.get("amount_total", 0) / 100

        if not user_id or not price_id:
            return {"status": "skipped", "reason": "missing user_id or price_id"}

        pkg = PACKAGE_MAP.get(price_id)
        if not pkg:
            return {"status": "skipped", "reason": f"unknown price_id: {price_id}"}

        total_tokens = pkg["tokens"] + pkg["bonus"]
        service = TokenService(db)

        # Ensure token account exists
        account = await service.get_token_account(user_id)
        if not account:
            account = await service.create_token_account(user_id, tier="sme")

        await service.add_tokens(
            user_id=user_id,
            transaction_type=TransactionType.PURCHASE,
            amount=total_tokens,
            metadata={
                "payment_id": payment_id,
                "price_id": price_id,
                "amount_paid": amount_paid,
                "package_tokens": pkg["tokens"],
                "bonus_tokens": pkg["bonus"],
            },
        )

        logger.info(
            f"Credited {total_tokens} tokens to user {user_id} "
            f"via Stripe payment {payment_id}"
        )
        return {"status": "ok", "tokens_credited": total_tokens}

    return {"status": "ignored", "event_type": event.get("type")}


@router.post("/admin/grant")
async def admin_grant_tokens(
    user_id: str,
    amount: int,
    reason: str,
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(get_admin_user),
) -> Dict[str, Any]:
    """Admin-only: grant tokens to any user (onboarding, referral, comp)"""
    service = TokenService(db)

    account = await service.get_token_account(user_id)
    if not account:
        account = await service.create_token_account(user_id)

    await service.add_tokens(
        user_id=user_id,
        transaction_type=TransactionType.BONUS,
        amount=amount,
        metadata={"granted_by": admin, "reason": reason},
    )

    return {"success": True, "user_id": user_id, "tokens_granted": amount, "reason": reason}


@router.get("/packages")
async def get_packages():
    """Public price list for token top-up packages (no auth needed)"""
    return {
        "packages": [
            {
                "id": "starter_5",
                "price_id": "price_starter_5",
                "name": "Starter Pack",
                "tokens": 5000,
                "bonus_tokens": 0,
                "price_usd": 5.00,
            },
            {
                "id": "growth_20",
                "price_id": "price_growth_20",
                "name": "Growth Pack",
                "tokens": 25000,
                "bonus_tokens": 2500,
                "price_usd": 20.00,
            },
            {
                "id": "pro_70",
                "price_id": "price_pro_70",
                "name": "Pro Pack",
                "tokens": 100000,
                "bonus_tokens": 15000,
                "price_usd": 70.00,
            },
        ]
    }
