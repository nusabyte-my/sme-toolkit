"""
Integration tests for orchestration system
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio


@pytest.mark.integration
class TestAgentCoordination:
    """Integration tests for agent coordination"""

    @pytest.mark.asyncio
    async def test_parallel_agent_execution(self, test_db, mock_gemini_client):
        """Test parallel execution of multiple agents"""
        from app.services.strategy_orchestrator import StrategyOrchestrator
        
        orchestrator = StrategyOrchestrator(test_db)
        
        # Mock agent responses
        mock_gemini_client.return_value.generate_content_async.return_value = MagicMock(
            text='{"success": true, "data": {"result": "test"}}'
        )
        
        profile = {
            "id": "test-profile-1",
            "bmc_data": {"valuePropositions": ["Test"]},
            "financial_data": {"monthly_revenue": 50000}
        }
        
        config = {
            "include_goals": True,
            "include_growth": True,
            "include_costing": True,
            "include_suggestions": True
        }
        
        # Execute agents in parallel
        results = await orchestrator._execute_agents_parallel(profile, config)
        
        assert "goals" in results
        assert "growth" in results
        assert "costing" in results
        assert "suggestions" in results

    @pytest.mark.asyncio
    async def test_sequential_agent_execution(self, test_db, mock_gemini_client):
        """Test sequential execution of multiple agents"""
        from app.services.strategy_orchestrator import StrategyOrchestrator
        
        orchestrator = StrategyOrchestrator(test_db)
        
        # Mock agent responses
        mock_gemini_client.return_value.generate_content_async.return_value = MagicMock(
            text='{"success": true, "data": {"result": "test"}}'
        )
        
        profile = {
            "id": "test-profile-1",
            "bmc_data": {"valuePropositions": ["Test"]},
            "financial_data": {"monthly_revenue": 50000}
        }
        
        config = {
            "include_goals": True,
            "include_growth": True,
            "include_costing": True,
            "include_suggestions": True
        }
        
        # Execute agents sequentially
        results = await orchestrator._execute_agents_sequential(profile, config)
        
        assert "goals" in results
        assert "growth" in results
        assert "costing" in results
        assert "suggestions" in results

    @pytest.mark.asyncio
    async def test_result_aggregation(self, test_db):
        """Test result aggregation from multiple agents"""
        from app.services.strategy_orchestrator import StrategyOrchestrator
        
        orchestrator = StrategyOrchestrator(test_db)
        
        results = {
            "goals": {
                "success": True,
                "goals": [
                    {"id": "goal-1", "title": "Increase Revenue"},
                    {"id": "goal-2", "title": "Improve Efficiency"}
                ]
            },
            "growth": {
                "success": True,
                "growth_plan": {
                    "opportunities": [
                        {"title": "Market Expansion", "confidence": 0.85}
                    ]
                }
            },
            "costing": {
                "success": True,
                "costing_analysis": {
                    "total_monthly_cost": 40000,
                    "optimization_opportunities": []
                }
            },
            "suggestions": {
                "success": True,
                "business_suggestions": {
                    "new_opportunities": [
                        {"title": "B2B Service", "feasibility": 0.90}
                    ]
                }
            }
        }
        
        aggregated = orchestrator._aggregate_results(results)
        
        assert "goals" in aggregated
        assert "growth" in aggregated
        assert "costing" in aggregated
        assert "suggestions" in aggregated
        assert "summary" in aggregated

    @pytest.mark.asyncio
    async def test_conflict_resolution(self, test_db):
        """Test conflict resolution between agent results"""
        from app.services.strategy_orchestrator import StrategyOrchestrator
        
        orchestrator = StrategyOrchestrator(test_db)
        
        results = {
            "goals": {"recommendations": ["Increase marketing", "Hire sales team"]},
            "growth": {"recommendations": ["Increase marketing", "Expand market"]},
            "costing": {"recommendations": ["Reduce costs", "Optimize operations"]},
            "suggestions": {"recommendations": ["Hire sales team", "Launch new product"]}
        }
        
        resolved = orchestrator._resolve_conflicts(results)
        
        assert "recommendations" in resolved
        assert isinstance(resolved["recommendations"], list)
        # Check for deduplication
        assert len(resolved["recommendations"]) <= sum(
            len(r["recommendations"]) for r in results.values()
        )


@pytest.mark.integration
class TestOrchestrationPerformance:
    """Integration tests for orchestration performance"""

    @pytest.mark.asyncio
    async def test_parallel_vs_sequential_performance(self, test_db, mock_gemini_client):
        """Test parallel vs sequential execution performance"""
        from app.services.strategy_orchestrator import StrategyOrchestrator
        import time
        
        orchestrator = StrategyOrchestrator(test_db)
        
        # Mock agent responses
        mock_gemini_client.return_value.generate_content_async.return_value = MagicMock(
            text='{"success": true, "data": {"result": "test"}}'
        )
        
        profile = {
            "id": "test-profile-1",
            "bmc_data": {"valuePropositions": ["Test"]},
            "financial_data": {"monthly_revenue": 50000}
        }
        
        config = {
            "include_goals": True,
            "include_growth": True,
            "include_costing": True,
            "include_suggestions": True
        }
        
        # Measure parallel execution
        start_parallel = time.time()
        await orchestrator._execute_agents_parallel(profile, config)
        parallel_time = time.time() - start_parallel
        
        # Measure sequential execution
        start_sequential = time.time()
        await orchestrator._execute_agents_sequential(profile, config)
        sequential_time = time.time() - start_sequential
        
        # Parallel should be faster
        assert parallel_time < sequential_time

    @pytest.mark.asyncio
    async def test_caching_performance(self, test_db, mock_redis_cache):
        """Test caching performance improvement"""
        from app.services.strategy_orchestrator import StrategyOrchestrator
        import time
        
        orchestrator = StrategyOrchestrator(test_db)
        
        profile = {
            "id": "test-profile-1",
            "bmc_data": {"valuePropositions": ["Test"]},
            "financial_data": {"monthly_revenue": 50000}
        }
        
        # First call (no cache)
        start_first = time.time()
        await orchestrator._load_profile("test-profile-1")
        first_time = time.time() - start_first
        
        # Second call (with cache)
        start_second = time.time()
        await orchestrator._load_profile("test-profile-1")
        second_time = time.time() - start_second
        
        # Cached call should be faster
        assert second_time <= first_time


@pytest.mark.integration
class TestOrchestrationErrorHandling:
    """Integration tests for orchestration error handling"""

    @pytest.mark.asyncio
    async def test_agent_failure_handling(self, test_db, mock_gemini_client):
        """Test handling of agent failures"""
        from app.services.strategy_orchestrator import StrategyOrchestrator
        
        orchestrator = StrategyOrchestrator(test_db)
        
        # Mock agent to fail
        mock_gemini_client.return_value.generate_content_async.side_effect = Exception("Agent Error")
        
        profile = {
            "id": "test-profile-1",
            "bmc_data": {"valuePropositions": ["Test"]},
            "financial_data": {"monthly_revenue": 50000}
        }
        
        config = {
            "include_goals": True,
            "include_growth": True,
            "include_costing": True,
            "include_suggestions": True
        }
        
        # Should handle failures gracefully
        results = await orchestrator._execute_agents_parallel(profile, config)
        
        # Some agents may fail, but orchestration should continue
        assert "goals" in results or "growth" in results

    @pytest.mark.asyncio
    async def test_partial_failure_recovery(self, test_db, mock_gemini_client):
        """Test recovery from partial failures"""
        from app.services.strategy_orchestrator import StrategyOrchestrator
        
        orchestrator = StrategyOrchestrator(test_db)
        
        # Mock some agents to fail
        call_count = 0
        
        async def mock_generate(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count in [2, 4]:  # Fail on 2nd and 4th call
                raise Exception("Agent Error")
            return MagicMock(text='{"success": true, "data": {"result": "test"}}')
        
        mock_gemini_client.return_value.generate_content_async = mock_generate
        
        profile = {
            "id": "test-profile-1",
            "bmc_data": {"valuePropositions": ["Test"]},
            "financial_data": {"monthly_revenue": 50000}
        }
        
        config = {
            "include_goals": True,
            "include_growth": True,
            "include_costing": True,
            "include_suggestions": True
        }
        
        # Should recover and return partial results
        results = await orchestrator._execute_agents_parallel(profile, config)
        
        # At least some agents should succeed
        successful_agents = [k for k, v in results.items() if v is not None]
        assert len(successful_agents) > 0

    @pytest.mark.asyncio
    async def test_timeout_handling(self, test_db, mock_gemini_client):
        """Test handling of agent timeouts"""
        from app.services.strategy_orchestrator import StrategyOrchestrator
        
        orchestrator = StrategyOrchestrator(test_db)
        
        # Mock agent to timeout
        async def mock_generate_timeout(*args, **kwargs):
            await asyncio.sleep(10)  # Simulate long-running agent
            return MagicMock(text='{"success": true, "data": {"result": "test"}}')
        
        mock_gemini_client.return_value.generate_content_async = mock_generate_timeout
        
        profile = {
            "id": "test-profile-1",
            "bmc_data": {"valuePropositions": ["Test"]},
            "financial_data": {"monthly_revenue": 50000}
        }
        
        config = {
            "include_goals": True,
            "include_growth": True,
            "include_costing": True,
            "include_suggestions": True
        }
        
        # Should handle timeout gracefully
        results = await orchestrator._execute_agents_parallel(profile, config, timeout=2)
        
        # Should return results or handle timeout
        assert isinstance(results, dict)


@pytest.mark.integration
class TestOrchestrationScenarios:
    """Integration tests for real-world orchestration scenarios"""

    @pytest.mark.asyncio
    async def test_comprehensive_analysis_scenario(self, test_db, mock_gemini_client):
        """Test comprehensive analysis scenario"""
        from app.services.strategy_orchestrator import StrategyOrchestrator
        
        orchestrator = StrategyOrchestrator(test_db)
        
        # Mock agent responses
        mock_gemini_client.return_value.generate_content_async.return_value = MagicMock(
            text='{"success": true, "data": {"result": "test"}}'
        )
        
        request = {
            "business_profile_id": "test-profile-1",
            "analysis_type": "comprehensive",
            "include_goals": True,
            "include_growth": True,
            "include_costing": True,
            "include_suggestions": True
        }
        
        result = await orchestrator.analyze_comprehensive("test-profile-1", request)
        
        assert "analysis_id" in result
        assert "results" in result
        assert "scores" in result
        assert "insights" in result

    @pytest.mark.asyncio
    async def test_quick_analysis_scenario(self, test_db, mock_gemini_client):
        """Test quick analysis scenario"""
        from app.services.strategy_orchestrator import StrategyOrchestrator
        
        orchestrator = StrategyOrchestrator(test_db)
        
        # Mock agent responses
        mock_gemini_client.return_value.generate_content_async.return_value = MagicMock(
            text='{"success": true, "data": {"result": "test"}}'
        )
        
        request = {
            "business_profile_id": "test-profile-1",
            "analysis_type": "quick",
            "include_goals": True,
            "include_growth": True,
            "include_costing": False,
            "include_suggestions": False
        }
        
        result = await orchestrator.analyze_comprehensive("test-profile-1", request)
        
        assert "analysis_id" in result
        assert "results" in result

    @pytest.mark.asyncio
    async def test_goal_focused_scenario(self, test_db, mock_gemini_client):
        """Test goal-focused analysis scenario"""
        from app.services.strategy_orchestrator import StrategyOrchestrator
        
        orchestrator = StrategyOrchestrator(test_db)
        
        # Mock agent responses
        mock_gemini_client.return_value.generate_content_async.return_value = MagicMock(
            text='{"success": true, "goals": [{"id": "goal-1", "title": "Test Goal"}]}'
        )
        
        request = {
            "business_profile_id": "test-profile-1",
            "analysis_type": "goal_focused",
            "include_goals": True,
            "include_growth": False,
            "include_costing": False,
            "include_suggestions": False
        }
        
        result = await orchestrator.analyze_comprehensive("test-profile-1", request)
        
        assert "analysis_id" in result
        assert "results" in result
        assert "goals" in result["results"]

    @pytest.mark.asyncio
    async def test_growth_focused_scenario(self, test_db, mock_gemini_client):
        """Test growth-focused analysis scenario"""
        from app.services.strategy_orchestrator import StrategyOrchestrator
        
        orchestrator = StrategyOrchestrator(test_db)
        
        # Mock agent responses
        mock_gemini_client.return_value.generate_content_async.return_value = MagicMock(
            text='{"success": true, "growth_plan": {"plan_id": "gp-1", "title": "Test Plan"}}'
        )
        
        request = {
            "business_profile_id": "test-profile-1",
            "analysis_type": "growth_focused",
            "include_goals": False,
            "include_growth": True,
            "include_costing": False,
            "include_suggestions": False
        }
        
        result = await orchestrator.analyze_comprehensive("test-profile-1", request)
        
        assert "analysis_id" in result
        assert "results" in result
        assert "growth" in result["results"]


@pytest.mark.integration
class TestOrchestrationDataFlow:
    """Integration tests for orchestration data flow"""

    @pytest.mark.asyncio
    async def test_data_sharing_between_agents(self, test_db, mock_gemini_client):
        """Test data sharing between agents"""
        from app.services.strategy_orchestrator import StrategyOrchestrator
        
        orchestrator = StrategyOrchestrator(test_db)
        
        # Mock agent responses with shared data
        mock_gemini_client.return_value.generate_content_async.return_value = MagicMock(
            text='{"success": true, "data": {"shared_insight": "test insight"}}'
        )
        
        profile = {
            "id": "test-profile-1",
            "bmc_data": {"valuePropositions": ["Test"]},
            "financial_data": {"monthly_revenue": 50000}
        }
        
        config = {
            "include_goals": True,
            "include_growth": True,
            "include_costing": True,
            "include_suggestions": True
        }
        
        results = await orchestrator._execute_agents_parallel(profile, config)
        
        # Agents should have access to shared data
        assert all(results.values())

    @pytest.mark.asyncio
    async def test_result_persistence(self, test_db, mock_gemini_client):
        """Test result persistence to database"""
        from app.services.strategy_orchestrator import StrategyOrchestrator
        from app.database import StrategyAnalysis
        from sqlalchemy import select
        
        orchestrator = StrategyOrchestrator(test_db)
        
        # Mock agent responses
        mock_gemini_client.return_value.generate_content_async.return_value = MagicMock(
            text='{"success": true, "data": {"result": "test"}}'
        )
        
        request = {
            "business_profile_id": "test-profile-1",
            "analysis_type": "comprehensive",
            "include_goals": True,
            "include_growth": True,
            "include_costing": True,
            "include_suggestions": True
        }
        
        result = await orchestrator.analyze_comprehensive("test-profile-1", request)
        
        # Verify persistence
        db_result = await test_db.execute(
            select(StrategyAnalysis).where(
                StrategyAnalysis.id == result["analysis_id"]
            )
        )
        analysis = db_result.scalar_one_or_none()
        
        assert analysis is not None
        assert analysis.business_profile_id == "test-profile-1"

    @pytest.mark.asyncio
    async def test_score_calculation_integration(self, test_db, mock_gemini_client):
        """Test score calculation integration with orchestration"""
        from app.services.strategy_orchestrator import StrategyOrchestrator
        
        orchestrator = StrategyOrchestrator(test_db)
        
        # Mock agent responses
        mock_gemini_client.return_value.generate_content_async.return_value = MagicMock(
            text='{"success": true, "data": {"result": "test"}}'
        )
        
        request = {
            "business_profile_id": "test-profile-1",
            "analysis_type": "comprehensive",
            "include_goals": True,
            "include_growth": True,
            "include_costing": True,
            "include_suggestions": True
        }
        
        result = await orchestrator.analyze_comprehensive("test-profile-1", request)
        
        # Scores should be calculated
        assert "scores" in result
        assert "business_health" in result["scores"]
        assert "growth_potential" in result["scores"]
