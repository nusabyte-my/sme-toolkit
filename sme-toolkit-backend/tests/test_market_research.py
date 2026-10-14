"""
Tests for Market Research TAM/SAM/SOM in MYR, Buyer Personas, and Virality Growth Hacks.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_calculate_market_size_myr():
    """Test TAM / SAM / SOM market size calculation in MYR (RM)"""
    payload = {
        "industry": "SME AI Automation & E-Commerce",
        "target_region": "Malaysia"
    }
    response = client.post("/api/v1/market-research/market-size", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "MYR"
    assert "RM 450,000,000" in data["formatted"]["tam"]
    assert data["tam_myr"] > data["sam_myr"] > data["som_myr"]


def test_generate_buyer_personas():
    """Test Malaysian buyer persona generation"""
    payload = {
        "industry": "Cloud Hosting & WhatsApp Bot",
        "product_name": "SME OS V2"
    }
    response = client.post("/api/v1/market-research/buyer-personas", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "personas" in data
    assert len(data["personas"]) >= 2
    assert "WhatsApp" in data["personas"][0]["primary_channels"]


def test_get_virality_growth_hacks():
    """Test retrieving virality growth strategies"""
    response = client.get("/api/v1/market-research/growth-hacks?industry=E-Commerce")
    assert response.status_code == 200
    data = response.json()
    assert "growth_hacks" in data
    assert len(data["growth_hacks"]) >= 3
    assert any("WhatsApp" in g["strategy"] for g in data["growth_hacks"])
