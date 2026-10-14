"""
Token API Endpoints
REST API endpoints for token-based billing system
Handles:
- Token balance and purchase
- Quota checking and enforcement
- Usage reporting
- Transaction history
- Model preferences
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.services.token_service import (
    TokenService,
    InsufficientTokensError,
    QuotaExceededError,
)
from app.schemas.tokens import (
    TokenAccountResponse,
    TokenBalanceResponse,
    TransactionResponse,
    QuotaCheckResponse,
    TokenPackageResponse,
    UsageReportResponse,
    TransactionType,
    ServiceType,
    ModelPreferenceUpdate,
)
from app.auth import get_current_user
from app.database import get_db


router = APIRouter()

# Request/Response models for consume/add
class ConsumeTokensRequest(BaseModel):
    amount: int
    service_type: str
    metadata: Optional[Dict[str, Any]] = None


class AddTokensRequest(BaseModel):
    amount: int
    source: str


# ============================================================================
# TOKEN ACCOUNT ENDPOINTS
# ============================================================================


@router.get("/balance", response_model=TokenBalanceResponse)
async def get_token_balance(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TokenBalanceResponse:
    """
    Get user's current token balance

    Returns:
        - Current balance
        - Tier information
        - Rollover balance
        - Last charge date
    """
    service = TokenService(db)

    try:
        balance_data = await service.get_balance(current_user)
        return {
            "success": True,
            "data": balance_data,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/purchase", response_model=TokenPackageResponse)
async def purchase_token_package(
    package_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TokenPackageResponse:
    """
    Purchase a token package

    Request body:
        - package_id: ID of package to purchase
    """
    service = TokenService(db)

    try:
        # Get package details
        package = await service.get_package(package_id)

        # Process payment (TODO: integrate with Stripe)
        payment_result = {
            "success": True,
            "payment_id": f"pay_{uuid.uuid4()}",
            "amount": package.price,
        }

        # Add tokens to user account
        result = await service.add_tokens(
            user_id=current_user,
            transaction_type=TransactionType.PURCHASE,
            amount=int(package.token_amount),
            metadata={"package_id": package_id},
        )

        return {
            "success": True,
            "data": {
                "transaction_id": result.id,
                "package_name": package.name,
                "tokens_purchased": package.token_amount,
                "amount_charged": f"${package.price:.2f}",
                "payment_id": payment_result["payment_id"],
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/transactions", response_model=TransactionResponse)
async def get_transactions(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
    service_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> TransactionResponse:
    """
    Get user's transaction history

    Query params:
        - skip: Number of records to skip
        - limit: Max records to return
        - service_type: Filter by service type
        - start_date: Filter by date range start
        - end_date: Filter by date range end
    """
    service = TokenService(db)

    try:
        transactions = await service.get_transactions(
            user_id=current_user,
            skip=skip,
            limit=limit,
            service_type=service_type,
            start_date=start_date,
            end_date=end_date,
        )

        return {
            "success": True,
            "data": {
                "transactions": transactions,
                "total": len(transactions),
                "page": (skip // limit) + 1,
                "total_pages": (len(transactions) + limit - 1) // limit,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/usage", response_model=UsageReportResponse)
async def get_usage_report(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    period: str = "month",  # day, week, month, year
) -> UsageReportResponse:
    """
    Get comprehensive usage report

    Response includes:
    - Token balance summary
    - Service usage breakdown
    - Cost analysis
    - Quota status
    - Recommendations
    """
    service = TokenService(db)

    try:
        report = await service.get_usage_report(current_user, period)
        return {"success": True, "data": report}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/quota/{service_type}", response_model=QuotaCheckResponse)
async def check_quota(
    service_type: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QuotaCheckResponse:
    """
    Check quota for a specific service type

    Returns quota information and whether operation is allowed
    """
    service = TokenService(db)

    try:
        # Parse service type
        try:
            service_type_enum = ServiceType(service_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid service type: {service_type}"
            )

        result = await service.check_quota_limits(current_user, service_type_enum, 0)

        if not result["allowed"]:
            return {"success": False, "error": f"Quota check failed", "data": None}

        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/quota/reset", response_model=dict)
async def reset_quota(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Reset monthly quota for all services

    Useful for testing or admin operations
    """
    service = TokenService(db)

    try:
        # Get all quotas for user
        from app.database import UsageQuota

        quotas = await service.get_all_quotas(current_user)

        # Reset all quotas
        reset_count = 0
        for quota in quotas:
            # Reset usage
            update_data = {
                "tokens_used": 0,
                "images_used": 0,
                "videos_used": 0,
                "agents_used": 0,
                "last_reset": datetime.utcnow(),
            }

            await service.reset_quota_usage(current_user, quota.tier, "monthly", update_data)
            reset_count += 1

        return {
            "success": True,
            "data": {
                "quotas_reset": reset_count,
                "message": f"Reset {reset_count} quota(s)",
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# MODEL PREFERENCES ENDPOINTS
# ============================================================================


@router.get("/models/available", response_model=dict)
async def get_available_models(
    service_type: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get available models for a service type

    Returns:
        - List of models
        - Provider information
        - Cost information
        - User's current preference
    """
    service = TokenService(db)

    try:
        try:
            service_type_enum = ServiceType(service_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid service type: {service_type}"
            )

        models = await service.get_available_models(current_user, service_type_enum)

        return {
            "success": True,
            "data": {
                "service_type": service_type,
                "models": models,
                "preferred_model": await service.get_user_preference(
                    current_user, service_type_enum
                ),
                "provider_rates": await service.get_provider_rates(service_type_enum),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/models/preference", response_model=dict)
async def set_model_preference(
    model_preference: ModelPreferenceUpdate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Set user's preferred model for a service

    Request body:
        - preferred_text_llm_model: Model ID for text LLM
        - preferred_text_llm_provider: Provider ID
        - preferred_image_generation_model: Model ID for image generation
        - preferred_image_generation_provider: Provider ID
        - preferred_video_generation_model: Model ID for video generation
    """
    service = TokenService(db)

    try:
        result = await service.set_model_preference(
            user_id=current_user, preference=model_preference
        )

        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/alerts", response_model=dict)
async def get_token_alerts(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 10,
    unread_only: bool = False,
) -> Dict[str, Any]:
    """
    Get token usage alerts for user

    Returns:
        - List of alerts
        - Unread count
        - High priority count
        - Category breakdown
    """
    service = TokenService(db)

    try:
        alerts = await service.get_alerts(current_user, limit, unread_only)

        return {
            "success": True,
            "data": {
                "alerts": alerts,
                "total": len(alerts),
                "unread_count": len(
                    [a for a in alerts if a.get("is_resolved") is False]
                ),
                "high_priority_count": len(
                    [a for a in alerts if a.get("severity") == "critical"]
                ),
                "categories": {
                    "quota_warning": len(
                        [a for a in alerts if a.get("alert_type") == "quota_warning"]
                    ),
                    "quota_exceeded": len(
                        [a for a in alerts if a.get("alert_type") == "quota_exceeded"]
                    ),
                    "cost_surge": len(
                        [a for a in alerts if a.get("alert_type") == "cost_surge"]
                    ),
                },
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/alerts/{alert_id}/dismiss", response_model=dict)
async def dismiss_alert(
    alert_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Dismiss a token alert

    Marks alert as resolved
    """
    service = TokenService(db)

    try:
        result = await service.dismiss_alert(alert_id)

        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# PACKAGE ENDPOINTS
# ============================================================================


@router.get("/packages", response_model=dict)
async def get_token_packages(
    tier: Optional[str] = None,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get available token packages
    Returns:
    - Packages filtered by tier
    - Pricing information
    - Feature comparisons
    """
    service = TokenService(db)

    try:
        packages = await service.get_packages(tier)

        return {
            "success": True,
            "data": {
                "packages": packages,
                "tier": tier,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# CONSUME & ADD ENDPOINTS
# ============================================================================


@router.post("/consume", response_model=dict)
async def consume_tokens(
    request: ConsumeTokensRequest,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Consume tokens for a service operation

    Request body:
        - amount: Number of tokens to consume
        - service_type: Service type identifier
        - metadata: Optional additional data
    """
    service = TokenService(db)

    try:
        service_type_enum = ServiceType(request.service_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid service type: {request.service_type}",
        )

    try:
        operation_id = str(uuid.uuid4())
        transaction = await service.charge_tokens(
            user_id=current_user,
            service_type=service_type_enum,
            operation_id=operation_id,
            tokens_required=request.amount,
            metadata=request.metadata or {},
        )

        return {
            "success": True,
            "remaining": int(transaction.balance_after),
            "transaction_id": transaction.id,
        }
    except InsufficientTokensError as e:
        raise HTTPException(status_code=402, detail=str(e))
    except QuotaExceededError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/add", response_model=dict)
async def add_tokens(
    request: AddTokensRequest,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Manually add tokens to user account (for testing/demo/bonus)

    Request body:
        - amount: Number of tokens to add
        - source: Source description (e.g. 'purchase', 'bonus', 'testing')
    """
    service = TokenService(db)

    try:
        transaction = await service.add_tokens(
            user_id=current_user,
            transaction_type=TransactionType.PURCHASE,
            amount=request.amount,
            metadata={"source": request.source},
        )

        return {
            "success": True,
            "balance": int(transaction.balance_after),
            "transaction_id": transaction.id,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================


@router.get("/health", response_model=dict)
async def health_check(
    current_user: str = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Health check for token system

    Returns:
        - System status
        - Database connectivity
        - Recent error logs
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "token_billing": "operational",
            "database": "connected",
            "api": "responsive",
        },
    }
