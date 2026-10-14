"""
SEO FastAPI Router for SME OS V2.
Generates Meta Tags, JSON-LD Schema.org, and On-Page SEO Audits.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from app.services.seo_service import SEOService

router = APIRouter()
seo_service = SEOService()


class MetaSchemaRequest(BaseModel):
    business_name: str = Field(..., description="Business or store name")
    industry: str = Field(..., description="Industry sector")
    keywords: List[str] = Field(..., description="Target keywords list")
    city_location: Optional[str] = Field("Kuala Lumpur, Malaysia")
    website_url: Optional[str] = Field("https://example.com.my")


class PageAuditRequest(BaseModel):
    page_title: str = Field(...)
    content_body: str = Field(...)
    target_keyword: str = Field(...)


@router.post("/generate-meta-schema", summary="Generate Title, Meta Description & JSON-LD Schema.org")
async def generate_meta_schema(req: MetaSchemaRequest):
    """Generates localized Title Tags, Meta Descriptions, and JSON-LD LocalBusiness Schema"""
    return seo_service.generate_meta_and_schema(
        business_name=req.business_name,
        industry=req.industry,
        keywords=req.keywords,
        city_location=req.city_location or "Kuala Lumpur, Malaysia",
        website_url=req.website_url or "https://example.com.my"
    )


@router.post("/audit-page", summary="Perform On-Page SEO Audit")
async def audit_page(req: PageAuditRequest):
    """Performs on-page SEO keyword density and structure audit"""
    return seo_service.audit_page_seo(
        page_title=req.page_title,
        content_body=req.content_body,
        target_keyword=req.target_keyword
    )
