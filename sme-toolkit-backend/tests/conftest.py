"""
Pytest configuration and fixtures for SME Toolkit Backend tests
"""
import asyncio
import os
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.config import settings


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.
    Uses in-memory SQLite for fast, isolated tests.
    """
    # Create async engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create session
    async with async_session_maker() as session:
        yield session

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Dispose engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test client for the FastAPI app.
    Overrides the database dependency with test database.
    """
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini AI client for testing."""
    with patch("google.generativeai.GenerativeModel") as mock:
        mock_instance = MagicMock()
        mock_instance.generate_content_async = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_redis_cache():
    """Mock Redis cache for testing."""
    with patch("app.services.cache_service.CacheService") as mock:
        cache_instance = MagicMock()
        cache_instance.get = AsyncMock(return_value=None)
        cache_instance.set = AsyncMock()
        cache_instance.delete = AsyncMock()
        mock.return_value = cache_instance
        yield cache_instance


@pytest.fixture
def sample_business_profile():
    """Sample business profile data for testing."""
    return {
        "id": "test-profile-1",
        "company_name": "Test Company",
        "industry": "Technology",
        "stage": "growth",
        "bmc_data": {
            "valuePropositions": ["Innovative solutions"],
            "customerSegments": ["Small businesses"],
            "channels": ["Online", "Direct sales"],
            "customerRelationships": ["Self-service"],
            "revenueStreams": ["Subscription", "Consulting"],
            "keyResources": ["Technology", "Team"],
            "keyActivities": ["Development", "Sales"],
            "keyPartners": ["Cloud providers"],
            "costStructure": ["Salaries", "Infrastructure"]
        },
        "financial_data": {
            "monthly_revenue": 50000,
            "monthly_costs": 35000,
            "profit_margin": 0.30
        },
        "goals": [
            {
                "id": "goal-1",
                "title": "Increase revenue",
                "target": 75000,
                "current": 50000,
                "deadline": "2024-12-31"
            }
        ]
    }


@pytest.fixture
def sample_goal_data():
    """Sample goal data for testing."""
    return {
        "title": "Increase Monthly Revenue",
        "description": "Achieve $75,000 monthly recurring revenue",
        "category": "financial",
        "target_value": 75000,
        "current_value": 50000,
        "deadline": "2024-12-31",
        "priority": "high"
    }


@pytest.fixture
def sample_growth_plan_data():
    """Sample growth plan data for testing."""
    return {
        "title": "6-Month Growth Strategy",
        "timeframe": "6 months",
        "target_metrics": {
            "revenue_growth": "50%",
            "customer_acquisition": "200 new customers"
        }
    }


@pytest.fixture
def sample_costing_data():
    """Sample costing data for testing."""
    return {
        "fixed_costs": {
            "rent": 8000,
            "salaries": 15000,
            "software": 2000
        },
        "variable_costs": {
            "materials": 8000,
            "shipping": 4000,
            "commissions": 3000
        },
        "current_price": 40,
        "units_sold": 2000
    }


@pytest.fixture
def sample_suggestion_request():
    """Sample suggestion request data for testing."""
    return {
        "business_profile_id": "test-profile-1",
        "suggestion_types": ["new_opportunities", "partnerships", "market_expansions"]
    }


@pytest.fixture
def sample_analysis_request():
    """Sample comprehensive analysis request."""
    return {
        "business_profile_id": "test-profile-1",
        "analysis_type": "comprehensive",
        "include_goals": True,
        "include_growth": True,
        "include_costing": True,
        "include_suggestions": True
    }


@pytest.fixture
def mock_agent_response():
    """Mock agent response for testing."""
    return {
        "success": True,
        "data": {
            "analysis": "Test analysis result",
            "recommendations": ["Recommendation 1", "Recommendation 2"],
            "confidence": 0.85
        }
    }


@pytest.fixture
def sample_score_data():
    """Sample score data for testing."""
    return {
        "business_health": {
            "overall_score": 75.5,
            "sub_metrics": {
                "financial_health": 80.0,
                "operational_efficiency": 75.0,
                "customer_satisfaction": 70.0,
                "market_position": 75.0,
                "innovation_readiness": 72.0
            }
        },
        "growth_potential": {
            "overall_score": 82.0,
            "sub_metrics": {
                "market_opportunity": 85.0,
                "competitive_advantage": 80.0,
                "execution_capability": 82.0,
                "financial_capacity": 78.0,
                "innovation_potential": 85.0
            }
        }
    }


@pytest.fixture
def sample_analytics_data():
    """Sample analytics data for testing."""
    return {
        "metrics": {
            "revenue": {"current": 50000, "previous": 45000, "trend": "up"},
            "customers": {"current": 200, "previous": 180, "trend": "up"},
            "conversion_rate": {"current": 0.05, "previous": 0.045, "trend": "up"}
        },
        "trends": {
            "revenue": [
                {"date": "2024-01", "value": 40000},
                {"date": "2024-02", "value": 42000},
                {"date": "2024-03", "value": 45000},
                {"date": "2024-04", "value": 50000}
            ]
        }
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )


# Async test configuration
pytest_plugins = ("pytest_asyncio",)
