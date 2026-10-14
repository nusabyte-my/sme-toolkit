"""
Database models and session management
"""

import os
from typing import Optional, Generator
from datetime import datetime, timedelta
import uuid

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    JSON,
    Integer,
    BigInteger,
    Float,
    LargeBinary,
    Boolean,
    ForeignKey,
    Enum as SQLEnum,
    Index,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column

from app.config import settings

# ============================================================================
# ASYNC SESSION SETUP
# ============================================================================

# Allow DATABASE_URL override via env (Docker uses postgres, dev uses sqlite)
DATABASE_URL = settings.database_url

if os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL", "")

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
    hide_parameters=True,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async_session = AsyncSession


async def get_db() -> AsyncSession:
    """Dependency to get async database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables (for development)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ============================================================================
# BASE CLASS
# ============================================================================


class Base(DeclarativeBase):
    """Base class for all database models"""

    pass


# ============================================================================
# ENUMS
# ============================================================================


class JobStatus(str):
    """Job execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GoalPriority(str):
    """Goal priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class GoalStatus(str):
    """Goal status"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SuggestionStatus(str):
    """Suggestion status"""

    NEW = "new"
    REVIEWED = "reviewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUGGESTED = "suggested"


class ScoreType(str):
    """Score types for business analytics"""

    BUSINESS_HEALTH = "business_health"
    GROWTH_POTENTIAL = "growth_potential"
    FINANCIAL_STABILITY = "financial_stability"
    MARKET_POSITION = "market_position"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    INNOVATION_READINESS = "innovation_readiness"


class ConversationPhase(str):
    """BMC conversation phases"""

    INTRO = "intro"
    VALUE_PROPOSITION = "value_proposition"
    CUSTOMER_SEGMENTS = "customer_segments"
    CHANNELS = "channels"
    CUSTOMER_RELATIONSHIPS = "customer_relationships"
    REVENUE_STREAMS = "revenue_streams"
    KEY_RESOURCES = "key_resources"
    KEY_ACTIVITIES = "key_activities"
    KEY_PARTNERSHIPS = "key_partnerships"
    COST_STRUCTURE = "cost_structure"
    COMPLETE = "complete"


class TransactionType(str):
    """Types of token transactions"""

    PURCHASE = "purchase"
    USAGE = "usage"
    REFUND = "refund"
    BONUS = "bonus"
    ROLLOVER = "rollover"
    ADJUSTMENT = "adjustment"


class ServiceType(str):
    """Types of AI services"""

    TEXT_LLM = "text_llm"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    AGENT_ORCHESTRATION = "agent_orchestration"
    ANALYSIS = "analysis"
    TRANSCRIPTION = "transcription"


class Modality(str):
    """Content modalities"""

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    MULTI_MODAL = "multi_modal"


# ============================================================================
# USER MODELS
# ============================================================================


class UserSubscription(Base):
    """User subscription information"""

    __tablename__ = "user_subscriptions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )

    tier: Mapped[str] = mapped_column(
        String, nullable=False, default="free"
    )

    # Stripe Integration
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String, index=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)

    # Subscription Period
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Custom Features Override
    features: Mapped[Optional[dict]] = mapped_column(JSON, default={})

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class UserProfile(Base):
    """User profile information"""

    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )

    # Personal Info
    first_name: Mapped[Optional[str]] = mapped_column(String)
    last_name: Mapped[Optional[str]] = mapped_column(String)
    display_name: Mapped[Optional[str]] = mapped_column(String)
    avatar_url: Mapped[Optional[str]] = mapped_column(String)

    # Contact Info
    email: Mapped[Optional[str]] = mapped_column(String, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String)

    # Bio & Preferences
    bio: Mapped[Optional[str]] = mapped_column(Text)
    timezone: Mapped[Optional[str]] = mapped_column(String)
    language: Mapped[Optional[str]] = mapped_column(String, default="en")

    # Metadata
    meta_json: Mapped[Optional[dict]] = mapped_column(JSON, default={})

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    social_media_profiles = relationship(
        "SocialMediaProfile", cascade="all, delete-orphan"
    )
    activity_logs = relationship(
        "UserActivityLog", cascade="all, delete-orphan"
    )
    privacy_settings = relationship(
        "PrivacySetting", cascade="all, delete-orphan"
    )
    profile_insights = relationship(
        "ProfileInsight", cascade="all, delete-orphan"
    )


class SocialMediaProfile(Base):
    """Social media profile links for users"""

    __tablename__ = "social_media_profiles"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("user_profiles.user_id"), nullable=False, index=True
    )

    platform: Mapped[str] = mapped_column(String, nullable=False, index=True)
    profile_url: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String)
    follower_count: Mapped[Optional[int]] = mapped_column(Integer)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)

    meta_json: Mapped[Optional[dict]] = mapped_column(JSON, default={})

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class UserActivityLog(Base):
    """User activity tracking"""

    __tablename__ = "user_activity_logs"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("user_profiles.user_id"), nullable=False, index=True
    )

    action: Mapped[str] = mapped_column(String, nullable=False, index=True)
    resource_type: Mapped[Optional[str]] = mapped_column(String, index=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String, index=True)

    ip_address: Mapped[Optional[str]] = mapped_column(String)
    user_agent: Mapped[Optional[str]] = mapped_column(String)
    activity_metadata: Mapped[Optional[dict]] = mapped_column(JSON, default={})

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_activity_user_action", "user_id", "action"),
        Index("idx_activity_resource", "resource_type", "resource_id"),
    )


class PrivacySetting(Base):
    """User privacy settings"""

    __tablename__ = "privacy_settings"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("user_profiles.user_id"), unique=True, nullable=False, index=True
    )

    profile_visibility: Mapped[str] = mapped_column(String, default="public")
    show_email: Mapped[bool] = mapped_column(Boolean, default=False)
    show_phone: Mapped[bool] = mapped_column(Boolean, default=False)
    show_social_media: Mapped[bool] = mapped_column(Boolean, default=False)

    allow_search: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_messages: Mapped[bool] = mapped_column(Boolean, default=True)

    meta_json: Mapped[Optional[dict]] = mapped_column(JSON, default={})

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class ProfileInsight(Base):
    """User profile insights and analytics"""

    __tablename__ = "profile_insights"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("user_profiles.user_id"), nullable=False, index=True
    )

    insight_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    insight_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_insight_user_type", "user_id", "insight_type"),
    )


# ============================================================================
# BUSINESS MODELS
# ============================================================================


class BusinessProfile(Base):
    """User's business profile"""

    __tablename__ = "business_profiles"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )

    # Business Info
    company_name: Mapped[str] = mapped_column(String, nullable=False)
    industry: Mapped[Optional[str]] = mapped_column(String)
    company_size: Mapped[Optional[str]] = mapped_column(String)
    website: Mapped[Optional[str]] = mapped_column(String)

    # Contact Info
    contact_email: Mapped[Optional[str]] = mapped_column(String)
    contact_phone: Mapped[Optional[str]] = mapped_column(String)

    # Location
    country: Mapped[Optional[str]] = mapped_column(String)
    city: Mapped[Optional[str]] = mapped_column(String)

    # Metadata
    meta_json: Mapped[Optional[dict]] = mapped_column(JSON, default={})

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @property
    def progress(self) -> float:
        return self.progress_percentage or 0.0

    # Relationships
    leads = relationship(
        "Lead", back_populates="business_profile", cascade="all, delete-orphan"
    )
    goals = relationship(
        "Goal", back_populates="business_profile", cascade="all, delete-orphan"
    )
    growth_scores = relationship(
        "GrowthScoreRecord", cascade="all, delete-orphan"
    )
    growth_plans = relationship(
        "GrowthPlan", cascade="all, delete-orphan"
    )
    costing_analyses = relationship(
        "CostingAnalysis", cascade="all, delete-orphan"
    )
    sales_transactions = relationship(
        "SalesTransaction", cascade="all, delete-orphan"
    )
    marketplace_credentials = relationship(
        "MarketplaceCredential", cascade="all, delete-orphan"
    )


class Lead(Base):
    """Lead/Customer information"""

    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    business_profile_id: Mapped[str] = mapped_column(
        String, ForeignKey("business_profiles.id"), nullable=False
    )

    # Lead Info
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String)
    company: Mapped[Optional[str]] = mapped_column(String)
    position: Mapped[Optional[str]] = mapped_column(String)

    # Lead Status
    status: Mapped[str] = mapped_column(
        String, default="new", index=True
    )  # new, contacted, qualified, proposal, won, lost
    lead_source: Mapped[Optional[str]] = mapped_column(String, index=True)  # website, referral, social_media, etc.
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # CRM Fields
    assigned_agent_id: Mapped[Optional[str]] = mapped_column(String, index=True)
    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    next_follow_up_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)

    # Lead Scoring
    score: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    score_factors: Mapped[Optional[dict]] = mapped_column(JSON)
    score_history: Mapped[Optional[list]] = mapped_column(JSON, default=[])

    # Tags and Custom Fields
    tags: Mapped[Optional[list]] = mapped_column(JSON, default=[])
    custom_fields: Mapped[Optional[dict]] = mapped_column(JSON, default={})

    # Metadata
    meta_json: Mapped[Optional[dict]] = mapped_column(JSON, default={})

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="leads")
    interactions = relationship(
        "LeadInteraction", back_populates="lead", cascade="all, delete-orphan"
    )
    sales_tasks = relationship(
        "SalesTask", back_populates="lead", cascade="all, delete-orphan"
    )


class LeadInteraction(Base):
    """Interactions with leads"""

    __tablename__ = "lead_interactions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    lead_id: Mapped[str] = mapped_column(String, ForeignKey("leads.id"), nullable=False)

    interaction_type: Mapped[str] = mapped_column(
        String, nullable=False
    )  # email, call, meeting, note
    notes: Mapped[Optional[str]] = mapped_column(Text)
    outcome: Mapped[Optional[str]] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    lead = relationship("Lead", back_populates="interactions")


class SalesTask(Base):
    """Sales tasks for lead follow-up"""

    __tablename__ = "sales_tasks"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    lead_id: Mapped[str] = mapped_column(
        String, ForeignKey("leads.id"), nullable=False, index=True
    )
    business_profile_id: Mapped[str] = mapped_column(
        String, ForeignKey("business_profiles.id"), nullable=False
    )

    # Task Details
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Task Type and Priority
    task_type: Mapped[str] = mapped_column(
        String, nullable=False, index=True
    )  # call, email, meeting, demo, proposal, follow_up
    priority: Mapped[str] = mapped_column(
        String, default="medium", index=True
    )  # low, medium, high, urgent

    # Task Status
    status: Mapped[str] = mapped_column(
        String, default="pending", index=True
    )  # pending, in_progress, completed, cancelled

    # Task Timing
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Task Assignment
    assigned_to: Mapped[Optional[str]] = mapped_column(String, index=True)
    assigned_by: Mapped[Optional[str]] = mapped_column(String)

    # Task Outcome
    outcome: Mapped[Optional[str]] = mapped_column(String)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Automation
    is_automated: Mapped[bool] = mapped_column(Boolean, default=False)
    follow_up_rule_id: Mapped[Optional[str]] = mapped_column(String, index=True)

    # Metadata
    meta_json: Mapped[Optional[dict]] = mapped_column(JSON, default={})

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    lead = relationship("Lead", back_populates="sales_tasks")
    business_profile = relationship("BusinessProfile")


class FollowUpRule(Base):
    """Automated follow-up rules for lead management"""

    __tablename__ = "follow_up_rules"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    business_profile_id: Mapped[str] = mapped_column(
        String, ForeignKey("business_profiles.id"), nullable=False, index=True
    )

    # Rule Details
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Rule Conditions
    trigger_event: Mapped[str] = mapped_column(
        String, nullable=False, index=True
    )  # lead_created, lead_status_changed, interaction_logged, score_changed
    trigger_status: Mapped[Optional[str]] = mapped_column(String, index=True)
    trigger_score_threshold: Mapped[Optional[int]] = mapped_column(Integer)

    # Rule Timing
    delay_hours: Mapped[int] = mapped_column(Integer, default=24)
    delay_business_days_only: Mapped[bool] = mapped_column(Boolean, default=False)

    # Task Configuration
    task_type: Mapped[str] = mapped_column(String, nullable=False)
    task_title_template: Mapped[str] = mapped_column(String, nullable=False)
    task_description_template: Mapped[Optional[str]] = mapped_column(String)
    task_priority: Mapped[str] = mapped_column(String, default="medium")

    # Assignment
    assign_to_agent: Mapped[Optional[str]] = mapped_column(String)

    # Rule Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    last_executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Metadata
    meta_json: Mapped[Optional[dict]] = mapped_column(JSON, default={})

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    business_profile = relationship("BusinessProfile")


class Goal(Base):
    """Business goals"""

    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    business_profile_id: Mapped[str] = mapped_column(
        String, ForeignKey("business_profiles.id"), nullable=False
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    priority: Mapped[str] = mapped_column(String, default=GoalPriority.MEDIUM)
    status: Mapped[str] = mapped_column(String, default=GoalStatus.NOT_STARTED)

    target_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    actual_completion_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Metrics
    target_value: Mapped[Optional[float]] = mapped_column(Float)
    current_value: Mapped[Optional[float]] = mapped_column(Float)
    progress_percentage: Mapped[Optional[float]] = mapped_column(Float)

    meta_json: Mapped[Optional[dict]] = mapped_column(JSON, default={})

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="goals")
    suggestions = relationship(
        "Suggestion", back_populates="goal", cascade="all, delete-orphan"
    )


class Suggestion(Base):
    """AI-generated suggestions for goals"""

    __tablename__ = "suggestions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    goal_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("goals.id"), nullable=True
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(String, default=SuggestionStatus.NEW)

    category: Mapped[Optional[str]] = mapped_column(String)
    expected_impact: Mapped[Optional[str]] = mapped_column(String)
    difficulty: Mapped[Optional[str]] = mapped_column(String)

    meta_json: Mapped[Optional[dict]] = mapped_column(JSON, default={})

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    goal = relationship("Goal", back_populates="suggestions")


BusinessSuggestion = Suggestion


class ScoreRecord(Base):
    """Historical record of business scores"""

    __tablename__ = "score_records"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    business_profile_id: Mapped[str] = mapped_column(
        String, ForeignKey("business_profiles.id"), nullable=False, index=True
    )

    score_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    sub_metrics: Mapped[dict] = mapped_column(JSON, default={})

    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_score_profile_type", "business_profile_id", "score_type"),
        CheckConstraint(
            "score_type IN ('business_health', 'growth_potential', 'financial_stability', 'market_position', 'operational_efficiency', 'innovation_readiness')",
            name="check_score_type",
        ),
    )


class AnalyticsMetric(Base):
    """Historical record of analytics metrics"""

    __tablename__ = "analytics_metrics"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    business_profile_id: Mapped[str] = mapped_column(
        String, ForeignKey("business_profiles.id"), nullable=False, index=True
    )

    metric_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    metric_unit: Mapped[Optional[str]] = mapped_column(String)
    metric_metadata: Mapped[Optional[dict]] = mapped_column(JSON, default={})

    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_analytics_profile_name", "business_profile_id", "metric_name"),
        Index("idx_analytics_recorded", "recorded_at"),
    )


CompanyGoal = Goal


class GrowthScoreRecord(ScoreRecord):
    """Alias for ScoreRecord for growth tracking"""

    pass


class GrowthPlan(Base):
    """Growth plans for business development"""

    __tablename__ = "growth_plans"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    business_profile_id: Mapped[str] = mapped_column(
        String, ForeignKey("business_profiles.id"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    timeframe: Mapped[Optional[str]] = mapped_column(String)
    plan_data: Mapped[dict] = mapped_column(JSON, default={})
    status: Mapped[str] = mapped_column(String, default="draft")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        Index("idx_growth_profile_status", "business_profile_id", "status"),
    )


class CostingAnalysis(Base):
    """Costing analysis for business financial planning"""

    __tablename__ = "costing_analyses"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    business_profile_id: Mapped[str] = mapped_column(
        String, ForeignKey("business_profiles.id"), nullable=False, index=True
    )

    analysis_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    cost_structure: Mapped[dict] = mapped_column(JSON, default={})
    pricing_strategies: Mapped[Optional[dict]] = mapped_column(JSON, default={})
    optimization_opportunities: Mapped[Optional[list]] = mapped_column(JSON, default=[])
    break_even_analysis: Mapped[Optional[dict]] = mapped_column(JSON, default={})

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_costing_profile_date", "business_profile_id", "analysis_date"),
    )


class SalesTransaction(Base):
    """Sales transaction records from marketplaces or manual entry"""

    __tablename__ = "sales_transactions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    business_profile_id: Mapped[str] = mapped_column(
        String, ForeignKey("business_profiles.id"), nullable=False, index=True
    )

    platform: Mapped[str] = mapped_column(String, nullable=False, index=True)
    external_id: Mapped[Optional[str]] = mapped_column(String, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, default="USD")
    status: Mapped[str] = mapped_column(String, default="completed", index=True)
    product_details: Mapped[Optional[dict]] = mapped_column(JSON, default={})
    customer_info: Mapped[Optional[dict]] = mapped_column(JSON, default={})
    transaction_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_sales_profile_date", "business_profile_id", "transaction_date"),
        Index("idx_sales_platform_date", "platform", "transaction_date"),
        UniqueConstraint('business_profile_id', 'platform', 'external_id', name='uq_sales_reference'),
    )


class MarketplaceCredential(Base):
    """Credentials for marketplace integrations"""

    __tablename__ = "marketplace_credentials"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    business_profile_id: Mapped[str] = mapped_column(
        String, ForeignKey("business_profiles.id"), nullable=False, index=True
    )

    platform: Mapped[str] = mapped_column(String, nullable=False, index=True)
    credential_data: Mapped[dict] = mapped_column(JSON, default={})
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        Index("idx_marketplace_profile_platform", "business_profile_id", "platform"),
    )


class Job(Base):
    """Background job tracking"""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)

    job_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default=JobStatus.PENDING)

    # Input/Output
    input_data: Mapped[Optional[dict]] = mapped_column(JSON, default={})
    output_data: Mapped[Optional[dict]] = mapped_column(JSON, default={})

    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_jobs_user_status", "user_id", "status"),
        Index("idx_jobs_created", "created_at"),
    )


class ConversationSession(Base):
    """BMC conversation sessions"""

    __tablename__ = "conversation_sessions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)

    phase: Mapped[str] = mapped_column(String, default=ConversationPhase.INTRO)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)

    # Conversation Data
    conversation_data: Mapped[dict] = mapped_column(JSON, default={})
    canvas_data: Mapped[dict] = mapped_column(JSON, default={})

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class AgentInteraction(Base):
    """Track agent orchestrations"""

    __tablename__ = "agent_interactions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)

    interaction_type: Mapped[str] = mapped_column(
        String, nullable=False
    )  # bmc_analysis, growth_scoring, etc.

    # Input/Output
    input_data: Mapped[dict] = mapped_column(JSON, default={})
    output_data: Mapped[dict] = mapped_column(JSON, default={})

    # Status
    status: Mapped[str] = mapped_column(String, default=JobStatus.PENDING)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_agent_user_type", "user_id", "interaction_type"),)


# ============================================================================
# TOKEN BILLING MODELS
# ============================================================================


class TokenAccount(Base):
    """Manages user token balances and subscription tiers"""

    __tablename__ = "token_accounts"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String, nullable=False, unique=True, index=True
    )

    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0000)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")

    tier: Mapped[str] = mapped_column(
        String, nullable=False, default="Free", index=True
    )

    status: Mapped[str] = mapped_column(
        String, nullable=False, default="active", index=True
    )

    rollover_balance: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0000
    )

    last_token_charge_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    transactions = relationship(
        "TokenTransaction", back_populates="token_account", cascade="all, delete-orphan"
    )
    quotas = relationship(
        "UsageQuota", back_populates="token_account", cascade="all, delete-orphan"
    )
    model_preferences = relationship(
        "ModelPreference", back_populates="token_account", cascade="all, delete-orphan"
    )
    alerts = relationship(
        "TokenUsageAlert", back_populates="token_account", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_token_user_tier", "user_id", "tier"),
        CheckConstraint(
            "tier IN ('Free', 'SME', 'Business', 'Enterprise')", name="check_tier"
        ),
        CheckConstraint(
            "status IN ('active', 'suspended', 'cancelled')", name="check_status"
        ),
    )


class TokenTransaction(Base):
    """Detailed transaction log for all token movements"""

    __tablename__ = "token_transactions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    token_account_id: Mapped[str] = mapped_column(
        String, ForeignKey("token_accounts.id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)

    # Transaction Details
    transaction_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # Positive for purchases/additions, negative for refunds/usage
    balance_after: Mapped[float] = mapped_column(Float, nullable=False)

    # Service Details
    service_type: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, index=True
    )
    model_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    provider_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    modality: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)

    operation_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    operation_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Usage Metrics
    input_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tokens_consumed: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, index=True
    )

    estimated_cost_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Metadata
    meta_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    token_account = relationship("TokenAccount", back_populates="transactions")

    __table_args__ = (
        Index("idx_transaction_user_date", "user_id", "created_at"),
        Index("idx_transaction_type_date", "transaction_type", "created_at"),
        Index("idx_transaction_operation", "operation_id"),
        CheckConstraint(
            "transaction_type IN ('purchase', 'usage', 'refund', 'bonus', 'rollover', 'adjustment')",
            name="check_transaction_type",
        ),
    )


class UsageQuota(Base):
    """Usage limits per tier and period"""

    __tablename__ = "usage_quotas"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    token_account_id: Mapped[str] = mapped_column(
        String, ForeignKey("token_accounts.id"), nullable=False, index=True
    )

    tier: Mapped[str] = mapped_column(String, nullable=False, index=True)
    period_type: Mapped[str] = mapped_column(
        String, nullable=False, index=True
    )  # daily, monthly, annual

    # Quota Limits
    max_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_images: Mapped[int] = mapped_column(Integer, default=0)
    max_videos: Mapped[int] = mapped_column(Integer, default=0)
    max_agents: Mapped[int] = mapped_column(Integer, default=0)
    max_api_calls: Mapped[int] = mapped_column(Integer, default=0)

    # Usage Tracking
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    images_used: Mapped[int] = mapped_column(Integer, default=0)
    videos_used: Mapped[int] = mapped_column(Integer, default=0)
    agents_used: Mapped[int] = mapped_column(Integer, default=0)
    api_calls_used: Mapped[int] = mapped_column(Integer, default=0)

    # Reset Schedule
    reset_day: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # For monthly quotas
    last_reset: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    token_account = relationship("TokenAccount", back_populates="quotas")

    __table_args__ = (
        UniqueConstraint(
            "token_account_id",
            "tier",
            "period_type",
            name="uq_quota_account_tier_period",
        ),
        Index(
            "idx_quota_account_tier_period", "token_account_id", "tier", "period_type"
        ),
        CheckConstraint(
            "period_type IN ('daily', 'monthly', 'annual')", name="check_period_type"
        ),
    )


class ProviderCostRate(Base):
    """Tracks costs per AI provider and model"""

    __tablename__ = "provider_cost_rates"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )

    provider_id: Mapped[str] = mapped_column(
        String, nullable=False, unique=True, index=True
    )
    provider_name: Mapped[str] = mapped_column(String, nullable=False)

    service_type: Mapped[str] = mapped_column(String, nullable=False, index=True)

    model_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Cost Configuration
    price_per_1k_tokens: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_per_image: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_per_video_second: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    price_per_agent_call: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")

    # Negotiated Rates
    is_negotiated: Mapped[bool] = mapped_column(Boolean, default=False)
    volume_discount_percent: Mapped[float] = mapped_column(Float, default=0.00)

    # Performance
    avg_latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    success_rate: Mapped[float] = mapped_column(Float, default=99.5)

    last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        Index("idx_provider_service", "provider_id", "service_type"),
        Index("idx_provider_model", "provider_id", "service_type", "model_id"),
        CheckConstraint(
            "service_type IN ('text_llm', 'image_generation', 'video_generation', 'agent_orchestration', 'analysis', 'transcription')",
            name="check_service_type",
        ),
    )


class TokenPackage(Base):
    """Predefined token packages users can purchase"""

    __tablename__ = "token_packages"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    token_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, default="USD")

    tier: Mapped[str] = mapped_column(String, nullable=False, index=True)

    bonus_tokens: Mapped[int] = mapped_column(Integer, default=0)
    features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        CheckConstraint(
            "tier IN ('Free', 'SME', 'Business', 'Enterprise')",
            name="check_package_tier",
        ),
    )


class ModelPreference(Base):
    """Stores user's preferred models for each service type"""

    __tablename__ = "model_preferences"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    token_account_id: Mapped[str] = mapped_column(
        String, ForeignKey("token_accounts.id"), nullable=False, index=True
    )

    # Preferred Models
    preferred_text_llm_model: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    preferred_text_llm_provider: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    preferred_image_generation_model: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    preferred_image_generation_provider: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    preferred_video_generation_model: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    preferred_video_generation_provider: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    preferred_agent_orchestration_provider: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )

    # Settings
    smart_selection_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_select_cheapest: Mapped[bool] = mapped_column(Boolean, default=True)
    max_cost_per_operation: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    token_account = relationship("TokenAccount", back_populates="model_preferences")

    __table_args__ = (Index("idx_model_preferences_account", "token_account_id"),)


class TokenUsageAlert(Base):
    """Tracks when users approach quota limits"""

    __tablename__ = "token_usage_alerts"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    token_account_id: Mapped[str] = mapped_column(
        String, ForeignKey("token_accounts.id"), nullable=False, index=True
    )

    # Alert Details
    alert_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    service_type: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Metrics
    current_tokens_remaining: Mapped[int] = mapped_column(Integer, nullable=False)
    percentage_used: Mapped[float] = mapped_column(Float)
    estimated_time_remaining: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # Days

    # Resolution
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    meta_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    token_account = relationship("TokenAccount", back_populates="alerts")

    __table_args__ = (
        Index("idx_alert_account_type", "token_account_id", "alert_type"),
        Index("idx_alert_severity", "severity"),
        CheckConstraint(
            "alert_type IN ('quota_warning', 'quota_exceeded', 'cost_surge', 'usage_anomaly')",
            name="check_alert_type",
        ),
        CheckConstraint(
            "severity IN ('info', 'warning', 'critical', 'emergency')",
            name="check_severity",
        ),
    )


class TemplateCategory(Base):
    """Categories for organizing ideation templates"""

    __tablename__ = "template_categories"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    business_profile_id: Mapped[Optional[str]] = mapped_column(String, index=True)

    # Category Details
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    color: Mapped[Optional[str]] = mapped_column(String)
    icon: Mapped[Optional[str]] = mapped_column(String)

    # Metadata
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    template_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class IdeationTemplate(Base):
    """Custom and default ideation templates"""

    __tablename__ = "ideation_templates"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    business_profile_id: Mapped[Optional[str]] = mapped_column(String, index=True)
    category_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("template_categories.id"), index=True
    )

    # Template Details
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    framework: Mapped[str] = mapped_column(String, nullable=False)
    
    # Template Content
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_template: Mapped[str] = mapped_column(Text)
    custom_instructions: Mapped[Optional[str]] = mapped_column(Text)
    
    # Configuration
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Metadata
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    meta_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class IdeationSession(Base):
    """Track ideation sessions for analytics and history"""

    __tablename__ = "ideation_sessions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    business_profile_id: Mapped[Optional[str]] = mapped_column(String, index=True)
    template_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("ideation_templates.id"), index=True
    )

    # Session Details
    action: Mapped[str] = mapped_column(String, nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String, nullable=False)
    template_name: Mapped[Optional[str]] = mapped_column(String)
    
    # Configuration
    innovation_level: Mapped[str] = mapped_column(String, default="incremental")
    quantity: Mapped[int] = mapped_column(Integer, default=10)
    enhance_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Context
    industry: Mapped[Optional[str]] = mapped_column(String)
    target_audience: Mapped[Optional[str]] = mapped_column(String)
    constraints: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    custom_instructions: Mapped[Optional[str]] = mapped_column(Text)
    
    # Status
    status: Mapped[str] = mapped_column(String, default="pending")
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Results Summary
    ideas_count: Mapped[int] = mapped_column(Integer, default=0)
    insights_count: Mapped[int] = mapped_column(Integer, default=0)
    recommendations_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)


class IdeationResult(Base):
    """Individual ideation results/ideas"""

    __tablename__ = "ideation_results"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        String, ForeignKey("ideation_sessions.id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)

    # Result Details
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String)
    
    # Scores
    impact: Mapped[str] = mapped_column(String)
    effort: Mapped[str] = mapped_column(String)
    innovation_type: Mapped[str] = mapped_column(String)
    feasibility_score: Mapped[int] = mapped_column(Integer)
    novelty_score: Mapped[int] = mapped_column(Integer)
    value_score: Mapped[int] = mapped_column(Integer)
    overall_score: Mapped[int] = mapped_column(Integer)
    
    # Content
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    implementation_steps: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    risks: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    meta_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # User Interaction
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_result_session_user", "session_id", "user_id"),
        Index("idx_result_score", "overall_score"),
        CheckConstraint(
            "feasibility_score >= 0 AND feasibility_score <= 100",
            name="check_feasibility_score"
        ),
        CheckConstraint(
            "novelty_score >= 0 AND novelty_score <= 100",
            name="check_novelty_score"
        ),
        CheckConstraint(
            "value_score >= 0 AND value_score <= 100",
            name="check_value_score"
        ),
        CheckConstraint(
            "overall_score >= 0 AND overall_score <= 100",
            name="check_overall_score"
        ),
    )


class OwnerAgentRun(Base):
    __tablename__ = 'owner_agent_runs'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    kind: Mapped[str] = mapped_column(String)
    objective: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default='needs_review')
    output: Mapped[str] = mapped_column(Text, default='')
    error: Mapped[Optional[str]] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String)
    context_snapshot: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (CheckConstraint("status IN ('needs_review','approved','dismissed','failed')"),)


class OwnerCampaign(Base):
    __tablename__ = 'owner_campaigns'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    title: Mapped[str] = mapped_column(String)
    platform: Mapped[str] = mapped_column(String)
    caption: Mapped[str] = mapped_column(Text)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String, default='draft')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (CheckConstraint("status IN ('draft','approved','archived')"),)


class AdProfile(Base):
    __tablename__ = 'ad_profiles'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdDraft(Base):
    __tablename__ = 'ad_drafts'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    profile_id: Mapped[str] = mapped_column(String, ForeignKey('ad_profiles.id'), index=True)
    profile_snapshot: Mapped[dict] = mapped_column(JSON)
    data: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String, default='draft')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (CheckConstraint("status IN ('draft','approved')"),)


class AdAsset(Base):
    __tablename__ = 'ad_assets'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    name: Mapped[str] = mapped_column(String)
    mime: Mapped[str] = mapped_column(String)
    content: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AdVideoJob(Base):
    __tablename__ = 'ad_video_jobs'
    id: Mapped[str] = mapped_column(String, primary_key=True)
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    operation: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default='submitting')
    error: Mapped[Optional[str]] = mapped_column(Text)
    asset_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('ad_assets.id'))
    prompt: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (CheckConstraint("status IN ('submitting','processing','completed','failed')"),)


class WorkspaceDocument(Base):
    __tablename__ = 'workspace_documents'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    kind: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    fields: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OwnerTask(Base):
    __tablename__ = 'owner_tasks'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    title: Mapped[str] = mapped_column(String)
    notes: Mapped[str] = mapped_column(Text, default='')
    owner: Mapped[str] = mapped_column(String, default='')
    due_date: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default='open')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (CheckConstraint("status IN ('open','in_progress','done')"),)


class AdPerformance(Base):
    __tablename__ = 'ad_performance'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    day: Mapped[str] = mapped_column(String)
    platform: Mapped[str] = mapped_column(String)
    campaign: Mapped[str] = mapped_column(String)
    creative: Mapped[str] = mapped_column(String)
    currency: Mapped[str] = mapped_column(String)
    attribution: Mapped[str] = mapped_column(String)
    impressions: Mapped[int] = mapped_column(Integer)
    clicks: Mapped[int] = mapped_column(Integer)
    conversions: Mapped[int] = mapped_column(Integer)
    spend_cents: Mapped[int] = mapped_column(Integer)
    revenue_cents: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('business_profile_id','day','platform','campaign','creative','currency','attribution', name='uq_ad_performance_day'),)


class AutomationRule(Base):
    __tablename__ = 'automation_rules'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    template_key: Mapped[str] = mapped_column(String)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    interval_hours: Mapped[int] = mapped_column(Integer, default=24)
    next_run_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_status: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (UniqueConstraint('business_profile_id','template_key',name='uq_automation_template'),
                     CheckConstraint('interval_hours IN (1,6,24,168)'),)


class AutomationRun(Base):
    __tablename__ = 'automation_runs'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id: Mapped[str] = mapped_column(String, ForeignKey('automation_rules.id'), index=True)
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    slot: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    summary: Mapped[str] = mapped_column(Text)
    task_ids: Mapped[list] = mapped_column(JSON, default=list)
    advisor_run_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('owner_agent_runs.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('rule_id','slot',name='uq_automation_run_slot'),
                     CheckConstraint("status IN ('completed','no_action','failed')"),)


class AutomationAction(Base):
    __tablename__ = 'automation_actions'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id: Mapped[str] = mapped_column(String, ForeignKey('automation_rules.id'), index=True)
    source_key: Mapped[str] = mapped_column(String)
    task_id: Mapped[str] = mapped_column(String, ForeignKey('owner_tasks.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('rule_id','source_key',name='uq_automation_action_source'),)


class BookAccount(Base):
    __tablename__ = 'book_accounts'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    code: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    kind: Mapped[str] = mapped_column(String)
    currency: Mapped[str] = mapped_column(String)
    is_cash: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = (UniqueConstraint('business_profile_id','code',name='uq_book_account'),
                     CheckConstraint("kind IN ('asset','liability','equity','income','expense')"),)


class BookEntry(Base):
    __tablename__ = 'book_entries'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    day: Mapped[str] = mapped_column(String, index=True)
    reference: Mapped[str] = mapped_column(String)
    memo: Mapped[str] = mapped_column(Text)
    currency: Mapped[str] = mapped_column(String)
    created_by: Mapped[str] = mapped_column(String)
    reversal_of: Mapped[Optional[str]] = mapped_column(String, ForeignKey('book_entries.id'), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('business_profile_id','reference',name='uq_book_reference'),)


class BookLine(Base):
    __tablename__ = 'book_lines'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entry_id: Mapped[str] = mapped_column(String, ForeignKey('book_entries.id'), index=True)
    account_id: Mapped[str] = mapped_column(String, ForeignKey('book_accounts.id'), index=True)
    debit_cents: Mapped[int] = mapped_column(BigInteger, default=0)
    credit_cents: Mapped[int] = mapped_column(BigInteger, default=0)
    __table_args__ = (CheckConstraint('debit_cents >= 0 AND credit_cents >= 0 AND ((debit_cents > 0 AND credit_cents = 0) OR (credit_cents > 0 AND debit_cents = 0))'),)


class BookReconciliation(Base):
    __tablename__ = 'book_reconciliations'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    account_id: Mapped[str] = mapped_column(String, ForeignKey('book_accounts.id'), index=True)
    day: Mapped[str] = mapped_column(String)
    statement_cents: Mapped[int] = mapped_column(BigInteger)
    book_cents: Mapped[int] = mapped_column(BigInteger)
    reference: Mapped[str] = mapped_column(String)
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('account_id','day',name='uq_book_reconciliation'),)


class Employee(Base):
    __tablename__ = 'employees'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    code: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, default='')
    department: Mapped[str] = mapped_column(String, default='')
    job_title: Mapped[str] = mapped_column(String, default='')
    manager_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('employees.id'))
    start_date: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default='active')
    annual_leave_days: Mapped[int] = mapped_column(Integer, default=0)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('business_profile_id','code',name='uq_employee_code'),
                     CheckConstraint("status IN ('active','onboarding','inactive')"),
                     CheckConstraint('annual_leave_days >= 0 AND annual_leave_days <= 365'),)


class LeaveRequest(Base):
    __tablename__ = 'leave_requests'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    employee_id: Mapped[str] = mapped_column(String, ForeignKey('employees.id'), index=True)
    start_date: Mapped[str] = mapped_column(String)
    end_date: Mapped[str] = mapped_column(String)
    days: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String)
    note: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String, default='pending')
    reviewed_by: Mapped[Optional[str]] = mapped_column(String)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (CheckConstraint("status IN ('pending','approved','rejected','cancelled')"),
                     CheckConstraint("kind IN ('annual','unpaid')"),CheckConstraint('days > 0'),)


class EmployeeTask(Base):
    __tablename__ = 'employee_tasks'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    employee_id: Mapped[str] = mapped_column(String, ForeignKey('employees.id'), index=True)
    title: Mapped[str] = mapped_column(String)
    due_date: Mapped[str] = mapped_column(String)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_by: Mapped[Optional[str]] = mapped_column(String)


class BillingCustomer(Base):
    __tablename__ = 'billing_customers'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, default='')
    address: Mapped[str] = mapped_column(Text, default='')
    registration_number: Mapped[str] = mapped_column(String, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CommercialDocument(Base):
    __tablename__ = 'commercial_documents'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    customer_id: Mapped[str] = mapped_column(String, ForeignKey('billing_customers.id'), index=True)
    kind: Mapped[str] = mapped_column(String)
    number: Mapped[str] = mapped_column(String)
    sequence: Mapped[int] = mapped_column(Integer)
    year: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, default='draft')
    day: Mapped[str] = mapped_column(String)
    due_date: Mapped[str] = mapped_column(String)
    currency: Mapped[str] = mapped_column(String)
    seller: Mapped[dict] = mapped_column(JSON)
    customer: Mapped[dict] = mapped_column(JSON)
    lines: Mapped[list] = mapped_column(JSON)
    subtotal_cents: Mapped[int] = mapped_column(BigInteger)
    discount_cents: Mapped[int] = mapped_column(BigInteger)
    tax_cents: Mapped[int] = mapped_column(BigInteger)
    total_cents: Mapped[int] = mapped_column(BigInteger)
    notes: Mapped[str] = mapped_column(Text, default='')
    terms: Mapped[str] = mapped_column(Text, default='')
    decision_note: Mapped[str] = mapped_column(Text, default='')
    source_quote_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('commercial_documents.id'), unique=True)
    journal_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('book_entries.id'))
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('business_profile_id','number',name='uq_document_number'),
                     CheckConstraint("kind IN ('quotation','invoice')"),
                     CheckConstraint("status IN ('draft','issued','accepted','declined','paid','void')"),)


class InvoicePayment(Base):
    __tablename__ = 'invoice_payments'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    document_id: Mapped[str] = mapped_column(String, ForeignKey('commercial_documents.id'), index=True)
    reference: Mapped[str] = mapped_column(String)
    day: Mapped[str] = mapped_column(String)
    amount_cents: Mapped[int] = mapped_column(BigInteger)
    account_id: Mapped[str] = mapped_column(String, ForeignKey('book_accounts.id'))
    journal_id: Mapped[str] = mapped_column(String, ForeignKey('book_entries.id'))
    reversal_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('book_entries.id'))
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('business_profile_id','reference',name='uq_invoice_payment_reference'),CheckConstraint('amount_cents > 0'),)


class BusinessAgent(Base):
    __tablename__ = 'business_agents'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    name: Mapped[str] = mapped_column(String)
    instructions: Mapped[str] = mapped_column(Text)
    tools: Mapped[list] = mapped_column(JSON, default=list)
    public_context: Mapped[str] = mapped_column(Text, default='')
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    interval_hours: Mapped[int] = mapped_column(Integer, default=0)
    schedule_prompt: Mapped[str] = mapped_column(Text, default='')
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (CheckConstraint('interval_hours IN (0,1,6,24,168)'),)


class AgentConversation(Base):
    __tablename__ = 'agent_conversations'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    agent_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('business_agents.id'), index=True)
    title: Mapped[str] = mapped_column(String)
    busy_until: Mapped[Optional[datetime]] = mapped_column(DateTime)
    busy_token: Mapped[Optional[str]] = mapped_column(String)
    builder_state: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AgentMessage(Base):
    __tablename__ = 'agent_messages'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id: Mapped[str] = mapped_column(String, ForeignKey('agent_conversations.id'), index=True)
    role: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    trace: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AgentProposal(Base):
    __tablename__ = 'agent_proposals'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    conversation_id: Mapped[str] = mapped_column(String, ForeignKey('agent_conversations.id'), index=True)
    kind: Mapped[str] = mapped_column(String)
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String, default='pending')
    result: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AgentScheduleRun(Base):
    __tablename__ = 'agent_schedule_runs'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(String, ForeignKey('business_agents.id'), index=True)
    slot: Mapped[str] = mapped_column(String)
    conversation_id: Mapped[str] = mapped_column(String, ForeignKey('agent_conversations.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('agent_id','slot',name='uq_agent_schedule_slot'),)


class AgentChannel(Base):
    __tablename__ = 'agent_channels'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey('business_profiles.id'), index=True)
    agent_id: Mapped[str] = mapped_column(String, ForeignKey('business_agents.id'), index=True)
    platform: Mapped[str] = mapped_column(String)
    external_id: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    credentials: Mapped[str] = mapped_column(Text)
    webhook_secret: Mapped[str] = mapped_column(String)
    verify_token: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default='verified')
    automation: Mapped[str] = mapped_column(String, default='manual')
    response_mode: Mapped[str] = mapped_column(String, default='fixed')
    fixed_reply: Mapped[str] = mapped_column(Text, default='')
    daily_limit: Mapped[int] = mapped_column(Integer, default=50)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('platform','external_id',name='uq_agent_channel_identity'),)


class ChannelMessage(Base):
    __tablename__ = 'channel_messages'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    channel_id: Mapped[str] = mapped_column(String, ForeignKey('agent_channels.id'), index=True)
    external_id: Mapped[str] = mapped_column(String)
    peer: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default='queued')
    error: Mapped[Optional[str]] = mapped_column(Text)
    processing_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('channel_id','external_id',name='uq_channel_inbound'),)


class ChannelOutbox(Base):
    __tablename__ = 'channel_outbox'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    channel_id: Mapped[str] = mapped_column(String, ForeignKey('agent_channels.id'), index=True)
    inbound_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('channel_messages.id'), unique=True)
    peer: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    template: Mapped[Optional[dict]] = mapped_column(JSON)
    consent: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String, default='pending')
    provider_message_id: Mapped[Optional[str]] = mapped_column(String, index=True)
    error: Mapped[Optional[str]] = mapped_column(Text)
    attempted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


class PilotRequest(Base):
    __tablename__ = 'pilot_requests'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100))
    company: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(254))
    workflow: Mapped[str] = mapped_column(String(30))
    goal: Mapped[str] = mapped_column(Text)
    contact_consent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(20), default='new', index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (CheckConstraint("status IN ('new','contacted','closed')"),)


class PilotIntakeLimit(Base):
    __tablename__ = 'pilot_intake_limits'
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
