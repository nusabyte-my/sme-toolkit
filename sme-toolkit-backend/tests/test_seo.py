"""
Tests for SEO Meta Tag, JSON-LD Schema.org, and On-Page Audit endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_generate_meta_and_schema():
    """Test generating SEO Title, Meta Description, and LocalBusiness JSON-LD Schema"""
    payload = {
        "business_name": "TechServ Solutions MY",
        "industry": "Cloud Hosting & IT",
        "keywords": ["Cloud Hosting MY", "Managed IT KL", "SME Web Dev"],
        "city_location": "Kuala Lumpur, Malaysia",
        "website_url": "https://techserv.com.my"
    }
    response = client.post("/api/v1/seo/generate-meta-schema", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "seo_score" in data
    assert data["seo_score"] >= 90
    assert "TechServ Solutions MY" in data["title_tag"]
    assert data["json_ld_schema"]["@type"] == "LocalBusiness"
    assert data["json_ld_schema"]["address"]["addressCountry"] == "MY"


def test_audit_page_seo():
    """Test on-page SEO audit evaluation"""
    payload = {
        "page_title": "Best Cloud Hosting Services for Malaysian SMEs in Kuala Lumpur",
        "content_body": "Looking for fast cloud hosting in Malaysia? TechServ provides reliable cloud hosting with 99.9% uptime for SMEs.",
        "target_keyword": "cloud hosting"
    }
    response = client.post("/api/v1/seo/audit-page", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "seo_audit_score" in data
    assert data["keyword_occurrences"] >= 2
    assert data["target_keyword"] == "cloud hosting"
