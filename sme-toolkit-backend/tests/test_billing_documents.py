import pytest
import html
from decimal import Decimal
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.auth import get_current_user
from app.database import get_db, BusinessProfile, BillingCustomer, CommercialDocument
from app.services.owner_service import context_data
from app.api.v1.endpoints.billing import build_document_html, totals, ItemInput, create_document_record


def test_context_data_returns_logo_data_url():
    profile = MagicMock(spec=BusinessProfile)
    profile.id = "biz-123"
    profile.company_name = "Acme Corp"
    profile.industry = "Tech"
    profile.website = "https://acme.com"
    profile.updated_at = None

    # Test 1: logo in owner_context
    profile.meta_json = {
        "owner_context": {
            "logo_data_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg==",
            "business_description": "We make anvils",
            "currency": "MYR",
            "timezone": "Asia/Kuala_Lumpur",
        }
    }
    data = context_data(profile)
    assert data is not None
    assert "logo_data_url" in data
    assert data["logo_data_url"] == "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg=="

    # Test 2: logo fallback in top-level meta_json
    profile.meta_json = {
        "logo_data_url": "data:image/svg+xml;utf8,<svg></svg>",
        "owner_context": {},
    }
    data2 = context_data(profile)
    assert data2["logo_data_url"] == "data:image/svg+xml;utf8,<svg></svg>"

    # Test 3: empty logo
    profile.meta_json = {}
    data3 = context_data(profile)
    assert data3["logo_data_url"] == ""


def test_build_document_html_renders_logo_and_layout():
    row = MagicMock(spec=CommercialDocument)
    row.id = "doc-1"
    row.kind = "invoice"
    row.number = "INV-2026-00001"
    row.status = "draft"
    row.day = "2026-10-07"
    row.due_date = "2026-11-06"
    row.currency = "MYR"
    row.subtotal_cents = 10000
    row.discount_cents = 1000
    row.tax_cents = 540
    row.total_cents = 9540
    row.notes = "Payment via bank transfer."
    row.terms = "Net 30 days."
    row.seller = {
        "name": "Acme Solutions Sdn Bhd",
        "address": "Kuala Lumpur, Malaysia",
        "registration_number": "202401099999",
        "email": "billing@acme.com.my",
        "website": "https://acme.com.my",
        "logo_data_url": "data:image/png;base64,testlogodata",
        "demo": False,
    }
    row.customer = {
        "name": "Global Client Ltd",
        "address": "123 Business Way, Singapore",
        "registration_number": "SG123456",
        "email": "finance@globalclient.com",
    }
    row.lines = [
        {
            "description": "Consulting Services",
            "quantity": "1.000",
            "unit_price_cents": 10000,
            "discount_cents": 1000,
            "tax_percent": "6.00",
            "tax_cents": 540,
            "total_cents": 9540,
        }
    ]

    # Test print version (is_preview=False)
    html_print = build_document_html(row, paid=3000, is_preview=False)
    assert '<body >' in html_print or '<body data-preview' not in html_print
    assert 'data-preview' not in html_print.split('<body')[1].split('>')[0]
    assert '<img src="data:image/png;base64,testlogodata" alt="Logo" class="logo">' in html_print
    assert "Acme Solutions Sdn Bhd" in html_print
    assert "Kuala Lumpur, Malaysia" in html_print
    assert "Reg No: 202401099999" in html_print
    assert "Global Client Ltd" in html_print
    assert "123 Business Way, Singapore" in html_print
    assert "Consulting Services" in html_print
    assert "INV-2026-00001" in html_print
    assert "Paid:" in html_print
    assert "Balance Due:" in html_print
    assert "MYR 30.00" in html_print
    assert "MYR 65.40" in html_print  # 95.40 - 30.00
    assert "Payment via bank transfer." in html_print
    assert "Net 30 days." in html_print

    # Test preview version (is_preview=True)
    html_prev = build_document_html(row, paid=0, is_preview=True)
    assert '<body data-preview>' in html_prev
    assert '<img src="data:image/png;base64,testlogodata" alt="Logo" class="logo">' in html_prev


def test_build_document_html_no_logo_and_quotation():
    row = MagicMock(spec=CommercialDocument)
    row.id = "doc-2"
    row.kind = "quotation"
    row.number = "QUO-2026-00005"
    row.status = "issued"
    row.day = "2026-10-07"
    row.due_date = "2026-10-21"
    row.currency = "MYR"
    row.subtotal_cents = 50000
    row.discount_cents = 0
    row.tax_cents = 0
    row.total_cents = 50000
    row.notes = ""
    row.terms = ""
    row.seller = {
        "name": "Simple Store",
        "address": "Penang, Malaysia",
        "registration_number": "",
        "email": "store@simple.com",
        "website": "",
        "logo_data_url": "",
        "demo": True,
    }
    row.customer = {
        "name": "Shopper One",
        "address": "",
        "registration_number": "",
        "email": "",
    }
    row.lines = []

    html_out = build_document_html(row, paid=0, is_preview=False)
    # When logo is empty, no <img ... class="logo"> tag should be rendered
    assert '<img src=""' not in html_out
    assert 'class="logo"' not in html_out
    assert "QUOTATION" in html_out
    assert "Valid Until:" in html_out
    assert "DEMO — fictional business and values" in html_out
    assert "Quote For" in html_out
    # Quotations should not display invoice payment/balance rows
    assert "Balance Due:" not in html_out


@pytest.mark.asyncio
async def test_seller_snapshot_in_create_document_record(test_db):
    profile = BusinessProfile(
        user_id="user-seller-test",
        company_name="Alpha Tech Enterprise",
        city="Subang Jaya",
        country="Malaysia",
        contact_email="owner@alphatech.com",
        website="https://alphatech.com",
        meta_json={
            "registration_number": "SSM-998877",
            "owner_context": {
                "logo_data_url": "data:image/svg+xml;utf8,<svg>Alpha</svg>",
                "currency": "MYR",
            }
        }
    )
    test_db.add(profile)
    await test_db.flush()

    customer = BillingCustomer(
        business_profile_id=profile.id,
        name="Target Customer Sdn Bhd",
        email="target@example.com",
        address="Cyberjaya, Malaysia",
        registration_number="CUST-12345",
    )
    test_db.add(customer)
    await test_db.flush()

    from app.api.v1.endpoints.billing import DocumentInput
    doc_input = DocumentInput(
        customer_id=customer.id,
        kind="invoice",
        day="2026-10-07",
        due_date="2026-11-07",
        notes="Thank you for your business.",
        terms="COD",
        lines=[
            ItemInput(
                description="Web Development",
                quantity=Decimal("1"),
                unit_price=Decimal("1500.00"),
                discount=Decimal("100.00"),
                tax_percent=Decimal("0"),
            )
        ]
    )

    doc = await create_document_record(test_db, profile, doc_input)
    assert doc.id is not None
    assert doc.seller["name"] == "Alpha Tech Enterprise"
    assert doc.seller["address"] == "Subang Jaya, Malaysia"
    assert doc.seller["registration_number"] == "SSM-998877"
    assert doc.seller["logo_data_url"] == "data:image/svg+xml;utf8,<svg>Alpha</svg>"
    assert doc.seller["email"] == "owner@alphatech.com"


@pytest.mark.asyncio
async def test_print_and_preview_endpoints(test_db):
    profile = BusinessProfile(
        user_id="user-preview-test",
        company_name="Omega Corp",
        city="Kuala Lumpur",
        country="Malaysia",
        contact_email="info@omega.com",
        website="https://omega.com",
        meta_json={
            "registration_number": "ROC-112233",
            "owner_context": {
                "logo_data_url": "data:image/png;base64,omega_logo",
                "currency": "MYR",
            }
        }
    )
    test_db.add(profile)
    await test_db.flush()

    customer = BillingCustomer(
        business_profile_id=profile.id,
        name="Beta Buyer",
        email="buyer@beta.com",
        address="10 Jalan Bukit, KL",
        registration_number="REG-9900",
    )
    test_db.add(customer)
    await test_db.flush()

    from app.api.v1.endpoints.billing import DocumentInput
    doc_input = DocumentInput(
        customer_id=customer.id,
        kind="invoice",
        day="2026-10-07",
        due_date="2026-11-07",
        notes="Please pay promptly",
        terms="Bank transfer to MBB",
        lines=[
            ItemInput(
                description="Server Setup",
                quantity=Decimal("2"),
                unit_price=Decimal("500.00"),
                discount=Decimal("0"),
                tax_percent=Decimal("6"),
            )
        ]
    )

    doc = await create_document_record(test_db, profile, doc_input)
    await test_db.commit()

    async def override_user():
        return profile.user_id

    async def override_db():
        yield test_db

    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_db] = override_db

    try:
        from httpx import AsyncClient, ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # Test print endpoint
            res_print = await ac.get(f"/api/v1/billing/documents/{doc.id}/print")
            assert res_print.status_code == 200
            assert "text/html" in res_print.headers.get("content-type", "")
            assert "img-src 'self' data: https:" in res_print.headers.get("content-security-policy", "")
            print_body = res_print.text
            assert "Omega Corp" in print_body
            assert "Beta Buyer" in print_body
            assert "data:image/png;base64,omega_logo" in print_body
            assert '<body data-preview>' not in print_body

            # Test preview endpoint
            res_prev = await ac.get(f"/api/v1/billing/documents/{doc.id}/preview")
            assert res_prev.status_code == 200
            assert "text/html" in res_prev.headers.get("content-type", "")
            assert "img-src 'self' data: https:" in res_prev.headers.get("content-security-policy", "")
            prev_body = res_prev.text
            assert "Omega Corp" in prev_body
            assert "data:image/png;base64,omega_logo" in prev_body
            assert '<body data-preview>' in prev_body
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_owner_context_accepts_logo_data_url(test_db):
    from app.api.v1.endpoints.owner import ContextInput
    
    ci = ContextInput(
        company_name="Mega Store",
        logo_data_url="data:image/png;base64,samplelogourl"
    )
    assert ci.logo_data_url == "data:image/png;base64,samplelogourl"
    
    async def override_user():
        return "owner-test-user"

    async def override_db():
        yield test_db

    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_db] = override_db

    try:
        from httpx import AsyncClient, ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.put("/api/v1/owner/context", json={
                "company_name": "Mega Store",
                "logo_data_url": "data:image/png;base64,samplelogourl"
            })
            assert res.status_code == 200
            data = res.json()
            assert data["company_name"] == "Mega Store"
            assert data["logo_data_url"] == "data:image/png;base64,samplelogourl"
    finally:
        app.dependency_overrides.clear()
