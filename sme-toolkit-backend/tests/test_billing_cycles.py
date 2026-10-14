"""
Tests for Subscription Billing Cycles (Monthly, Bi-Yearly 15% OFF, Yearly 30% OFF) and MYR pricing calculations.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_full_pricing_plans_myr():
    """Test retrieving full pricing matrix across all tiers and cycles"""
    res = client.get("/api/v1/billing-v2/plans-myr")
    assert res.status_code == 200
    data = res.json()
    assert data["currency"] == "MYR"
    assert "enterprise" in data["pricing_matrix"]
    # Check Enterprise price (RM799 base)
    ent_yearly = data["pricing_matrix"]["enterprise"]["yearly"]
    assert ent_yearly["base_monthly_rate_myr"] == 799
    assert ent_yearly["discount_percentage"] == 30


def test_calculate_bi_yearly_discount():
    """Test calculating 15% discount on Bi-Yearly cycle for SME Plus tier (RM399/mo)"""
    payload = {
        "tier": "sme_plus",
        "cycle": "bi_yearly"
    }
    res = client.post("/api/v1/billing-v2/calculate-price", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["discount_percentage"] == 15
    assert data["base_monthly_rate_myr"] == 399
    # 399 * (1 - 0.15) = 339.15
    assert data["effective_monthly_rate_myr"] == 339.15
    assert data["savings_amount_myr"] > 0


def test_calculate_yearly_discount_enterprise():
    """Test calculating 30% discount on Yearly cycle for Enterprise tier (RM799/mo)"""
    payload = {
        "tier": "enterprise",
        "cycle": "yearly"
    }
    res = client.post("/api/v1/billing-v2/calculate-price", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["discount_percentage"] == 30
    assert data["base_monthly_rate_myr"] == 799
    # 799 * (1 - 0.30) = 559.30
    assert data["effective_monthly_rate_myr"] == 559.30
    assert "RM 559.30/mo" in data["formatted"]["effective_monthly"]


def test_create_checkout_session():
    """Test creating an FPX / Card checkout session"""
    payload = {
        "tier": "sme_plus",
        "cycle": "yearly",
        "user_email": "ahmad@techserv.com.my"
    }
    res = client.post("/api/v1/billing-v2/checkout", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "checkout_session_id" in data
    assert "https://checkout.jebat.online/pay/" in data["payment_url"]
    assert any("FPX" in m for m in data["supported_payment_methods"])
