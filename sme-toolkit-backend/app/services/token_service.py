"""
Token Service - Manages token-based billing system
Handles:
- Token balance management
- Quota enforcement
- Transaction logging
- Cost calculation
- Usage tracking
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from decimal import Decimal, getcontext, ROUND_HALF_UP
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, text
from sqlalchemy.orm import joinedload

from app.database import (
    TokenAccount,
    TokenTransaction,
    UsageQuota,
    ProviderCostRate,
    TokenPackage,
    ModelPreference,
    TokenUsageAlert,
)
from app.schemas.tokens import (
    TransactionType,
    ServiceType,
    Modality,
    ModelPreferenceUpdate,
)

logger = logging.getLogger(__name__)


FIQSTR_TEXT_MODELS = [
    {"model_id": "fiqstr/deepseek-3.2", "model_name": "Deepseek 3.2"},
    {"model_id": "fiqstr/glm-5", "model_name": "Glm 5"},
    {"model_id": "fiqstr/minimax-m2.1", "model_name": "Minimax M2.1"},
    {"model_id": "fiqstr/minimax-m2.5", "model_name": "Minimax M2.5"},
    {"model_id": "fiqstr/qwen3-coder-next", "model_name": "Qwen3 Coder Next"},
]

# Token conversion rates
TOKEN_RATES = {
    "text": {
        "input_chars_per_token": 750,
        "output_chars_per_token": 750,
        "words_per_token": 150,
    },
    "image": {
        "base_image_tokens": 100,  # 1024x1024
        "resolution_multiplier": {
            "512x512": 0.5,
            "1024x1024": 1.0,
            "2048x2048": 2.0,
            "4096x4096": 4.0,
        },
        "quality_multiplier": {
            "standard": 1.0,
            "hd": 2.0,
            "4k": 4.0,
        },
    },
    "video": {
        "base_video_tokens": 500,  # Per 10 seconds
        "duration_multiplier": {
            "5s": 0.5,
            "15s": 1.5,
            "30s": 3.0,
            "60s": 6.0,
        },
        "resolution_multiplier": {
            "480p": 1.0,
            "720p": 1.5,
            "1080p": 2.0,
        },
    },
    "agent": {
        "base_call_tokens": 50,
        "complexity_multiplier": {
            "simple": 1.0,
            "medium": 2.0,
            "complex": 3.0,
        },
        "agent_type_multiplier": {
            "goal_advisor": 1.5,
            "growth_plan": 1.2,
            "costing_advisor": 1.3,
            "business_suggestion": 1.0,
        },
    },
}


class TokenService:
    """Service for managing token-based billing and usage tracking"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_token_account(self, user_id: str) -> Optional[TokenAccount]:
        """
        Retrieve user's token account
        """
        result = await self.db.execute(
            select(TokenAccount).where(TokenAccount.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_token_account(
        self, user_id: str, tier: str = "Free"
    ) -> TokenAccount:
        """
        Create a new token account for user
        """
        account = TokenAccount(
            id=str(uuid.uuid4()),
            user_id=user_id,
            balance=Decimal("0.0000"),
            currency="USD",
            tier=tier,
            status="active",
            rollover_balance=Decimal("0.0000"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        return account

    async def get_balance(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's current token balance
        """
        account = await self.get_token_account(user_id)

        if not account:
            account = await self.create_token_account(user_id)

        return {
            "token_account_id": account.id,
            "user_id": user_id,
            "balance": float(account.balance),
            "currency": account.currency,
            "tier": account.tier,
            "status": account.status,
            "rollover_balance": float(account.rollover_balance),
        }

    async def charge_tokens(
        self,
        user_id: str,
        service_type: ServiceType,
        operation_id: str,
        tokens_required: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TokenTransaction:
        """
        Deduct tokens from user account for an operation
        Raises InsufficientTokensError if insufficient balance
        """
        account = await self.get_token_account(user_id)

        if not account:
            account = await self.create_token_account(user_id)

        if float(account.balance) < tokens_required:
            raise InsufficientTokensError(f"Insufficient tokens: required {tokens_required}, available {account.balance}")

        # Check quota limits before charging
        quota_ok, quota_info = await self._check_quota_limits(
            user_id, service_type, tokens_required
        )

        if not quota_ok:
            # Create quota exceeded alert
            await self._create_quota_alert(user_id, service_type, quota_info)
            raise QuotaExceededError(f"Quota exceeded for {service_type.value}")

        # Calculate total cost
        cost_info = await self._calculate_token_cost(
            user_id, service_type, operation_id, tokens_required
        )

        # Create transaction
        transaction = TokenTransaction(
            id=str(uuid.uuid4()),
            token_account_id=account.id,
            user_id=user_id,
            transaction_type=TransactionType.USAGE,
            amount=-float(tokens_required),
            balance_after=float(account.balance) - tokens_required,
            service_type=service_type.value,
            operation_id=operation_id,
            modality=self._get_modality_for_service(service_type),
            input_tokens=cost_info["input_tokens"],
            output_tokens=cost_info["output_tokens"],
            tokens_consumed=tokens_required,
            estimated_cost_usd=cost_info["estimated_cost"],
            metadata=metadata or {},
            created_at=datetime.utcnow(),
        )

        # Update account balance
        account.balance = float(account.balance) - tokens_required
        account.last_token_charge_at = datetime.utcnow()
        account.updated_at = datetime.utcnow()

        # Update quota
        await self._update_quota_usage(user_id, service_type, tokens_required)

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)

        logger.info(
            f"Charged {tokens_required} tokens from user {user_id} "
            f"for {service_type.value} operation {operation_id}"
        )

        return transaction

    async def add_tokens(
        self,
        user_id: str,
        transaction_type: TransactionType,
        amount: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TokenTransaction:
        """
        Add tokens to user account (purchase, bonus, rollover)
        """
        account = await self.get_token_account(user_id)

        if not account:
            account = await self.create_token_account(user_id)

        # Create transaction
        transaction = TokenTransaction(
            id=str(uuid.uuid4()),
            token_account_id=account.id,
            user_id=user_id,
            transaction_type=transaction_type.value,
            amount=float(amount),
            balance_after=float(account.balance) + amount,
            service_type=None,
            operation_id=None,
            modality=None,
            input_tokens=None,
            output_tokens=None,
            tokens_consumed=None,
            estimated_cost_usd=None,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
        )

        # Update account balance
        account.balance = float(account.balance) + amount
        account.updated_at = datetime.utcnow()

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)

        logger.info(
            f"Added {amount} tokens to user {user_id} via {transaction_type.value}"
        )

        return transaction

    async def _calculate_token_cost(
        self,
        user_id: str,
        service_type: ServiceType,
        operation_id: str,
        tokens_required: int,
    ) -> Dict[str, Any]:
        """
        Calculate token cost based on service type and provider rates
        """
        # Get user's preferred model/provider
        model_pref = await self._get_model_preference(user_id, service_type)
        provider_id = model_pref.get(
            f"preferred_{service_type.value}_provider", "default"
        )
        model_id = model_pref.get(f"preferred_{service_type.value}_model", "default")

        # Get cost rate
        cost_rate = await self._get_provider_rate(provider_id, service_type, model_id)

        if not cost_rate:
            # Use default rates
            cost_rate = await self._get_default_cost_rate(service_type)

        # Calculate cost
        estimated_cost = self._calculate_cost_by_service(
            service_type, tokens_required, cost_rate
        )

        # Calculate token breakdown
        input_tokens = 0
        output_tokens = 0

        if service_type == ServiceType.TEXT_LLM:
            input_tokens = tokens_required // 2  # Assume 50% input, 50% output
            output_tokens = tokens_required - input_tokens

        elif service_type == ServiceType.IMAGE_GENERATION:
            output_tokens = tokens_required  # Image generation cost

        elif service_type == ServiceType.VIDEO_GENERATION:
            output_tokens = tokens_required  # Video generation cost

        elif service_type == ServiceType.AGENT_ORCHESTRATION:
            output_tokens = tokens_required  # Agent orchestration cost

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": estimated_cost,
            "provider_id": provider_id,
            "model_id": model_id,
        }

    def _calculate_cost_by_service(
        self,
        service_type: ServiceType,
        tokens_required: int,
        cost_rate: ProviderCostRate,
    ) -> float:
        """
        Calculate cost based on service type
        """

        if service_type == ServiceType.TEXT_LLM:
            # Text: price per 1K tokens
            tokens = Decimal(str(tokens_required))
            price = (
                Decimal(str(cost_rate.price_per_1k_tokens))
                if cost_rate.price_per_1k_tokens
                else Decimal("0.030")
            )
            cost = (tokens * price) / Decimal("1000")

        elif service_type == ServiceType.IMAGE_GENERATION:
            # Image: flat rate per image
            cost = (
                Decimal(str(cost_rate.price_per_image))
                if cost_rate.price_per_image
                else Decimal("0.025")
            )

        elif service_type == ServiceType.VIDEO_GENERATION:
            # Video: price per second
            tokens = Decimal(str(tokens_required))
            price = (
                Decimal(str(cost_rate.price_per_video_second))
                if cost_rate.price_per_video_second
                else Decimal("0.100")
            )
            cost = tokens * price

        elif service_type == ServiceType.AGENT_ORCHESTRATION:
            # Agent: flat rate per call
            tokens = Decimal(str(tokens_required))
            price = (
                Decimal(str(cost_rate.price_per_agent_call))
                if cost_rate.price_per_agent_call
                else Decimal("0.050")
            )
            cost = tokens * price

        else:
            cost = Decimal("0")

        # Quantize and convert to float
        if isinstance(cost, Decimal):
            cost = cost.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            return float(cost)
        else:
            return cost

    async def _get_default_cost_rate(
        self, service_type: ServiceType
    ) -> ProviderCostRate:
        """
        Get default cost rate for a service
        """
        # This would be loaded from configuration or default values
        # For now, return a dummy rate
        return ProviderCostRate(
            id="default",
            provider_id="default",
            provider_name="Default",
            service_type=service_type.value,
            model_id="default",
            price_per_1k_tokens=Decimal("0.030"),
            price_per_image=Decimal("0.050"),
            price_per_video_second=Decimal("0.100"),
            price_per_agent_call=Decimal("0.050"),
            currency="USD",
            is_negotiated=False,
            volume_discount_percent=Decimal("0.00"),
        )

    async def _get_model_preference(
        self,
        user_id: str,
        service_type: ServiceType,
    ) -> Dict[str, str]:
        """
        Get user's preferred model/provider for a service
        """
        account = await self.get_token_account(user_id)

        if not account:
            return {"preferred_provider": "default", "preferred_model": "default"}

        # Load model preferences
        pref = await self.db.execute(
            select(ModelPreference).where(
                ModelPreference.token_account_id == account.id
            )
        )
        pref_result = pref.scalar_one_or_none()

        if not pref_result:
            return {"preferred_provider": "default", "preferred_model": "default"}

        # Return preference as dict
        return {
            "preferred_provider": getattr(
                pref_result, f"preferred_{service_type.value}_provider", "default"
            )
            or "default",
            "preferred_model": getattr(
                pref_result, f"preferred_{service_type.value}_model", "default"
            )
            or "default",
        }

    async def _get_provider_rate(
        self,
        provider_id: str,
        service_type: ServiceType,
        model_id: str = "default",
    ) -> Optional[ProviderCostRate]:
        """
        Get cost rate for provider/service
        """
        result = await self.db.execute(
            select(ProviderCostRate).where(
                ProviderCostRate.provider_id == provider_id,
                ProviderCostRate.service_type == service_type.value,
                (ProviderCostRate.model_id == model_id)
                | (ProviderCostRate.model_id.is_(None)),
            )
        )
        return result.scalar_one_or_none()

    async def _get_modality_for_service(self, service_type: ServiceType) -> str:
        """Determine modality for a service type"""
        if service_type == ServiceType.TEXT_LLM:
            return "text"
        elif service_type == ServiceType.IMAGE_GENERATION:
            return "image"
        elif service_type == ServiceType.VIDEO_GENERATION:
            return "video"
        elif service_type == ServiceType.AGENT_ORCHESTRATION:
            return "multi_modal"
        else:
            return "text"  # Default

    async def _check_quota_limits(
        self,
        user_id: str,
        service_type: ServiceType,
        tokens_required: int,
    ) -> Tuple[bool, Optional[UsageQuota]]:
        """
        Check if operation is within user's quota limits
        """
        account = await self.get_token_account(user_id)

        if not account:
            return False, None

        # Get monthly quota for user's tier
        result = await self.db.execute(
            select(UsageQuota).where(
                UsageQuota.token_account_id == account.id,
                UsageQuota.tier == account.tier,
                UsageQuota.period_type == "monthly",
            )
        )
        quota = result.scalar_one_or_none()

        if not quota:
            # No quota set up, use default limits
            if account.tier == "Free":
                return False, None
            else:
                # Higher tiers can use more
                return True, None

        # Check specific limits
        max_allowed = 0
        used = 0

        if service_type == ServiceType.TEXT_LLM:
            max_allowed = quota.max_tokens or 0
            used = quota.tokens_used + tokens_required

        elif service_type == ServiceType.IMAGE_GENERATION:
            max_allowed = quota.max_images or 0
            used = quota.images_used + 1  # One image

        elif service_type == ServiceType.VIDEO_GENERATION:
            max_allowed = quota.max_videos or 0
            used = quota.videos_used + 1  # One video

        elif service_type == ServiceType.AGENT_ORCHESTRATION:
            max_allowed = quota.max_agents or 0
            used = quota.agents_used + 1  # One agent call

        else:
            return True, None

        # Check if within limits
        if used > max_allowed:
            return False, quota

        return True, quota

    async def _update_quota_usage(
        self,
        user_id: str,
        service_type: ServiceType,
        tokens_used: int,
    ) -> None:
        """Update quota usage after successful operation"""
        account = await self.get_token_account(user_id)

        if not account:
            return

        # Get monthly quota
        result = await self.db.execute(
            select(UsageQuota).where(
                UsageQuota.token_account_id == account.id,
                UsageQuota.tier == account.tier,
                UsageQuota.period_type == "monthly",
            )
        )
        quota = result.scalar_one_or_none()

        if not quota:
            return

        # Update usage
        update_data = {}

        if service_type == ServiceType.TEXT_LLM:
            update_data["tokens_used"] = quota.tokens_used + tokens_used

        elif service_type == ServiceType.IMAGE_GENERATION:
            update_data["images_used"] = quota.images_used + 1

        elif service_type == ServiceType.VIDEO_GENERATION:
            update_data["videos_used"] = quota.videos_used + 1

        elif service_type == ServiceType.AGENT_ORCHESTRATION:
            update_data["agents_used"] = quota.agents_used + 1

        update_data["updated_at"] = datetime.utcnow()

        await self.db.execute(
            update(UsageQuota).where(UsageQuota.id == quota.id).values(**update_data)
        )

    async def _create_quota_alert(
        self,
        user_id: str,
        service_type: ServiceType,
        quota: Optional[UsageQuota],
    ) -> None:
        """Create alert when quota is exceeded"""
        account = await self.get_token_account(user_id)

        if not account or not quota:
            return

        # Determine severity based on how much quota is exceeded
        percentage_used = 0.0
        if quota.max_tokens:
            percentage_used = float(quota.tokens_used / quota.max_tokens) * 100
        elif quota.max_images:
            percentage_used = float((quota.images_used + 1) / quota.max_images) * 100

        severity = "warning"
        if percentage_used >= 150:
            severity = "critical"
        elif percentage_used >= 120:
            severity = "critical"
        elif percentage_used >= 100:
            severity = "emergency"

        # Import TokenUsageAlert here (circular import avoidance)
        from app.database import TokenUsageAlert

        alert = TokenUsageAlert(
            id=str(uuid.uuid4()),
            token_account_id=account.id,
            alert_type="quota_exceeded",
            severity=severity,
            service_type=service_type.value,
            message=f"Monthly quota exceeded for {service_type.value}",
            current_tokens_remaining=quota.tokens_used,
            percentage_used=float(percentage_used),
            estimated_time_remaining=30,
            is_resolved=False,
            metadata={
                "quota_id": quota.id,
                "service_type": service_type.value,
                "tier": account.tier,
            },
            created_at=datetime.utcnow(),
        )

        self.db.add(alert)
        await self.db.commit()

    async def get_quota_status(
        self,
        user_id: str,
        service_type: ServiceType,
    ) -> Dict[str, Any]:
        """
        Get quota status for user and service
        """
        account = await self.get_token_account(user_id)

        if not account:
            return {"allowed": False, "error": "Account not found"}

        # Get monthly quota
        result = await self.db.execute(
            select(UsageQuota).where(
                UsageQuota.token_account_id == account.id,
                UsageQuota.tier == account.tier,
                UsageQuota.period_type == "monthly",
            )
        )
        quota = result.scalar_one_or_none()

        if not quota:
            return {"allowed": True, "quota_exceeded": False}

        # Calculate remaining
        remaining = 0
        percentage_used = 0.0

        if service_type == ServiceType.TEXT_LLM and quota.max_tokens:
            remaining = quota.max_tokens - quota.tokens_used
            percentage_used = float(quota.tokens_used / quota.max_tokens) * 100

        elif service_type == ServiceType.IMAGE_GENERATION and quota.max_images:
            remaining = quota.max_images - quota.images_used
            percentage_used = float(quota.images_used / quota.max_images) * 100

        elif service_type == ServiceType.VIDEO_GENERATION and quota.max_videos:
            remaining = quota.max_videos - quota.videos_used
            percentage_used = float(quota.videos_used / quota.max_videos) * 100

        return {
            "allowed": True,
            "quota_exceeded": False,
            "tokens_remaining": remaining,
            "images_remaining": remaining,
            "videos_remaining": remaining,
            "percentage_used": percentage_used,
            "tier": account.tier,
            "quota_reset_date": quota.last_reset,
        }

    # ========================================================================
    # PUBLIC API METHODS
    # ========================================================================

    async def get_transactions(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        service_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get user's transaction history
        """
        account = await self.get_token_account(user_id)

        if not account:
            raise ValueError(f"Token account not found for user {user_id}")

        # Build query
        query = select(TokenTransaction).where(
            TokenTransaction.token_account_id == account.id
        )

        if service_type:
            query = query.where(TokenTransaction.service_type == service_type)

        if start_date:
            query = query.where(
                TokenTransaction.created_at >= datetime.fromisoformat(start_date)
            )

        if end_date:
            query = query.where(
                TokenTransaction.created_at <= datetime.fromisoformat(end_date)
            )

        query = query.order_by(TokenTransaction.created_at.desc())

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        transactions = result.scalars().all()

        # Convert to dicts
        return [
            {
                "id": t.id,
                "token_account_id": t.token_account_id,
                "user_id": t.user_id,
                "transaction_type": t.transaction_type,
                "amount": t.amount,
                "balance_after": t.balance_after,
                "service_type": t.service_type,
                "model_id": t.model_id,
                "provider_id": t.provider_id,
                "modality": t.modality,
                "operation_id": t.operation_id,
                "operation_type": t.operation_type,
                "input_tokens": t.input_tokens,
                "output_tokens": t.output_tokens,
                "tokens_consumed": t.tokens_consumed,
                "estimated_cost_usd": t.estimated_cost_usd,
                "metadata": t.metadata,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in transactions
        ]

    async def get_usage_report(
        self,
        user_id: str,
        period: str = "month",
    ) -> Dict[str, Any]:
        """
        Get comprehensive usage report
        """
        account = await self.get_token_account(user_id)

        if not account:
            raise ValueError(f"Token account not found for user {user_id}")

        # Calculate date range
        now = datetime.utcnow()
        if period == "day":
            start_date = now - timedelta(days=1)
        elif period == "week":
            start_date = now - timedelta(weeks=1)
        elif period == "year":
            start_date = now - timedelta(days=365)
        else:  # month (default)
            start_date = now - timedelta(days=30)

        # Get transactions in period
        result = await self.db.execute(
            select(TokenTransaction).where(
                TokenTransaction.token_account_id == account.id,
                TokenTransaction.created_at >= start_date,
                TokenTransaction.transaction_type == TransactionType.USAGE,
            )
        )
        transactions = result.scalars().all()

        # Calculate usage by service type
        usage_by_service = {}
        total_tokens = 0
        total_cost = 0.0

        for t in transactions:
            service = t.service_type or "unknown"
            if service not in usage_by_service:
                usage_by_service[service] = {
                    "tokens": 0,
                    "cost": 0.0,
                    "count": 0,
                }

            tokens = abs(t.tokens_consumed or 0)
            cost = abs(t.estimated_cost_usd or 0.0)

            usage_by_service[service]["tokens"] += tokens
            usage_by_service[service]["cost"] += cost
            usage_by_service[service]["count"] += 1

            total_tokens += tokens
            total_cost += cost

        # Get quota status
        quota_result = await self.db.execute(
            select(UsageQuota).where(
                UsageQuota.token_account_id == account.id,
                UsageQuota.period_type == "monthly",
            )
        )
        quotas = quota_result.scalars().all()

        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": now.isoformat(),
            "balance": {
                "tokens": float(account.balance),
                "currency": account.currency,
                "tier": account.tier,
            },
            "usage_by_service": usage_by_service,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "quotas": [
                {
                    "tier": q.tier,
                    "period_type": q.period_type,
                    "max_tokens": q.max_tokens,
                    "tokens_used": q.tokens_used,
                    "tokens_remaining": (q.max_tokens or 0) - q.tokens_used,
                }
                for q in quotas
            ],
            "recommendations": self._generate_usage_recommendations(
                account, usage_by_service, quotas
            ),
        }

    def _generate_usage_recommendations(
        self,
        account: TokenAccount,
        usage_by_service: Dict[str, Any],
        quotas: Any,
    ) -> List[str]:
        """Generate usage recommendations based on patterns"""
        recommendations = []

        # Check for high usage
        for service, data in usage_by_service.items():
            if data["tokens"] > 10000:
                recommendations.append(
                    f"High {service} usage detected. Consider upgrading to higher tier."
                )

        # Check quota limits
        for quota in quotas:
            if quota.max_tokens:
                percentage = (quota.tokens_used / quota.max_tokens) * 100
                if percentage > 80:
                    recommendations.append(
                        f"You've used {percentage:.1f}% of your monthly {quota.tier} quota."
                    )

        if not recommendations:
            recommendations.append("Your usage is within normal limits.")

        return recommendations

    async def check_quota_limits(
        self,
        user_id: str,
        service_type: ServiceType,
        tokens_required: int,
    ) -> Dict[str, Any]:
        """
        Check if operation is within user's quota limits (public API)
        """
        allowed, quota = await self._check_quota_limits(
            user_id, service_type, tokens_required
        )

        result = {
            "allowed": allowed,
            "service_type": service_type.value,
            "tokens_required": tokens_required,
        }

        if not allowed:
            result["error"] = "Quota limit exceeded"
            if quota:
                result["quota_id"] = quota.id
                result["tier"] = quota.tier

        return result

    async def get_all_quotas(self, user_id: str) -> Any:
        """Get all quotas for user"""
        account = await self.get_token_account(user_id)

        if not account:
            return []

        result = await self.db.execute(
            select(UsageQuota).where(UsageQuota.token_account_id == account.id)
        )
        return result.scalars().all()

    async def reset_quota_usage(
        self,
        user_id: str,
        tier: str,
        period_type: str,
        update_data: Dict[str, Any],
    ) -> None:
        """Reset quota usage"""
        account = await self.get_token_account(user_id)

        if not account:
            return

        await self.db.execute(
            update(UsageQuota)
            .where(
                UsageQuota.token_account_id == account.id,
                UsageQuota.tier == tier,
                UsageQuota.period_type == period_type,
            )
            .values(**update_data)
        )

    async def get_available_models(
        self,
        user_id: str,
        service_type: ServiceType,
    ) -> List[Dict[str, Any]]:
        """Get available models for a service type"""
        account = await self.get_token_account(user_id)

        # Get all provider rates for service type
        result = await self.db.execute(
            select(ProviderCostRate).where(
                ProviderCostRate.service_type == service_type.value
            )
        )
        rates = result.scalars().all()

        # Convert to model info
        models = []
        for rate in rates:
            models.append(
                {
                    "provider_id": rate.provider_id,
                    "provider_name": rate.provider_name,
                    "model_id": rate.model_id,
                    "model_name": rate.model_id or "default",
                    "service_type": rate.service_type,
                    "price_info": {
                        "price_per_1k_tokens": rate.price_per_1k_tokens,
                        "price_per_image": rate.price_per_image,
                        "price_per_video_second": rate.price_per_video_second,
                        "price_per_agent_call": rate.price_per_agent_call,
                    },
                    "features": [],
                    "is_available": True,
                }
            )

        if service_type == ServiceType.TEXT_LLM:
            existing_model_ids = {model["model_id"] for model in models}
            for fiqstr_model in FIQSTR_TEXT_MODELS:
                if fiqstr_model["model_id"] in existing_model_ids:
                    continue

                models.append(
                    {
                        "provider_id": "fiqstr-v2",
                        "provider_name": "Fiqstr V2",
                        "model_id": fiqstr_model["model_id"],
                        "model_name": fiqstr_model["model_name"],
                        "service_type": service_type.value,
                        "price_info": {
                            "price_per_1k_tokens": 0.0,
                            "price_per_image": None,
                            "price_per_video_second": None,
                            "price_per_agent_call": None,
                        },
                        "features": ["chat", "completion", "code", "reasoning"],
                        "is_available": True,
                    }
                )

        return models

    async def get_user_preference(
        self,
        user_id: str,
        service_type: ServiceType,
    ) -> Dict[str, str]:
        """Get user's model preference for a service"""
        account = await self.get_token_account(user_id)

        if not account:
            return {"preferred_model": "default", "preferred_provider": "default"}

        result = await self.db.execute(
            select(ModelPreference).where(
                ModelPreference.token_account_id == account.id
            )
        )
        pref = result.scalar_one_or_none()

        if not pref:
            return {"preferred_model": "default", "preferred_provider": "default"}

        # Map preference to service type
        if service_type == ServiceType.TEXT_LLM:
            return {
                "preferred_model": pref.preferred_text_llm_model or "default",
                "preferred_provider": pref.preferred_text_llm_provider or "default",
            }
        elif service_type == ServiceType.IMAGE_GENERATION:
            return {
                "preferred_model": pref.preferred_image_generation_model or "default",
                "preferred_provider": pref.preferred_image_generation_provider
                or "default",
            }
        elif service_type == ServiceType.VIDEO_GENERATION:
            return {
                "preferred_model": pref.preferred_video_generation_model or "default",
                "preferred_provider": pref.preferred_video_generation_provider
                or "default",
            }
        else:
            return {"preferred_model": "default", "preferred_provider": "default"}

    async def get_provider_rates(
        self,
        service_type: ServiceType,
    ) -> List[Dict[str, Any]]:
        """Get all provider rates for a service type"""
        result = await self.db.execute(
            select(ProviderCostRate).where(
                ProviderCostRate.service_type == service_type.value
            )
        )
        rates = result.scalars().all()

        return [
            {
                "provider_id": r.provider_id,
                "provider_name": r.provider_name,
                "model_id": r.model_id,
                "price_per_1k_tokens": r.price_per_1k_tokens,
                "price_per_image": r.price_per_image,
                "price_per_video_second": r.price_per_video_second,
                "price_per_agent_call": r.price_per_agent_call,
                "currency": r.currency,
            }
            for r in rates
        ] + (
            [
                {
                    "provider_id": "fiqstr-v2",
                    "provider_name": "Fiqstr V2",
                    "model_id": model["model_id"],
                    "price_per_1k_tokens": 0.0,
                    "price_per_image": None,
                    "price_per_video_second": None,
                    "price_per_agent_call": None,
                    "currency": "USD",
                    "is_negotiated": False,
                    "volume_discount_percent": 0.0,
                    "success_rate": 99.5,
                }
                for model in FIQSTR_TEXT_MODELS
            ]
            if service_type == ServiceType.TEXT_LLM
            else []
        )

    async def set_model_preference(
        self,
        user_id: str,
        preference: ModelPreferenceUpdate,
    ) -> Dict[str, Any]:
        """Set user's model preference"""
        account = await self.get_token_account(user_id)

        if not account:
            raise ValueError(f"Token account not found for user {user_id}")

        # Get or create preference
        result = await self.db.execute(
            select(ModelPreference).where(
                ModelPreference.token_account_id == account.id
            )
        )
        pref = result.scalar_one_or_none()

        if not pref:
            pref = ModelPreference(
                id=str(uuid.uuid4()),
                token_account_id=account.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self.db.add(pref)

        # Update fields
        if preference.preferred_text_llm_model is not None:
            pref.preferred_text_llm_model = preference.preferred_text_llm_model
        if preference.preferred_text_llm_provider is not None:
            pref.preferred_text_llm_provider = preference.preferred_text_llm_provider
        if preference.preferred_image_generation_model is not None:
            pref.preferred_image_generation_model = (
                preference.preferred_image_generation_model
            )
        if preference.preferred_image_generation_provider is not None:
            pref.preferred_image_generation_provider = (
                preference.preferred_image_generation_provider
            )
        if preference.preferred_video_generation_model is not None:
            pref.preferred_video_generation_model = (
                preference.preferred_video_generation_model
            )
        if preference.preferred_video_generation_provider is not None:
            pref.preferred_video_generation_provider = (
                preference.preferred_video_generation_provider
            )
        if preference.preferred_agent_orchestration_provider is not None:
            pref.preferred_agent_orchestration_provider = (
                preference.preferred_agent_orchestration_provider
            )

        if preference.smart_selection_enabled is not None:
            pref.smart_selection_enabled = preference.smart_selection_enabled
        if preference.auto_select_cheapest is not None:
            pref.auto_select_cheapest = preference.auto_select_cheapest
        if preference.max_cost_per_operation is not None:
            pref.max_cost_per_operation = preference.max_cost_per_operation

        pref.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(pref)

        logger.info(f"Updated model preference for user {user_id}")

        return {
            "token_account_id": pref.token_account_id,
            "preferences": {
                "text_llm": {
                    "model": pref.preferred_text_llm_model,
                    "provider": pref.preferred_text_llm_provider,
                },
                "image_generation": {
                    "model": pref.preferred_image_generation_model,
                    "provider": pref.preferred_image_generation_provider,
                },
                "video_generation": {
                    "model": pref.preferred_video_generation_model,
                    "provider": pref.preferred_video_generation_provider,
                },
            },
            "settings": {
                "smart_selection_enabled": pref.smart_selection_enabled,
                "auto_select_cheapest": pref.auto_select_cheapest,
                "max_cost_per_operation": pref.max_cost_per_operation,
            },
        }

    async def get_alerts(
        self,
        user_id: str,
        limit: int = 10,
        unread_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get token usage alerts for user"""
        account = await self.get_token_account(user_id)

        if not account:
            return []

        # Build query
        query = select(TokenUsageAlert).where(
            TokenUsageAlert.token_account_id == account.id
        )

        if unread_only:
            query = query.where(TokenUsageAlert.is_resolved == False)

        query = query.order_by(TokenUsageAlert.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        alerts = result.scalars().all()

        return [
            {
                "id": a.id,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "service_type": a.service_type,
                "message": a.message,
                "current_tokens_remaining": a.current_tokens_remaining,
                "percentage_used": a.percentage_used,
                "is_resolved": a.is_resolved,
                "created_at": a.created_at.isoformat(),
            }
            for a in alerts
        ]

    async def dismiss_alert(
        self,
        alert_id: str,
    ) -> Dict[str, Any]:
        """Dismiss a token alert"""
        result = await self.db.execute(
            select(TokenUsageAlert).where(TokenUsageAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()

        if not alert:
            raise ValueError(f"Alert {alert_id} not found")

        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()

        await self.db.commit()

        logger.info(f"Dismissed alert {alert_id}")

        resolved_at_value = alert.resolved_at
        if resolved_at_value is not None:
            resolved_at_iso = resolved_at_value.isoformat()
        else:
            resolved_at_iso = None

        return {
            "alert_id": alert.id,
            "resolved": True,
            "resolved_at": resolved_at_iso,
        }

    async def get_packages(
        self,
        tier: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get available token packages"""
        query = select(TokenPackage).where(TokenPackage.is_active == True)

        if tier:
            query = query.where(TokenPackage.tier == tier)

        query = query.order_by(TokenPackage.price.asc())

        result = await self.db.execute(query)
        packages = result.scalars().all()

        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "token_amount": p.token_amount,
                "currency": p.currency,
                "tier": p.tier,
                "bonus_tokens": p.bonus_tokens,
                "features": p.features or {},
            }
            for p in packages
        ]

    async def get_package(
        self,
        package_id: str,
    ) -> TokenPackage:
        """Get a specific token package"""
        result = await self.db.execute(
            select(TokenPackage).where(
                TokenPackage.id == package_id, TokenPackage.is_active == True
            )
        )
        package = result.scalar_one_or_none()

        if not package:
            raise ValueError(f"Package {package_id} not found")

        return package


class InsufficientTokensError(Exception):
    """Raised when user has insufficient tokens for an operation"""

    pass


class QuotaExceededError(Exception):
    """Raised when user has exceeded their quota limits"""

    pass
