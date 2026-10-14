"""
SubscriptionBillingEngine — Multi-Cycle Subscription & Discount Calculation Engine in MYR.
Supports Monthly, Bi-Yearly (15% Discount), and Yearly (30% Discount / 2 Months FREE).
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger("subscription_billing")

BASE_MONTHLY_RATES_MYR = {
    "free": {"name": "Free Tier", "base_price_myr": 0},
    "sme": {"name": "SME Tier", "base_price_myr": 129},
    "sme_plus": {"name": "SME Plus Tier", "base_price_myr": 399},
    "enterprise": {"name": "Enterprise Tier (Discounted)", "base_price_myr": 799}
}

CYCLE_DISCOUNTS = {
    "monthly": {"name": "Monthly Billing", "discount_pct": 0, "months": 1},
    "bi_yearly": {"name": "Bi-Yearly Billing (Every 6 Months)", "discount_pct": 15, "months": 6},
    "yearly": {"name": "Yearly Billing (Every 12 Months - Save 30%)", "discount_pct": 30, "months": 12}
}


class SubscriptionBillingEngine:
    """
    Calculates multi-cycle subscription pricing, MYR discount savings,
    and generates payment checkout payloads for FPX & Stripe.
    """

    def calculate_plan_price(self, tier: str, cycle: str = "yearly") -> Dict[str, Any]:
        tier_clean = tier.lower().strip()
        cycle_clean = cycle.lower().strip()

        tier_info = BASE_MONTHLY_RATES_MYR.get(tier_clean, BASE_MONTHLY_RATES_MYR["sme_plus"])
        cycle_info = CYCLE_DISCOUNTS.get(cycle_clean, CYCLE_DISCOUNTS["yearly"])

        base_monthly = tier_info["base_price_myr"]
        discount_pct = cycle_info["discount_pct"]
        months = cycle_info["months"]

        effective_monthly_myr = round(base_monthly * (1 - (discount_pct / 100)), 2)
        total_billing_amount_myr = round(effective_monthly_myr * months, 2)
        standard_undiscounted_total = base_monthly * months
        savings_myr = round(standard_undiscounted_total - total_billing_amount_myr, 2)

        return {
            "tier": tier_clean,
            "tier_name": tier_info["name"],
            "billing_cycle": cycle_clean,
            "cycle_name": cycle_info["name"],
            "discount_percentage": discount_pct,
            "base_monthly_rate_myr": base_monthly,
            "effective_monthly_rate_myr": effective_monthly_myr,
            "total_billing_amount_myr": total_billing_amount_myr,
            "savings_amount_myr": savings_myr,
            "currency": "MYR",
            "formatted": {
                "effective_monthly": f"RM {effective_monthly_myr:,.2f}/mo",
                "total_billed": f"RM {total_billing_amount_myr:,.2f}",
                "total_savings": f"RM {savings_myr:,.2f}"
            }
        }

    def get_full_pricing_matrix(self) -> Dict[str, Any]:
        """Returns pricing matrix across all tiers and cycles"""
        matrix = {}
        for tier_key in BASE_MONTHLY_RATES_MYR:
            matrix[tier_key] = {
                "monthly": self.calculate_plan_price(tier_key, "monthly"),
                "bi_yearly": self.calculate_plan_price(tier_key, "bi_yearly"),
                "yearly": self.calculate_plan_price(tier_key, "yearly")
            }
        return {
            "currency": "MYR",
            "cycle_discounts": CYCLE_DISCOUNTS,
            "pricing_matrix": matrix
        }

    def create_checkout_session(self, tier: str, cycle: str, user_email: str) -> Dict[str, Any]:
        """Generates payment checkout session for FPX Online Banking or Stripe"""
        calc = self.calculate_plan_price(tier, cycle)
        session_id = f"cs_myr_{uuid.uuid4().hex[:10]}"

        return {
            "checkout_session_id": session_id,
            "user_email": user_email,
            "plan_details": calc,
            "supported_payment_methods": ["FPX Online Banking (Maybank, CIMB, RHB)", "Credit/Debit Card", "GrabPay", "Touch 'n Go eWallet"],
            "payment_url": f"https://checkout.jebat.online/pay/{session_id}",
            "expires_at": (datetime.utcnow() + timedelta(hours=2)).isoformat()
        }
