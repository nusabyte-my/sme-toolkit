"""
Integration tests for database operations
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta


@pytest.mark.integration
class TestDatabaseCRUD:
    """Integration tests for CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_business_profile(self, test_db: AsyncSession):
        """Test creating a business profile"""
        from app.database import BusinessProfile
        
        profile = BusinessProfile(
            id="test-profile-1",
            company_name="Test Company",
            industry="Technology",
            stage="growth",
            bmc_data={"valuePropositions": ["Test"]},
            created_at=datetime.utcnow()
        )
        
        test_db.add(profile)
        await test_db.commit()
        await test_db.refresh(profile)
        
        assert profile.id is not None
        assert profile.company_name == "Test Company"

    @pytest.mark.asyncio
    async def test_read_business_profile(self, test_db: AsyncSession):
        """Test reading a business profile"""
        from app.database import BusinessProfile
        from sqlalchemy import select
        
        # Create profile
        profile = BusinessProfile(
            id="test-profile-2",
            company_name="Test Company 2",
            industry="Technology",
            stage="startup",
            bmc_data={"valuePropositions": ["Test"]},
            created_at=datetime.utcnow()
        )
        test_db.add(profile)
        await test_db.commit()
        
        # Read profile
        result = await test_db.execute(
            select(BusinessProfile).where(BusinessProfile.id == "test-profile-2")
        )
        retrieved_profile = result.scalar_one_or_none()
        
        assert retrieved_profile is not None
        assert retrieved_profile.company_name == "Test Company 2"

    @pytest.mark.asyncio
    async def test_update_business_profile(self, test_db: AsyncSession):
        """Test updating a business profile"""
        from app.database import BusinessProfile
        from sqlalchemy import select
        
        # Create profile
        profile = BusinessProfile(
            id="test-profile-3",
            company_name="Test Company 3",
            industry="Technology",
            stage="startup",
            bmc_data={"valuePropositions": ["Test"]},
            created_at=datetime.utcnow()
        )
        test_db.add(profile)
        await test_db.commit()
        
        # Update profile
        profile.company_name = "Updated Company"
        profile.stage = "growth"
        await test_db.commit()
        await test_db.refresh(profile)
        
        assert profile.company_name == "Updated Company"
        assert profile.stage == "growth"

    @pytest.mark.asyncio
    async def test_delete_business_profile(self, test_db: AsyncSession):
        """Test deleting a business profile"""
        from app.database import BusinessProfile
        from sqlalchemy import select
        
        # Create profile
        profile = BusinessProfile(
            id="test-profile-4",
            company_name="Test Company 4",
            industry="Technology",
            stage="startup",
            bmc_data={"valuePropositions": ["Test"]},
            created_at=datetime.utcnow()
        )
        test_db.add(profile)
        await test_db.commit()
        
        # Delete profile
        await test_db.delete(profile)
        await test_db.commit()
        
        # Verify deletion
        result = await test_db.execute(
            select(BusinessProfile).where(BusinessProfile.id == "test-profile-4")
        )
        retrieved_profile = result.scalar_one_or_none()
        
        assert retrieved_profile is None

    @pytest.mark.asyncio
    async def test_create_goal(self, test_db: AsyncSession):
        """Test creating a goal"""
        from app.database import CompanyGoal
        
        goal = CompanyGoal(
            id="goal-1",
            business_profile_id="test-profile-1",
            title="Increase Revenue",
            description="Achieve $75,000 monthly revenue",
            category="financial",
            target_value=75000,
            current_value=50000,
            deadline=datetime.utcnow() + timedelta(days=90),
            priority="high",
            status="in_progress",
            created_at=datetime.utcnow()
        )
        
        test_db.add(goal)
        await test_db.commit()
        await test_db.refresh(goal)
        
        assert goal.id is not None
        assert goal.title == "Increase Revenue"

    @pytest.mark.asyncio
    async def test_goal_relationships(self, test_db: AsyncSession):
        """Test goal-business profile relationships"""
        from app.database import BusinessProfile, CompanyGoal
        from sqlalchemy import select
        
        # Create profile
        profile = BusinessProfile(
            id="test-profile-5",
            company_name="Test Company 5",
            industry="Technology",
            stage="growth",
            bmc_data={"valuePropositions": ["Test"]},
            created_at=datetime.utcnow()
        )
        test_db.add(profile)
        await test_db.commit()
        
        # Create goals
        goal1 = CompanyGoal(
            id="goal-2",
            business_profile_id="test-profile-5",
            title="Goal 1",
            category="financial",
            target_value=100000,
            current_value=50000,
            deadline=datetime.utcnow() + timedelta(days=90),
            priority="high",
            status="in_progress",
            created_at=datetime.utcnow()
        )
        goal2 = CompanyGoal(
            id="goal-3",
            business_profile_id="test-profile-5",
            title="Goal 2",
            category="operational",
            target_value=50,
            current_value=30,
            deadline=datetime.utcnow() + timedelta(days=60),
            priority="medium",
            status="in_progress",
            created_at=datetime.utcnow()
        )
        test_db.add(goal1)
        test_db.add(goal2)
        await test_db.commit()
        
        # Query goals for profile
        result = await test_db.execute(
            select(CompanyGoal).where(CompanyGoal.business_profile_id == "test-profile-5")
        )
        goals = result.scalars().all()
        
        assert len(goals) == 2
        assert all(g.business_profile_id == "test-profile-5" for g in goals)

    @pytest.mark.asyncio
    async def test_create_growth_plan(self, test_db: AsyncSession):
        """Test creating a growth plan"""
        from app.database import GrowthPlan
        
        plan = GrowthPlan(
            id="gp-1",
            business_profile_id="test-profile-1",
            title="6-Month Growth Strategy",
            timeframe="6 months",
            plan_data={
                "opportunities": [],
                "channels": [],
                "roadmap": []
            },
            status="draft",
            created_at=datetime.utcnow()
        )
        
        test_db.add(plan)
        await test_db.commit()
        await test_db.refresh(plan)
        
        assert plan.id is not None
        assert plan.title == "6-Month Growth Strategy"

    @pytest.mark.asyncio
    async def test_create_costing_analysis(self, test_db: AsyncSession):
        """Test creating a costing analysis"""
        from app.database import CostingAnalysis
        
        analysis = CostingAnalysis(
            id="ca-1",
            business_profile_id="test-profile-1",
            analysis_date=datetime.utcnow(),
            cost_structure={
                "fixed_costs": {},
                "variable_costs": {}
            },
            pricing_strategies=[],
            optimization_opportunities=[],
            break_even_analysis={},
            created_at=datetime.utcnow()
        )
        
        test_db.add(analysis)
        await test_db.commit()
        await test_db.refresh(analysis)
        
        assert analysis.id is not None
        assert analysis.business_profile_id == "test-profile-1"

    @pytest.mark.asyncio
    async def test_create_business_suggestion(self, test_db: AsyncSession):
        """Test creating a business suggestion"""
        from app.database import BusinessSuggestion
        
        suggestion = BusinessSuggestion(
            id="bs-1",
            business_profile_id="test-profile-1",
            suggestion_type="new_opportunity",
            title="B2B Subscription Service",
            description="Launch subscription service for enterprise clients",
            potential_value=200000,
            feasibility_score=0.85,
            status="suggested",
            created_at=datetime.utcnow()
        )
        
        test_db.add(suggestion)
        await test_db.commit()
        await test_db.refresh(suggestion)
        
        assert suggestion.id is not None
        assert suggestion.title == "B2B Subscription Service"

    @pytest.mark.asyncio
    async def test_create_score_record(self, test_db: AsyncSession):
        """Test creating a score record"""
        from app.database import ScoreRecord
        
        record = ScoreRecord(
            id="sr-1",
            business_profile_id="test-profile-1",
            score_type="business_health",
            overall_score=75.5,
            sub_metrics={
                "financial_health": 80.0,
                "operational_efficiency": 75.0,
                "customer_satisfaction": 70.0,
                "market_position": 75.0,
                "innovation_readiness": 72.0
            },
            calculated_at=datetime.utcnow()
        )
        
        test_db.add(record)
        await test_db.commit()
        await test_db.refresh(record)
        
        assert record.id is not None
        assert record.overall_score == 75.5

    @pytest.mark.asyncio
    async def test_create_analytics_metric(self, test_db: AsyncSession):
        """Test creating an analytics metric"""
        from app.database import AnalyticsMetric
        
        metric = AnalyticsMetric(
            id="am-1",
            business_profile_id="test-profile-1",
            metric_name="monthly_revenue",
            metric_value=50000.00,
            metric_unit="USD",
            recorded_at=datetime.utcnow(),
            metadata={"source": "stripe"}
        )
        
        test_db.add(metric)
        await test_db.commit()
        await test_db.refresh(metric)
        
        assert metric.id is not None
        assert metric.metric_name == "monthly_revenue"


@pytest.mark.integration
class TestDatabaseConstraints:
    """Integration tests for database constraints"""

    @pytest.mark.asyncio
    async def test_unique_constraint_business_profile(self, test_db: AsyncSession):
        """Test unique constraint on business profile ID"""
        from app.database import BusinessProfile
        from sqlalchemy.exc import IntegrityError
        
        # Create first profile
        profile1 = BusinessProfile(
            id="test-profile-unique",
            company_name="Test Company",
            industry="Technology",
            stage="growth",
            bmc_data={"valuePropositions": ["Test"]},
            created_at=datetime.utcnow()
        )
        test_db.add(profile1)
        await test_db.commit()
        
        # Try to create duplicate
        profile2 = BusinessProfile(
            id="test-profile-unique",  # Same ID
            company_name="Another Company",
            industry="Technology",
            stage="startup",
            bmc_data={"valuePropositions": ["Test"]},
            created_at=datetime.utcnow()
        )
        test_db.add(profile2)
        
        # Should raise IntegrityError
        with pytest.raises(IntegrityError):
            await test_db.commit()

    @pytest.mark.asyncio
    async def test_foreign_key_constraint_goal(self, test_db: AsyncSession):
        """Test foreign key constraint on goal"""
        from app.database import CompanyGoal
        from sqlalchemy.exc import IntegrityError
        
        # Try to create goal with non-existent profile
        goal = CompanyGoal(
            id="goal-fk-test",
            business_profile_id="non-existent-profile",
            title="Test Goal",
            category="financial",
            target_value=100000,
            current_value=50000,
            deadline=datetime.utcnow() + timedelta(days=90),
            priority="high",
            status="in_progress",
            created_at=datetime.utcnow()
        )
        test_db.add(goal)
        
        # Should raise IntegrityError
        with pytest.raises(IntegrityError):
            await test_db.commit()

    @pytest.mark.asyncio
    async def test_not_null_constraint(self, test_db: AsyncSession):
        """Test NOT NULL constraints"""
        from app.database import BusinessProfile
        from sqlalchemy.exc import IntegrityError
        
        # Try to create profile without required fields
        profile = BusinessProfile(
            id="test-profile-null",
            # Missing company_name
            industry="Technology",
            stage="growth",
            bmc_data={"valuePropositions": ["Test"]},
            created_at=datetime.utcnow()
        )
        test_db.add(profile)
        
        # Should raise IntegrityError
        with pytest.raises(IntegrityError):
            await test_db.commit()


@pytest.mark.integration
class TestDatabaseQueries:
    """Integration tests for database queries"""

    @pytest.mark.asyncio
    async def test_query_with_filters(self, test_db: AsyncSession):
        """Test querying with filters"""
        from app.database import CompanyGoal
        from sqlalchemy import select
        
        # Create multiple goals
        for i in range(5):
            goal = CompanyGoal(
                id=f"goal-filter-{i}",
                business_profile_id="test-profile-1",
                title=f"Goal {i}",
                category="financial" if i % 2 == 0 else "operational",
                target_value=100000,
                current_value=50000,
                deadline=datetime.utcnow() + timedelta(days=90),
                priority="high" if i < 3 else "medium",
                status="in_progress",
                created_at=datetime.utcnow()
            )
            test_db.add(goal)
        await test_db.commit()
        
        # Query with filters
        result = await test_db.execute(
            select(CompanyGoal)
            .where(CompanyGoal.category == "financial")
            .where(CompanyGoal.priority == "high")
        )
        goals = result.scalars().all()
        
        assert len(goals) == 2  # Goals 0 and 2

    @pytest.mark.asyncio
    async def test_query_with_ordering(self, test_db: AsyncSession):
        """Test querying with ordering"""
        from app.database import ScoreRecord
        from sqlalchemy import select, desc
        
        # Create multiple score records
        for i in range(5):
            record = ScoreRecord(
                id=f"sr-order-{i}",
                business_profile_id="test-profile-1",
                score_type="business_health",
                overall_score=70.0 + i * 5,
                sub_metrics={},
                calculated_at=datetime.utcnow() - timedelta(days=i)
            )
            test_db.add(record)
        await test_db.commit()
        
        # Query with ordering
        result = await test_db.execute(
            select(ScoreRecord)
            .where(ScoreRecord.business_profile_id == "test-profile-1")
            .order_by(desc(ScoreRecord.overall_score))
        )
        records = result.scalars().all()
        
        assert records[0].overall_score == 90.0
        assert records[-1].overall_score == 70.0

    @pytest.mark.asyncio
    async def test_query_with_pagination(self, test_db: AsyncSession):
        """Test querying with pagination"""
        from app.database import AnalyticsMetric
        from sqlalchemy import select
        
        # Create multiple metrics
        for i in range(20):
            metric = AnalyticsMetric(
                id=f"am-page-{i}",
                business_profile_id="test-profile-1",
                metric_name="revenue",
                metric_value=50000 + i * 1000,
                metric_unit="USD",
                recorded_at=datetime.utcnow(),
                metadata={}
            )
            test_db.add(metric)
        await test_db.commit()
        
        # Query with pagination
        result = await test_db.execute(
            select(AnalyticsMetric)
            .where(AnalyticsMetric.business_profile_id == "test-profile-1")
            .limit(10)
            .offset(5)
        )
        metrics = result.scalars().all()
        
        assert len(metrics) == 10

    @pytest.mark.asyncio
    async def test_query_with_joins(self, test_db: AsyncSession):
        """Test querying with joins"""
        from app.database import BusinessProfile, CompanyGoal
        from sqlalchemy import select
        
        # Create profile and goals
        profile = BusinessProfile(
            id="test-profile-join",
            company_name="Test Company",
            industry="Technology",
            stage="growth",
            bmc_data={"valuePropositions": ["Test"]},
            created_at=datetime.utcnow()
        )
        test_db.add(profile)
        await test_db.commit()
        
        for i in range(3):
            goal = CompanyGoal(
                id=f"goal-join-{i}",
                business_profile_id="test-profile-join",
                title=f"Goal {i}",
                category="financial",
                target_value=100000,
                current_value=50000,
                deadline=datetime.utcnow() + timedelta(days=90),
                priority="high",
                status="in_progress",
                created_at=datetime.utcnow()
            )
            test_db.add(goal)
        await test_db.commit()
        
        # Query with join
        result = await test_db.execute(
            select(BusinessProfile, CompanyGoal)
            .join(CompanyGoal, BusinessProfile.id == CompanyGoal.business_profile_id)
            .where(BusinessProfile.id == "test-profile-join")
        )
        rows = result.all()
        
        assert len(rows) == 3
        assert all(row[0].id == "test-profile-join" for row in rows)


@pytest.mark.integration
class TestDatabasePerformance:
    """Integration tests for database performance"""

    @pytest.mark.asyncio
    async def test_bulk_insert_performance(self, test_db: AsyncSession):
        """Test bulk insert performance"""
        from app.database import AnalyticsMetric
        import time
        
        # Create 1000 metrics
        metrics = []
        for i in range(1000):
            metric = AnalyticsMetric(
                id=f"am-bulk-{i}",
                business_profile_id="test-profile-1",
                metric_name="revenue",
                metric_value=50000 + i,
                metric_unit="USD",
                recorded_at=datetime.utcnow(),
                metadata={}
            )
            metrics.append(metric)
        
        # Measure time
        start_time = time.time()
        test_db.add_all(metrics)
        await test_db.commit()
        end_time = time.time()
        
        # Should complete in reasonable time (< 5 seconds)
        assert end_time - start_time < 5.0

    @pytest.mark.asyncio
    async def test_query_performance_with_index(self, test_db: AsyncSession):
        """Test query performance with indexes"""
        from app.database import ScoreRecord
        from sqlalchemy import select
        import time
        
        # Create records
        for i in range(100):
            record = ScoreRecord(
                id=f"sr-perf-{i}",
                business_profile_id="test-profile-1",
                score_type="business_health",
                overall_score=70.0 + i * 0.3,
                sub_metrics={},
                calculated_at=datetime.utcnow()
            )
            test_db.add(record)
        await test_db.commit()
        
        # Measure query time
        start_time = time.time()
        result = await test_db.execute(
            select(ScoreRecord)
            .where(ScoreRecord.business_profile_id == "test-profile-1")
            .where(ScoreRecord.score_type == "business_health")
        )
        records = result.scalars().all()
        end_time = time.time()
        
        # Should complete quickly (< 1 second)
        assert end_time - start_time < 1.0
        assert len(records) == 100
