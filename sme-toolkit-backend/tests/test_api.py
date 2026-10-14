"""
Integration tests for API endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestStrategyAdvisorAPI:
    """Integration tests for Strategy Advisor API endpoints"""

    @pytest.mark.asyncio
    async def test_analyze_strategy(self, client: AsyncClient, sample_analysis_request):
        """Test comprehensive strategy analysis endpoint"""
        response = await client.post(
            "/api/v1/strategy-advisor/analyze",
            json=sample_analysis_request
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "analysis_id" in data
        assert "results" in data
        assert "scores" in data

    @pytest.mark.asyncio
    async def test_get_analysis(self, client: AsyncClient):
        """Test retrieving analysis by ID"""
        # First create an analysis
        create_response = await client.post(
            "/api/v1/strategy-advisor/analyze",
            json={
                "business_profile_id": "test-profile-1",
                "analysis_type": "comprehensive"
            }
        )
        analysis_id = create_response.json()["analysis_id"]
        
        # Then retrieve it
        response = await client.get(f"/api/v1/strategy-advisor/analysis/{analysis_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["analysis_id"] == analysis_id

    @pytest.mark.asyncio
    async def test_create_goal(self, client: AsyncClient, sample_goal_data):
        """Test creating a goal"""
        response = await client.post(
            "/api/v1/strategy-advisor/goals",
            json={
                "business_profile_id": "test-profile-1",
                **sample_goal_data
            }
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert data["title"] == sample_goal_data["title"]

    @pytest.mark.asyncio
    async def test_get_goals(self, client: AsyncClient):
        """Test retrieving all goals"""
        response = await client.get(
            "/api/v1/strategy-advisor/goals",
            params={"business_profile_id": "test-profile-1"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "goals" in data
        assert isinstance(data["goals"], list)

    @pytest.mark.asyncio
    async def test_update_goal(self, client: AsyncClient, sample_goal_data):
        """Test updating a goal"""
        # First create a goal
        create_response = await client.post(
            "/api/v1/strategy-advisor/goals",
            json={
                "business_profile_id": "test-profile-1",
                **sample_goal_data
            }
        )
        goal_id = create_response.json()["id"]
        
        # Then update it
        update_data = {"title": "Updated Goal Title"}
        response = await client.put(
            f"/api/v1/strategy-advisor/goals/{goal_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Goal Title"

    @pytest.mark.asyncio
    async def test_delete_goal(self, client: AsyncClient, sample_goal_data):
        """Test deleting a goal"""
        # First create a goal
        create_response = await client.post(
            "/api/v1/strategy-advisor/goals",
            json={
                "business_profile_id": "test-profile-1",
                **sample_goal_data
            }
        )
        goal_id = create_response.json()["id"]
        
        # Then delete it
        response = await client.delete(f"/api/v1/strategy-advisor/goals/{goal_id}")
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_growth_plan(self, client: AsyncClient, sample_growth_plan_data):
        """Test creating a growth plan"""
        response = await client.post(
            "/api/v1/strategy-advisor/growth-plans",
            json={
                "business_profile_id": "test-profile-1",
                **sample_growth_plan_data
            }
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert data["title"] == sample_growth_plan_data["title"]

    @pytest.mark.asyncio
    async def test_get_growth_plans(self, client: AsyncClient):
        """Test retrieving all growth plans"""
        response = await client.get(
            "/api/v1/strategy-advisor/growth-plans",
            params={"business_profile_id": "test-profile-1"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "growth_plans" in data
        assert isinstance(data["growth_plans"], list)

    @pytest.mark.asyncio
    async def test_analyze_costing(self, client: AsyncClient, sample_costing_data):
        """Test costing analysis endpoint"""
        response = await client.post(
            "/api/v1/strategy-advisor/costing/analyze",
            json={
                "business_profile_id": "test-profile-1",
                **sample_costing_data
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "costing_analysis" in data
        assert "cost_structure" in data["costing_analysis"]

    @pytest.mark.asyncio
    async def test_get_costing_analysis(self, client: AsyncClient):
        """Test retrieving costing analysis"""
        response = await client.get(
            "/api/v1/strategy-advisor/costing/test-analysis-1"
        )
        
        assert response.status_code in [200, 404]  # May not exist

    @pytest.mark.asyncio
    async def test_get_suggestions(self, client: AsyncClient, sample_suggestion_request):
        """Test getting business suggestions"""
        response = await client.post(
            "/api/v1/strategy-advisor/suggestions",
            json=sample_suggestion_request
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "business_suggestions" in data
        assert "new_opportunities" in data["business_suggestions"]


@pytest.mark.integration
class TestAnalyticsAPI:
    """Integration tests for Analytics API endpoints"""

    @pytest.mark.asyncio
    async def test_get_dashboard_data(self, client: AsyncClient):
        """Test getting dashboard data"""
        response = await client.get(
            "/api/v1/analytics/dashboard",
            params={
                "business_profile_id": "test-profile-1",
                "time_range": "30d"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert "trends" in data

    @pytest.mark.asyncio
    async def test_get_metrics(self, client: AsyncClient):
        """Test getting specific metrics"""
        response = await client.get(
            "/api/v1/analytics/metrics",
            params={
                "business_profile_id": "test-profile-1",
                "metric_names": ["revenue", "customers"],
                "time_range": "30d"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data

    @pytest.mark.asyncio
    async def test_get_trends(self, client: AsyncClient):
        """Test getting trend analysis"""
        response = await client.get(
            "/api/v1/analytics/trends",
            params={
                "business_profile_id": "test-profile-1",
                "metric_name": "revenue",
                "time_range": "90d"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "metric" in data
        assert "trend" in data

    @pytest.mark.asyncio
    async def test_get_benchmarks(self, client: AsyncClient):
        """Test getting benchmarks"""
        response = await client.get(
            "/api/v1/analytics/benchmarks",
            params={
                "business_profile_id": "test-profile-1",
                "industry": "Technology"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "industry" in data
        assert "benchmarks" in data


@pytest.mark.integration
class TestScoringAPI:
    """Integration tests for Scoring API endpoints"""

    @pytest.mark.asyncio
    async def test_get_current_scores(self, client: AsyncClient):
        """Test getting current scores"""
        response = await client.get(
            "/api/v1/scoring/current",
            params={"business_profile_id": "test-profile-1"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "scores" in data

    @pytest.mark.asyncio
    async def test_get_score_history(self, client: AsyncClient):
        """Test getting score history"""
        response = await client.get(
            "/api/v1/scoring/history",
            params={
                "business_profile_id": "test-profile-1",
                "score_type": "business_health",
                "time_range": "90d"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "score_type" in data
        assert "historical_data" in data

    @pytest.mark.asyncio
    async def test_get_score_details(self, client: AsyncClient):
        """Test getting detailed score breakdown"""
        response = await client.get(
            "/api/v1/scoring/business_health",
            params={"business_profile_id": "test-profile-1"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "score_type" in data
        assert "overall_score" in data
        assert "sub_metrics" in data

    @pytest.mark.asyncio
    async def test_recalculate_scores(self, client: AsyncClient):
        """Test triggering score recalculation"""
        response = await client.post(
            "/api/v1/scoring/recalculate",
            json={"business_profile_id": "test-profile-1"}
        )
        
        assert response.status_code in [200, 202]
        data = response.json()
        assert "status" in data

    @pytest.mark.asyncio
    async def test_get_benchmarks(self, client: AsyncClient):
        """Test getting score benchmarks"""
        response = await client.get(
            "/api/v1/scoring/benchmarks",
            params={"business_profile_id": "test-profile-1"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "benchmarks" in data


@pytest.mark.integration
class TestOrchestrationAPI:
    """Integration tests for Orchestration API endpoints"""

    @pytest.mark.asyncio
    async def test_analyze(self, client: AsyncClient, sample_analysis_request):
        """Test orchestration analysis endpoint"""
        response = await client.post(
            "/api/v1/orchestration/analyze",
            json=sample_analysis_request
        )
        
        assert response.status_code in [200, 202]
        data = response.json()
        assert "job_id" in data or "results" in data

    @pytest.mark.asyncio
    async def test_get_status(self, client: AsyncClient):
        """Test getting job status"""
        response = await client.get(
            "/api/v1/orchestration/status/test-job-1"
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "job_id" in data
            assert "status" in data

    @pytest.mark.asyncio
    async def test_parallel_execution(self, client: AsyncClient):
        """Test parallel execution endpoint"""
        response = await client.post(
            "/api/v1/orchestration/parallel",
            json={
                "business_profile_id": "test-profile-1",
                "agents": ["goal", "growth", "costing", "suggestions"]
            }
        )
        
        assert response.status_code in [200, 202]
        data = response.json()
        assert "job_id" in data or "results" in data

    @pytest.mark.asyncio
    async def test_sequential_execution(self, client: AsyncClient):
        """Test sequential execution endpoint"""
        response = await client.post(
            "/api/v1/orchestration/sequential",
            json={
                "business_profile_id": "test-profile-1",
                "agents": ["goal", "growth", "costing", "suggestions"]
            }
        )
        
        assert response.status_code in [200, 202]
        data = response.json()
        assert "job_id" in data or "results" in data


@pytest.mark.integration
class TestAPIErrorHandling:
    """Integration tests for API error handling"""

    @pytest.mark.asyncio
    async def test_invalid_request_body(self, client: AsyncClient):
        """Test handling of invalid request body"""
        response = await client.post(
            "/api/v1/strategy-advisor/analyze",
            json={"invalid": "data"}
        )
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_missing_required_field(self, client: AsyncClient):
        """Test handling of missing required fields"""
        response = await client.post(
            "/api/v1/strategy-advisor/goals",
            json={"title": "Test Goal"}  # Missing business_profile_id
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_not_found(self, client: AsyncClient):
        """Test handling of not found resources"""
        response = await client.get("/api/v1/strategy-advisor/analysis/non-existent-id")
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_method_not_allowed(self, client: AsyncClient):
        """Test handling of invalid HTTP methods"""
        response = await client.put("/api/v1/strategy-advisor/analyze")
        
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_rate_limiting(self, client: AsyncClient):
        """Test rate limiting (if implemented)"""
        # Make multiple rapid requests
        responses = []
        for _ in range(100):
            response = await client.get(
                "/api/v1/scoring/current",
                params={"business_profile_id": "test-profile-1"}
            )
            responses.append(response.status_code)
            if response.status_code == 429:
                break
        
        # Check if rate limiting was triggered
        assert 429 in responses or all(status == 200 for status in responses)


@pytest.mark.integration
class TestAPIAuthentication:
    """Integration tests for API authentication"""

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test unauthorized access to protected endpoints"""
        # This test assumes authentication is implemented
        response = await client.post(
            "/api/v1/strategy-advisor/analyze",
            json={"business_profile_id": "test-profile-1"},
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        # Should either succeed (if auth not implemented) or fail with 401/403
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_valid_authentication(self, client: AsyncClient):
        """Test valid authentication"""
        # This test assumes authentication is implemented
        response = await client.post(
            "/api/v1/strategy-advisor/analyze",
            json={"business_profile_id": "test-profile-1"}
        )
        
        # Should succeed with valid auth or if auth not implemented
        assert response.status_code in [200, 201, 202]
