"""
Unit tests for agent layer
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.agents.goal_advisor_agent import GoalAdvisorAgent
from app.agents.growth_plan_advisor_agent import GrowthPlanAdvisorAgent
from app.agents.costing_advisor_agent import CostingAdvisorAgent
from app.agents.business_suggestion_agent import BusinessSuggestionAgent


@pytest.mark.unit
class TestGoalAdvisorAgent:
    """Test cases for GoalAdvisorAgent"""

    @pytest.fixture
    def goal_agent(self):
        """Create goal advisor agent instance"""
        return GoalAdvisorAgent()

    @pytest.mark.asyncio
    async def test_invoke_success(self, goal_agent, mock_gemini_client):
        """Test successful agent invocation"""
        mock_gemini_client.return_value.generate_content_async.return_value = MagicMock(
            text='{"success": true, "goals": [{"id": "goal-1", "title": "Test Goal"}]}'
        )
        
        result = await goal_agent.invoke({
            "bmc_data": {"valuePropositions": ["Test"]},
            "business_context": "Test context"
        })
        
        assert result["success"] is True
        assert "goals" in result

    @pytest.mark.asyncio
    async def test_invoke_with_goals(self, goal_agent, mock_gemini_client):
        """Test agent invocation with existing goals"""
        mock_gemini_client.return_value.generate_content_async.return_value = MagicMock(
            text='{"success": true, "goals": [{"id": "goal-2", "title": "New Goal"}]}'
        )
        
        result = await goal_agent.invoke({
            "bmc_data": {"valuePropositions": ["Test"]},
            "existing_goals": [{"id": "goal-1", "title": "Existing Goal"}]
        })
        
        assert result["success"] is True
        assert "goals" in result

    @pytest.mark.asyncio
    async def test_validate_smart_criteria(self, goal_agent):
        """Test SMART criteria validation"""
        goal = {
            "title": "Increase revenue to $75,000 by December 2024",
            "description": "Achieve specific revenue target",
            "deadline": "2024-12-31"
        }
        
        validation = goal_agent.validate_smart_criteria(goal)
        
        assert "is_smart" in validation
        assert "criteria" in validation
        assert "specific" in validation["criteria"]
        assert "measurable" in validation["criteria"]
        assert "achievable" in validation["criteria"]
        assert "relevant" in validation["criteria"]
        assert "time_bound" in validation["criteria"]

    @pytest.mark.asyncio
    async def test_analyze_bmc_alignment(self, goal_agent):
        """Test BMC alignment analysis"""
        goal = {
            "title": "Increase revenue",
            "category": "financial"
        }
        
        bmc_data = {
            "revenueStreams": ["Subscription", "Consulting"],
            "customerSegments": ["Small businesses"]
        }
        
        alignment = goal_agent.analyze_bmc_alignment(goal, bmc_data)
        
        assert "alignment_score" in alignment
        assert "aligned_blocks" in alignment
        assert "gaps" in alignment

    @pytest.mark.asyncio
    async def test_generate_milestones(self, goal_agent):
        """Test milestone generation"""
        goal = {
            "title": "Increase revenue to $75,000",
            "target_value": 75000,
            "current_value": 50000,
            "deadline": "2024-12-31"
        }
        
        milestones = goal_agent.generate_milestones(goal)
        
        assert isinstance(milestones, list)
        assert len(milestones) > 0
        assert all("milestone" in m for m in milestones)
        assert all("target_date" in m for m in milestones)

    @pytest.mark.asyncio
    async def test_invoke_error_handling(self, goal_agent, mock_gemini_client):
        """Test error handling in agent invocation"""
        mock_gemini_client.return_value.generate_content_async.side_effect = Exception("AI Error")
        
        result = await goal_agent.invoke({
            "bmc_data": {"valuePropositions": ["Test"]}
        })
        
        assert result["success"] is False
        assert "error" in result


@pytest.mark.unit
class TestGrowthPlanAdvisorAgent:
    """Test cases for GrowthPlanAdvisorAgent"""

    @pytest.fixture
    def growth_agent(self):
        """Create growth plan advisor agent instance"""
        return GrowthPlanAdvisorAgent()

    @pytest.mark.asyncio
    async def test_invoke_success(self, growth_agent, mock_gemini_client):
        """Test successful agent invocation"""
        mock_gemini_client.return_value.generate_content_async.return_value = MagicMock(
            text='{"success": true, "growth_plan": {"plan_id": "gp-1", "title": "Test Plan"}}'
        )
        
        result = await growth_agent.invoke({
            "bmc_data": {"valuePropositions": ["Test"]},
            "market_analysis": {"market_size": 1000000}
        })
        
        assert result["success"] is True
        assert "growth_plan" in result

    @pytest.mark.asyncio
    async def test_identify_opportunities(self, growth_agent):
        """Test opportunity identification"""
        bmc_data = {
            "valuePropositions": ["Innovative solutions"],
            "customerSegments": ["Small businesses"],
            "channels": ["Online"]
        }
        
        opportunities = growth_agent.identify_opportunities(bmc_data)
        
        assert isinstance(opportunities, list)
        assert all("title" in o for o in opportunities)
        assert all("type" in o for o in opportunities)

    @pytest.mark.asyncio
    async def test_generate_roadmap(self, growth_agent):
        """Test roadmap generation"""
        opportunities = [
            {"title": "Market Expansion", "priority": "high", "time_to_market": "3 months"}
        ]
        
        roadmap = growth_agent.generate_roadmap(opportunities, "6 months")
        
        assert isinstance(roadmap, list)
        assert all("phase" in r for r in roadmap)
        assert all("duration" in r for r in roadmap)
        assert all("objectives" in r for r in roadmap)

    @pytest.mark.asyncio
    async def test_prioritize_channels(self, growth_agent):
        """Test channel prioritization"""
        channels = [
            {"channel": "digital_marketing", "expected_impact": "40%", "cost": 20000},
            {"channel": "content_marketing", "expected_impact": "25%", "cost": 10000}
        ]
        
        prioritized = growth_agent.prioritize_channels(channels)
        
        assert len(prioritized) == len(channels)
        assert prioritized[0]["channel"] == "digital_marketing"

    @pytest.mark.asyncio
    async def test_assess_risks(self, growth_agent):
        """Test risk assessment"""
        opportunities = [
            {"title": "Market Expansion", "risks": ["regulatory", "cultural"]}
        ]
        
        risk_assessment = growth_agent.assess_risks(opportunities)
        
        assert "high_risks" in risk_assessment
        assert "medium_risks" in risk_assessment
        assert "low_risks" in risk_assessment


@pytest.mark.unit
class TestCostingAdvisorAgent:
    """Test cases for CostingAdvisorAgent"""

    @pytest.fixture
    def costing_agent(self):
        """Create costing advisor agent instance"""
        return CostingAdvisorAgent()

    @pytest.mark.asyncio
    async def test_invoke_success(self, costing_agent, mock_gemini_client):
        """Test successful agent invocation"""
        mock_gemini_client.return_value.generate_content_async.return_value = MagicMock(
            text='{"success": true, "costing_analysis": {"total_monthly_cost": 40000}}'
        )
        
        result = await costing_agent.invoke({
            "bmc_data": {"costStructure": ["Salaries", "Infrastructure"]},
            "financial_data": {"monthly_revenue": 50000}
        })
        
        assert result["success"] is True
        assert "costing_analysis" in result

    @pytest.mark.asyncio
    async def test_analyze_cost_structure(self, costing_agent):
        """Test cost structure analysis"""
        cost_data = {
            "fixed_costs": {"rent": 8000, "salaries": 15000},
            "variable_costs": {"materials": 8000, "shipping": 4000}
        }
        
        analysis = costing_agent.analyze_cost_structure(cost_data)
        
        assert "fixed_costs" in analysis
        assert "variable_costs" in analysis
        assert "total_monthly_cost" in analysis
        assert "cost_per_unit" in analysis

    @pytest.mark.asyncio
    async def test_generate_pricing_strategies(self, costing_agent):
        """Test pricing strategy generation"""
        cost_data = {
            "total_monthly_cost": 40000,
            "units_sold": 2000,
            "cost_per_unit": 20
        }
        
        strategies = costing_agent.generate_pricing_strategies(cost_data)
        
        assert isinstance(strategies, list)
        assert len(strategies) > 0
        assert all("strategy" in s for s in strategies)
        assert all("recommended_price" in s for s in strategies)

    @pytest.mark.asyncio
    async def test_identify_optimization_opportunities(self, costing_agent):
        """Test optimization opportunity identification"""
        cost_data = {
            "fixed_costs": {"rent": 8000, "salaries": 15000},
            "variable_costs": {"materials": 8000, "shipping": 4000}
        }
        
        opportunities = costing_agent.identify_optimization_opportunities(cost_data)
        
        assert isinstance(opportunities, list)
        assert all("area" in o for o in opportunities)
        assert all("potential_savings" in o for o in opportunities)

    @pytest.mark.asyncio
    async def test_calculate_break_even(self, costing_agent):
        """Test break-even calculation"""
        cost_data = {
            "total_monthly_cost": 40000,
            "current_price": 40,
            "cost_per_unit": 20
        }
        
        break_even = costing_agent.calculate_break_even(cost_data)
        
        assert "break_even_units" in break_even
        assert "break_even_revenue" in break_even
        assert "margin_of_safety" in break_even
        assert "sensitivity_analysis" in break_even


@pytest.mark.unit
class TestBusinessSuggestionAgent:
    """Test cases for BusinessSuggestionAgent"""

    @pytest.fixture
    def suggestion_agent(self):
        """Create business suggestion agent instance"""
        return BusinessSuggestionAgent()

    @pytest.mark.asyncio
    async def test_invoke_success(self, suggestion_agent, mock_gemini_client):
        """Test successful agent invocation"""
        mock_gemini_client.return_value.generate_content_async.return_value = MagicMock(
            text='{"success": true, "business_suggestions": {"new_opportunities": [{"id": "opp-1"}]}}'
        )
        
        result = await suggestion_agent.invoke({
            "bmc_data": {"valuePropositions": ["Test"]},
            "market_analysis": {"trends": ["AI", "Automation"]}
        })
        
        assert result["success"] is True
        assert "business_suggestions" in result

    @pytest.mark.asyncio
    async def test_identify_new_opportunities(self, suggestion_agent):
        """Test new opportunity identification"""
        bmc_data = {
            "valuePropositions": ["Innovative solutions"],
            "customerSegments": ["Small businesses"],
            "keyResources": ["Technology", "Team"]
        }
        
        opportunities = suggestion_agent.identify_new_opportunities(bmc_data)
        
        assert isinstance(opportunities, list)
        assert all("title" in o for o in opportunities)
        assert all("type" in o for o in opportunities)

    @pytest.mark.asyncio
    async def test_identify_partnership_opportunities(self, suggestion_agent):
        """Test partnership opportunity identification"""
        bmc_data = {
            "keyPartners": ["Cloud providers"],
            "channels": ["Online", "Direct sales"]
        }
        
        partnerships = suggestion_agent.identify_partnership_opportunities(bmc_data)
        
        assert isinstance(partnerships, list)
        assert all("title" in p for p in partnerships)
        assert all("partner_type" in p for p in partnerships)

    @pytest.mark.asyncio
    async def test_identify_market_expansions(self, suggestion_agent):
        """Test market expansion identification"""
        bmc_data = {
            "customerSegments": ["Small businesses"],
            "channels": ["Online"]
        }
        
        expansions = suggestion_agent.identify_market_expansions(bmc_data)
        
        assert isinstance(expansions, list)
        assert all("title" in e for e in expansions)
        assert all("target_market" in e for e in expansions)

    @pytest.mark.asyncio
    async def test_score_opportunities(self, suggestion_agent):
        """Test opportunity scoring"""
        opportunities = [
            {
                "title": "B2B Subscription",
                "feasibility": 0.85,
                "alignment": 0.90,
                "potential_revenue": 200000
            }
        ]
        
        scored = suggestion_agent.score_opportunities(opportunities)
        
        assert len(scored) == len(opportunities)
        assert all("overall_score" in o for o in scored)

    @pytest.mark.asyncio
    async def test_prioritize_suggestions(self, suggestion_agent):
        """Test suggestion prioritization"""
        suggestions = [
            {"id": "1", "score": 0.85, "expected_value": 200000},
            {"id": "2", "score": 0.75, "expected_value": 100000},
            {"id": "3", "score": 0.90, "expected_value": 300000}
        ]
        
        prioritized = suggestion_agent.prioritize_suggestions(suggestions)
        
        assert prioritized[0]["id"] == "3"
        assert prioritized[1]["id"] == "1"
        assert prioritized[2]["id"] == "2"

    @pytest.mark.asyncio
    async def test_invoke_with_suggestion_types(self, suggestion_agent, mock_gemini_client):
        """Test agent invocation with specific suggestion types"""
        mock_gemini_client.return_value.generate_content_async.return_value = MagicMock(
            text='{"success": true, "business_suggestions": {"new_opportunities": []}}'
        )
        
        result = await suggestion_agent.invoke({
            "bmc_data": {"valuePropositions": ["Test"]},
            "suggestion_types": ["new_opportunities"]
        })
        
        assert result["success"] is True
        assert "business_suggestions" in result


@pytest.mark.unit
class TestAgentFallbackBehavior:
    """Test cases for agent fallback behavior"""

    @pytest.mark.asyncio
    async def test_goal_agent_fallback(self, mock_gemini_client):
        """Test goal agent fallback when AI fails"""
        agent = GoalAdvisorAgent()
        mock_gemini_client.return_value.generate_content_async.side_effect = Exception("AI Error")
        
        result = await agent.invoke({"bmc_data": {"valuePropositions": ["Test"]}})
        
        assert result["success"] is False
        assert "error" in result
        assert "fallback" in result

    @pytest.mark.asyncio
    async def test_growth_agent_fallback(self, mock_gemini_client):
        """Test growth agent fallback when AI fails"""
        agent = GrowthPlanAdvisorAgent()
        mock_gemini_client.return_value.generate_content_async.side_effect = Exception("AI Error")
        
        result = await agent.invoke({"bmc_data": {"valuePropositions": ["Test"]}})
        
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_costing_agent_fallback(self, mock_gemini_client):
        """Test costing agent fallback when AI fails"""
        agent = CostingAdvisorAgent()
        mock_gemini_client.return_value.generate_content_async.side_effect = Exception("AI Error")
        
        result = await agent.invoke({"bmc_data": {"costStructure": ["Test"]}})
        
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_suggestion_agent_fallback(self, mock_gemini_client):
        """Test suggestion agent fallback when AI fails"""
        agent = BusinessSuggestionAgent()
        mock_gemini_client.return_value.generate_content_async.side_effect = Exception("AI Error")
        
        result = await agent.invoke({"bmc_data": {"valuePropositions": ["Test"]}})
        
        assert result["success"] is False
        assert "error" in result
