"""
Unit tests for utility functions
"""
import pytest
from datetime import datetime, timedelta

from app.utils.scoring_calculators import (
    BusinessHealthCalculator,
    GrowthPotentialCalculator,
    FinancialStabilityCalculator,
    MarketPositionCalculator,
    OperationalEfficiencyCalculator,
    InnovationReadinessCalculator
)
from app.utils.trend_analysis import TrendAnalyzer
from app.utils.conflict_resolution import ConflictResolver
from app.utils.decision_tree import DecisionTree
from app.utils.agent_communication import AgentCommunicator


@pytest.mark.unit
class TestScoringCalculators:
    """Test cases for scoring calculators"""

    @pytest.mark.asyncio
    async def test_business_health_calculator(self):
        """Test business health score calculation"""
        calculator = BusinessHealthCalculator()
        
        profile = {
            "financial_data": {
                "monthly_revenue": 50000,
                "profit_margin": 0.30,
                "cash_flow": 15000
            },
            "operational_data": {
                "efficiency_score": 0.75,
                "resource_utilization": 0.80
            },
            "customer_data": {
                "satisfaction_score": 0.85,
                "retention_rate": 0.90
            },
            "market_data": {
                "market_share": 0.15,
                "brand_strength": 0.80
            },
            "innovation_data": {
                "rd_investment": 0.10,
                "innovation_culture": 0.75
            }
        }
        
        result = await calculator.calculate(profile, {})
        
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100
        assert "sub_metrics" in result
        assert "financial_health" in result["sub_metrics"]
        assert "operational_efficiency" in result["sub_metrics"]
        assert "customer_satisfaction" in result["sub_metrics"]
        assert "market_position" in result["sub_metrics"]
        assert "innovation_readiness" in result["sub_metrics"]

    @pytest.mark.asyncio
    async def test_growth_potential_calculator(self):
        """Test growth potential score calculation"""
        calculator = GrowthPotentialCalculator()
        
        profile = {
            "market_data": {
                "market_size": 10000000,
                "growth_rate": 0.15,
                "accessibility": 0.80
            },
            "competitive_data": {
                "differentiation": 0.85,
                "barriers_to_entry": 0.70
            },
            "execution_data": {
                "team_capability": 0.80,
                "resources": 0.75,
                "processes": 0.85
            },
            "financial_data": {
                "funding": 100000,
                "runway": 12,
                "investment_readiness": 0.80
            },
            "innovation_data": {
                "rd_investment": 0.10,
                "technology": 0.85,
                "adaptability": 0.80
            }
        }
        
        result = await calculator.calculate(profile, {})
        
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100
        assert "sub_metrics" in result
        assert "market_opportunity" in result["sub_metrics"]
        assert "competitive_advantage" in result["sub_metrics"]
        assert "execution_capability" in result["sub_metrics"]
        assert "financial_capacity" in result["sub_metrics"]
        assert "innovation_potential" in result["sub_metrics"]

    @pytest.mark.asyncio
    async def test_financial_stability_calculator(self):
        """Test financial stability score calculation"""
        calculator = FinancialStabilityCalculator()
        
        profile = {
            "revenue_data": {
                "monthly_revenue": 50000,
                "revenue_variance": 0.10,
                "predictability": 0.85
            },
            "profitability_data": {
                "gross_margin": 0.60,
                "net_margin": 0.25,
                "margin_trend": "up"
            },
            "cash_flow_data": {
                "cash_position": 100000,
                "burn_rate": 35000,
                "cash_flow_health": 0.80
            },
            "debt_data": {
                "debt_ratio": 0.30,
                "leverage": 0.40,
                "debt_service": 0.20
            },
            "funding_data": {
                "access_to_capital": 0.80,
                "investor_interest": 0.75,
                "funding_readiness": 0.85
            }
        }
        
        result = await calculator.calculate(profile, {})
        
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100
        assert "sub_metrics" in result
        assert "revenue_stability" in result["sub_metrics"]
        assert "profitability" in result["sub_metrics"]
        assert "cash_flow_health" in result["sub_metrics"]
        assert "debt_management" in result["sub_metrics"]
        assert "funding_readiness" in result["sub_metrics"]

    @pytest.mark.asyncio
    async def test_market_position_calculator(self):
        """Test market position score calculation"""
        calculator = MarketPositionCalculator()
        
        profile = {
            "market_share_data": {
                "current_share": 0.15,
                "growth_rate": 0.05,
                "penetration": 0.20
            },
            "brand_data": {
                "awareness": 0.75,
                "reputation": 0.85,
                "loyalty": 0.80
            },
            "positioning_data": {
                "differentiation": 0.80,
                "value_proposition": 0.85,
                "competitive_positioning": 0.75
            },
            "customer_data": {
                "retention": 0.90,
                "advocacy": 0.75,
                "satisfaction": 0.85
            },
            "influence_data": {
                "thought_leadership": 0.70,
                "industry_impact": 0.65,
                "influence_score": 0.68
            }
        }
        
        result = await calculator.calculate(profile, {})
        
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100
        assert "sub_metrics" in result
        assert "market_share" in result["sub_metrics"]
        assert "brand_strength" in result["sub_metrics"]
        assert "competitive_positioning" in result["sub_metrics"]
        assert "customer_loyalty" in result["sub_metrics"]
        assert "market_influence" in result["sub_metrics"]

    @pytest.mark.asyncio
    async def test_operational_efficiency_calculator(self):
        """Test operational efficiency score calculation"""
        calculator = OperationalEfficiencyCalculator()
        
        profile = {
            "process_data": {
                "workflow_optimization": 0.80,
                "automation_level": 0.75,
                "cycle_time": 0.85
            },
            "resource_data": {
                "asset_efficiency": 0.80,
                "team_productivity": 0.85,
                "utilization": 0.75
            },
            "cost_data": {
                "cost_control": 0.80,
                "optimization": 0.75,
                "cost_efficiency": 0.78
            },
            "quality_data": {
                "error_rate": 0.05,
                "customer_satisfaction": 0.85,
                "quality_score": 0.80
            },
            "scalability_data": {
                "ability_to_scale": 0.80,
                "infrastructure": 0.75,
                "scalability_score": 0.78
            }
        }
        
        result = await calculator.calculate(profile, {})
        
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100
        assert "sub_metrics" in result
        assert "process_efficiency" in result["sub_metrics"]
        assert "resource_utilization" in result["sub_metrics"]
        assert "cost_management" in result["sub_metrics"]
        assert "quality_metrics" in result["sub_metrics"]
        assert "scalability" in result["sub_metrics"]

    @pytest.mark.asyncio
    async def test_innovation_readiness_calculator(self):
        """Test innovation readiness score calculation"""
        calculator = InnovationReadinessCalculator()
        
        profile = {
            "rd_data": {
                "investment": 0.10,
                "budget_allocation": 0.15,
                "investment_score": 0.80
            },
            "culture_data": {
                "mindset": 0.85,
                "experimentation": 0.80,
                "culture_score": 0.83
            },
            "technology_data": {
                "adoption": 0.80,
                "modernization": 0.75,
                "tech_score": 0.78
            },
            "idea_data": {
                "generation_rate": 0.85,
                "flow": 0.80,
                "idea_score": 0.83
            },
            "success_data": {
                "conversion_rate": 0.75,
                "time_to_market": 0.80,
                "success_score": 0.78
            }
        }
        
        result = await calculator.calculate(profile, {})
        
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100
        assert "sub_metrics" in result
        assert "rd_investment" in result["sub_metrics"]
        assert "innovation_culture" in result["sub_metrics"]
        assert "technology_adoption" in result["sub_metrics"]
        assert "idea_generation" in result["sub_metrics"]
        assert "innovation_success_rate" in result["sub_metrics"]


@pytest.mark.unit
class TestTrendAnalyzer:
    """Test cases for trend analysis"""

    @pytest.fixture
    def trend_analyzer(self):
        """Create trend analyzer instance"""
        return TrendAnalyzer()

    def test_calculate_trend(self, trend_analyzer):
        """Test trend calculation"""
        data = [
            {"date": "2024-01", "value": 40000},
            {"date": "2024-02", "value": 42000},
            {"date": "2024-03", "value": 45000},
            {"date": "2024-04", "value": 50000}
        ]
        
        trend = trend_analyzer.calculate_trend(data)
        
        assert "direction" in trend
        assert "rate" in trend
        assert "confidence" in trend
        assert trend["direction"] in ["up", "down", "stable"]

    def test_detect_anomalies(self, trend_analyzer):
        """Test anomaly detection"""
        data = [
            {"date": "2024-01", "value": 40000},
            {"date": "2024-02", "value": 42000},
            {"date": "2024-03", "value": 45000},
            {"date": "2024-04", "value": 100000},  # Anomaly
            {"date": "2024-05", "value": 48000}
        ]
        
        anomalies = trend_analyzer.detect_anomalies(data)
        
        assert isinstance(anomalies, list)
        assert len(anomalies) > 0
        assert all("date" in a for a in anomalies)
        assert all("value" in a for a in anomalies)

    def test_forecast(self, trend_analyzer):
        """Test forecasting"""
        data = [
            {"date": "2024-01", "value": 40000},
            {"date": "2024-02", "value": 42000},
            {"date": "2024-03", "value": 45000},
            {"date": "2024-04", "value": 50000}
        ]
        
        forecast = trend_analyzer.forecast(data, periods=3)
        
        assert isinstance(forecast, list)
        assert len(forecast) == 3
        assert all("date" in f for f in forecast)
        assert all("predicted_value" in f for f in forecast)

    def test_calculate_moving_average(self, trend_analyzer):
        """Test moving average calculation"""
        data = [40000, 42000, 45000, 50000, 48000]
        
        ma = trend_analyzer.calculate_moving_average(data, window=3)
        
        assert len(ma) == len(data) - 2
        assert all(isinstance(v, (int, float)) for v in ma)

    def test_calculate_growth_rate(self, trend_analyzer):
        """Test growth rate calculation"""
        data = [
            {"date": "2024-01", "value": 40000},
            {"date": "2024-02", "value": 42000},
            {"date": "2024-03", "value": 45000}
        ]
        
        growth_rate = trend_analyzer.calculate_growth_rate(data)
        
        assert "rate" in growth_rate
        assert "period" in growth_rate
        assert isinstance(growth_rate["rate"], (int, float))


@pytest.mark.unit
class TestConflictResolver:
    """Test cases for conflict resolution"""

    @pytest.fixture
    def conflict_resolver(self):
        """Create conflict resolver instance"""
        return ConflictResolver()

    def test_resolve_score_conflicts(self, conflict_resolver):
        """Test score conflict resolution"""
        scores = {
            "agent1": {"business_health": 75},
            "agent2": {"business_health": 80},
            "agent3": {"business_health": 78}
        }
        
        resolved = conflict_resolver.resolve_score_conflicts(scores)
        
        assert "business_health" in resolved
        assert 0 <= resolved["business_health"] <= 100

    def test_resolve_recommendation_conflicts(self, conflict_resolver):
        """Test recommendation conflict resolution"""
        recommendations = {
            "agent1": ["Increase marketing", "Hire sales team"],
            "agent2": ["Increase marketing", "Improve product"],
            "agent3": ["Hire sales team", "Expand market"]
        }
        
        resolved = conflict_resolver.resolve_recommendation_conflicts(recommendations)
        
        assert isinstance(resolved, list)
        assert len(resolved) > 0

    def test_prioritize_conflicting_goals(self, conflict_resolver):
        """Test conflicting goal prioritization"""
        goals = [
            {"id": "1", "priority": "high", "alignment": 0.85},
            {"id": "2", "priority": "medium", "alignment": 0.90},
            {"id": "3", "priority": "high", "alignment": 0.75}
        ]
        
        prioritized = conflict_resolver.prioritize_conflicting_goals(goals)
        
        assert len(prioritized) == len(goals)
        assert prioritized[0]["id"] == "2"  # Highest alignment

    def test_merge_duplicate_suggestions(self, conflict_resolver):
        """Test duplicate suggestion merging"""
        suggestions = [
            {"title": "Increase marketing", "source": "agent1"},
            {"title": "Increase marketing", "source": "agent2"},
            {"title": "Hire sales team", "source": "agent1"}
        ]
        
        merged = conflict_resolver.merge_duplicate_suggestions(suggestions)
        
        assert len(merged) == 2
        assert all("sources" in s for s in merged)


@pytest.mark.unit
class TestDecisionTree:
    """Test cases for decision tree"""

    @pytest.fixture
    def decision_tree(self):
        """Create decision tree instance"""
        return DecisionTree()

    def test_select_agent(self, decision_tree):
        """Test agent selection"""
        request = {
            "type": "goal_setting",
            "has_bmc": True,
            "analysis_depth": "quick"
        }
        
        selected = decision_tree.select_agent(request)
        
        assert selected is not None
        assert "agent" in selected
        assert "reason" in selected

    def test_determine_execution_mode(self, decision_tree):
        """Test execution mode determination"""
        request = {
            "analysis_type": "comprehensive",
            "time_constraint": "none",
            "resource_availability": "high"
        }
        
        mode = decision_tree.determine_execution_mode(request)
        
        assert mode in ["parallel", "sequential", "hybrid"]

    def test_route_request(self, decision_tree):
        """Test request routing"""
        request = {
            "type": "cost_analysis",
            "data": {"financial_data": {}}
        }
        
        route = decision_tree.route_request(request)
        
        assert "endpoint" in route
        assert "method" in route
        assert "parameters" in route

    def test_evaluate_conditions(self, decision_tree):
        """Test condition evaluation"""
        conditions = {
            "has_bmc": True,
            "has_goals": False,
            "has_financial_data": True
        }
        
        result = decision_tree.evaluate_conditions(conditions)
        
        assert isinstance(result, dict)
        assert all(k in result for k in conditions.keys())


@pytest.mark.unit
class TestAgentCommunicator:
    """Test cases for agent communication"""

    @pytest.fixture
    def communicator(self):
        """Create agent communicator instance"""
        return AgentCommunicator()

    def test_create_message(self, communicator):
        """Test message creation"""
        message = communicator.create_message(
            sender="agent1",
            receiver="agent2",
            message_type="request",
            content={"data": "test"}
        )
        
        assert "id" in message
        assert "sender" in message
        assert "receiver" in message
        assert "type" in message
        assert "content" in message
        assert "timestamp" in message

    def test_send_message(self, communicator):
        """Test message sending"""
        message = communicator.create_message(
            sender="agent1",
            receiver="agent2",
            message_type="request",
            content={"data": "test"}
        )
        
        result = communicator.send_message(message)
        
        assert result is True

    def test_receive_message(self, communicator):
        """Test message receiving"""
        message = communicator.create_message(
            sender="agent1",
            receiver="agent2",
            message_type="request",
            content={"data": "test"}
        )
        
        communicator.send_message(message)
        received = communicator.receive_message("agent2")
        
        assert received is not None
        assert received["sender"] == "agent1"

    def test_broadcast_message(self, communicator):
        """Test message broadcasting"""
        message = communicator.create_message(
            sender="agent1",
            receiver="all",
            message_type="broadcast",
            content={"data": "test"}
        )
        
        result = communicator.broadcast_message(message, ["agent2", "agent3", "agent4"])
        
        assert result is True

    def test_get_message_history(self, communicator):
        """Test message history retrieval"""
        message = communicator.create_message(
            sender="agent1",
            receiver="agent2",
            message_type="request",
            content={"data": "test"}
        )
        
        communicator.send_message(message)
        history = communicator.get_message_history("agent1", "agent2")
        
        assert isinstance(history, list)
        assert len(history) > 0
