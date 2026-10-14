"""
Unit tests for service layer
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.scoring_service import ScoringService
from app.services.analytics_service import AnalyticsService
from app.services.strategy_orchestrator import StrategyOrchestrator
from app.services.goal_service import GoalService
from app.services.costing_service import CostingService
from app.services.suggestion_service import SuggestionService


@pytest.mark.unit
class TestScoringService:
    """Test cases for ScoringService"""

    @pytest.fixture
    def scoring_service(self, test_db):
        """Create scoring service instance"""
        return ScoringService(test_db)

    @pytest.mark.asyncio
    async def test_calculate_business_health_score(self, scoring_service, sample_business_profile):
        """Test business health score calculation"""
        result = await scoring_service.calculate_business_health_score(sample_business_profile)
        
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100
        assert "sub_metrics" in result
        assert "financial_health" in result["sub_metrics"]
        assert "operational_efficiency" in result["sub_metrics"]

    @pytest.mark.asyncio
    async def test_calculate_growth_potential_score(self, scoring_service, sample_business_profile):
        """Test growth potential score calculation"""
        result = await scoring_service.calculate_growth_potential_score(sample_business_profile)
        
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100
        assert "sub_metrics" in result
        assert "market_opportunity" in result["sub_metrics"]
        assert "competitive_advantage" in result["sub_metrics"]

    @pytest.mark.asyncio
    async def test_calculate_financial_stability_score(self, scoring_service, sample_business_profile):
        """Test financial stability score calculation"""
        result = await scoring_service.calculate_financial_stability_score(sample_business_profile)
        
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100
        assert "sub_metrics" in result
        assert "revenue_stability" in result["sub_metrics"]
        assert "profitability" in result["sub_metrics"]

    @pytest.mark.asyncio
    async def test_calculate_all_scores(self, scoring_service, sample_business_profile, mock_redis_cache):
        """Test calculating all scores"""
        result = await scoring_service.calculate_all_scores(sample_business_profile, {})
        
        assert "business_health" in result
        assert "growth_potential" in result
        assert "financial_stability" in result
        assert "market_position" in result
        assert "operational_efficiency" in result
        assert "innovation_readiness" in result

    @pytest.mark.asyncio
    async def test_store_scores(self, scoring_service, sample_score_data):
        """Test storing scores in database"""
        record_ids = await scoring_service.store_scores("test-profile-1", sample_score_data)
        
        assert len(record_ids) == len(sample_score_data)
        assert all(isinstance(id, str) for id in record_ids)

    @pytest.mark.asyncio
    async def test_get_score_history(self, scoring_service):
        """Test retrieving score history"""
        history = await scoring_service.get_score_history("test-profile-1", "business_health", "90d")
        
        assert "score_type" in history
        assert "time_range" in history
        assert "historical_data" in history


@pytest.mark.unit
class TestAnalyticsService:
    """Test cases for AnalyticsService"""

    @pytest.fixture
    def analytics_service(self, test_db):
        """Create analytics service instance"""
        return AnalyticsService(test_db)

    @pytest.mark.asyncio
    async def test_collect_metrics(self, analytics_service, mock_redis_cache):
        """Test collecting metrics"""
        metrics = await analytics_service.collect_metrics(
            "test-profile-1",
            ["revenue", "customers", "conversion_rate"]
        )
        
        assert "revenue" in metrics
        assert "customers" in metrics
        assert "conversion_rate" in metrics

    @pytest.mark.asyncio
    async def test_analyze_trends(self, analytics_service):
        """Test trend analysis"""
        result = await analytics_service.analyze_trends(
            "test-profile-1",
            "revenue",
            "90d"
        )
        
        assert "metric" in result
        assert "time_range" in result
        assert "trend" in result
        assert "insights" in result

    @pytest.mark.asyncio
    async def test_get_dashboard_data(self, analytics_service):
        """Test getting dashboard data"""
        dashboard = await analytics_service.get_dashboard_data("test-profile-1", "30d")
        
        assert "metrics" in dashboard
        assert "trends" in dashboard
        assert "benchmarks" in dashboard

    @pytest.mark.asyncio
    async def test_get_benchmarks(self, analytics_service):
        """Test getting benchmarks"""
        benchmarks = await analytics_service.get_benchmarks("test-profile-1", "Technology")
        
        assert "industry" in benchmarks
        assert "benchmarks" in benchmarks
        assert "your_performance" in benchmarks


@pytest.mark.unit
class TestStrategyOrchestrator:
    """Test cases for StrategyOrchestrator"""

    @pytest.fixture
    def orchestrator(self, test_db):
        """Create orchestrator instance"""
        return StrategyOrchestrator(test_db)

    @pytest.mark.asyncio
    async def test_analyze_comprehensive(self, orchestrator, sample_analysis_request, mock_gemini_client):
        """Test comprehensive analysis"""
        result = await orchestrator.analyze_comprehensive(
            "test-profile-1",
            sample_analysis_request
        )
        
        assert "analysis_id" in result
        assert "results" in result
        assert "scores" in result
        assert "insights" in result

    @pytest.mark.asyncio
    async def test_execute_agents_parallel(self, orchestrator, sample_business_profile, mock_gemini_client):
        """Test parallel agent execution"""
        config = {
            "include_goals": True,
            "include_growth": True,
            "include_costing": True,
            "include_suggestions": True
        }
        
        results = await orchestrator._execute_agents_parallel(sample_business_profile, config)
        
        assert "goals" in results
        assert "growth" in results
        assert "costing" in results
        assert "suggestions" in results

    @pytest.mark.asyncio
    async def test_aggregate_results(self, orchestrator):
        """Test result aggregation"""
        results = {
            "goals": {"data": "goal data"},
            "growth": {"data": "growth data"},
            "costing": {"data": "costing data"},
            "suggestions": {"data": "suggestion data"}
        }
        
        aggregated = orchestrator._aggregate_results(results)
        
        assert "goals" in aggregated
        assert "growth" in aggregated
        assert "costing" in aggregated
        assert "suggestions" in aggregated


@pytest.mark.unit
class TestGoalService:
    """Test cases for GoalService"""

    @pytest.fixture
    def goal_service(self, test_db):
        """Create goal service instance"""
        return GoalService(test_db)

    @pytest.mark.asyncio
    async def test_create_goal(self, goal_service, sample_goal_data):
        """Test creating a goal"""
        goal = await goal_service.create_goal("test-profile-1", sample_goal_data)
        
        assert goal.id is not None
        assert goal.title == sample_goal_data["title"]
        assert goal.category == sample_goal_data["category"]

    @pytest.mark.asyncio
    async def test_get_goals(self, goal_service):
        """Test retrieving goals"""
        goals = await goal_service.get_goals("test-profile-1")
        
        assert isinstance(goals, list)

    @pytest.mark.asyncio
    async def test_update_goal(self, goal_service, sample_goal_data):
        """Test updating a goal"""
        goal = await goal_service.create_goal("test-profile-1", sample_goal_data)
        
        updated_data = {"title": "Updated Goal Title"}
        updated_goal = await goal_service.update_goal(goal.id, updated_data)
        
        assert updated_goal.title == "Updated Goal Title"

    @pytest.mark.asyncio
    async def test_delete_goal(self, goal_service, sample_goal_data):
        """Test deleting a goal"""
        goal = await goal_service.create_goal("test-profile-1", sample_goal_data)
        
        result = await goal_service.delete_goal(goal.id)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_smart_goal(self, goal_service):
        """Test SMART goal validation"""
        valid_goal = {
            "title": "Increase revenue to $75,000 by December 2024",
            "description": "Achieve specific revenue target",
            "deadline": "2024-12-31"
        }
        
        validation = await goal_service.validate_smart_goal(valid_goal)
        
        assert "is_valid" in validation
        assert "criteria" in validation


@pytest.mark.unit
class TestCostingService:
    """Test cases for CostingService"""

    @pytest.fixture
    def costing_service(self, test_db):
        """Create costing service instance"""
        return CostingService(test_db)

    @pytest.mark.asyncio
    async def test_analyze_cost_structure(self, costing_service, sample_costing_data):
        """Test cost structure analysis"""
        analysis = await costing_service.analyze_cost_structure(sample_costing_data)
        
        assert "fixed_costs" in analysis
        assert "variable_costs" in analysis
        assert "total_monthly_cost" in analysis
        assert "cost_per_unit" in analysis

    @pytest.mark.asyncio
    async def test_generate_pricing_strategies(self, costing_service, sample_costing_data):
        """Test pricing strategy generation"""
        strategies = await costing_service.generate_pricing_strategies(sample_costing_data)
        
        assert isinstance(strategies, list)
        assert len(strategies) > 0
        assert all("strategy" in s for s in strategies)
        assert all("recommended_price" in s for s in strategies)

    @pytest.mark.asyncio
    async def test_identify_optimization_opportunities(self, costing_service, sample_costing_data):
        """Test optimization opportunity identification"""
        opportunities = await costing_service.identify_optimization_opportunities(sample_costing_data)
        
        assert isinstance(opportunities, list)
        assert all("area" in o for o in opportunities)
        assert all("potential_savings" in o for o in opportunities)

    @pytest.mark.asyncio
    async def test_calculate_break_even(self, costing_service, sample_costing_data):
        """Test break-even calculation"""
        break_even = await costing_service.calculate_break_even(sample_costing_data)
        
        assert "break_even_units" in break_even
        assert "break_even_revenue" in break_even
        assert "margin_of_safety" in break_even


@pytest.mark.unit
class TestSuggestionService:
    """Test cases for SuggestionService"""

    @pytest.fixture
    def suggestion_service(self, test_db):
        """Create suggestion service instance"""
        return SuggestionService(test_db)

    @pytest.mark.asyncio
    async def test_generate_suggestions(self, suggestion_service, sample_suggestion_request, mock_gemini_client):
        """Test generating suggestions"""
        suggestions = await suggestion_service.generate_suggestions(sample_suggestion_request)
        
        assert "new_opportunities" in suggestions
        assert "partnership_opportunities" in suggestions
        assert "market_expansions" in suggestions

    @pytest.mark.asyncio
    async def test_score_opportunities(self, suggestion_service):
        """Test opportunity scoring"""
        opportunities = [
            {"title": "Opportunity 1", "feasibility": 0.8, "alignment": 0.9},
            {"title": "Opportunity 2", "feasibility": 0.6, "alignment": 0.7}
        ]
        
        scored = await suggestion_service.score_opportunities(opportunities)
        
        assert len(scored) == len(opportunities)
        assert all("overall_score" in o for o in scored)

    @pytest.mark.asyncio
    async def test_prioritize_suggestions(self, suggestion_service):
        """Test suggestion prioritization"""
        suggestions = [
            {"id": "1", "score": 0.85},
            {"id": "2", "score": 0.75},
            {"id": "3", "score": 0.90}
        ]
        
        prioritized = await suggestion_service.prioritize_suggestions(suggestions)
        
        assert prioritized[0]["id"] == "3"
        assert prioritized[1]["id"] == "1"
        assert prioritized[2]["id"] == "2"

    @pytest.mark.asyncio
    async def test_store_suggestion(self, suggestion_service):
        """Test storing suggestion"""
        suggestion_data = {
            "business_profile_id": "test-profile-1",
            "suggestion_type": "new_opportunity",
            "title": "Test Suggestion",
            "description": "Test description",
            "potential_value": 100000,
            "feasibility_score": 0.85
        }
        
        suggestion = await suggestion_service.store_suggestion(suggestion_data)
        
        assert suggestion.id is not None
        assert suggestion.title == "Test Suggestion"
