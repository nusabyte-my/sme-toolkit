"""Growth Plan Advisor Agent - Growth strategy and roadmap generation"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.prompts.growth_advisor_prompts import GROWTH_ADVISOR_PROMPTS
from app.services.growth_service import GrowthService

logger = logging.getLogger(__name__)


class GrowthPlanAdvisorAgent(BaseAgent):
    """
    Agent for creating growth strategies, identifying opportunities,
    generating roadmaps, and assessing risks.
    """

    def __init__(self, growth_service: Optional[GrowthService] = None):
        self.growth_service = growth_service
        self.gemini_client = get_gemini_client()

    @property
    def name(self) -> str:
        return "Growth Plan Advisor Agent"

    def get_actions(self) -> list:
        return [
            "create_growth_strategy",
            "identify_opportunities",
            "generate_roadmap",
            "assess_risks",
            "calculate_growth_potential"
        ]

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for the agent.
        
        Args:
            input_data: Dictionary containing action type and parameters
            
        Returns:
            Agent response with results
        """
        action = input_data.get("action")
        
        try:
            if action == "create_growth_strategy":
                return await self.create_growth_strategy(
                    business_context=input_data.get("business_context", {}),
                    bmc_data=input_data.get("bmc_data", {}),
                    market_data=input_data.get("market_data", {}),
                    financial_projections=input_data.get("financial_projections", {}),
                    growth_metrics=input_data.get("growth_metrics", {}),
                    competitive_landscape=input_data.get("competitive_landscape", {}),
                    business_profile_id=input_data.get("business_profile_id")
                )
            elif action == "identify_opportunities":
                return await self.identify_opportunities(
                    market_data=input_data.get("market_data", {}),
                    business_data=input_data.get("business_data", {}),
                    bmc_data=input_data.get("bmc_data", {}),
                    current_performance=input_data.get("current_performance", {})
                )
            elif action == "generate_roadmap":
                return await self.generate_roadmap(
                    strategy=input_data.get("strategy", {}),
                    opportunities=input_data.get("opportunities", []),
                    timeframe=input_data.get("timeframe", "6 months"),
                    resources=input_data.get("resources", {})
                )
            elif action == "assess_risks":
                return await self.assess_risks(
                    strategy=input_data.get("strategy", {}),
                    opportunities=input_data.get("opportunities", []),
                    market_conditions=input_data.get("market_conditions", {}),
                    capabilities=input_data.get("capabilities", {})
                )
            elif action == "calculate_growth_potential":
                return await self.calculate_growth_potential(
                    business_data=input_data.get("business_data", {}),
                    market_analysis=input_data.get("market_analysis", {}),
                    competitive_landscape=input_data.get("competitive_landscape", {}),
                    financial_performance=input_data.get("financial_performance", {}),
                    historical_growth=input_data.get("historical_growth", [])
                )
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": self.get_actions()
                }
        except Exception as e:
            logger.error(f"Error in GrowthPlanAdvisorAgent.invoke: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "fallback_response": self._get_fallback_response(action)
            }

    async def create_growth_strategy(
        self,
        business_context: Dict[str, Any],
        bmc_data: Dict[str, Any],
        market_data: Dict[str, Any],
        financial_projections: Dict[str, Any],
        growth_metrics: Dict[str, Any],
        competitive_landscape: Dict[str, Any],
        business_profile_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive growth strategy.
        
        Args:
            business_context: Business context information
            bmc_data: Business Model Canvas data
            market_data: Market analysis data
            financial_projections: Financial projections
            growth_metrics: Current growth metrics
            competitive_landscape: Competitive analysis
            business_profile_id: Optional business profile ID for storage
            
        Returns:
            Complete growth strategy
        """
        try:
            logger.info("Creating growth strategy")
            
            # Prepare prompt
            prompt = GROWTH_ADVISOR_PROMPTS["CREATE_GROWTH_STRATEGY"].format(
                business_context=self._format_context(business_context),
                bmc_data=self._format_bmc(bmc_data),
                market_data=self._format_market_data(market_data),
                financial_projections=self._format_financial_data(financial_projections),
                growth_metrics=self._format_metrics(growth_metrics),
                competitive_landscape=self._format_competitive_data(competitive_landscape)
            )
            
            # Generate strategy using AI
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Structure growth plan data
            growth_plan = self._parse_growth_strategy_response(response)
            
            # Store growth plan if business_profile_id provided
            stored_plan = None
            if business_profile_id and self.growth_service:
                try:
                    stored_plan = await self.growth_service.create_growth_plan(
                        business_profile_id=business_profile_id,
                        title=growth_plan.get("title", "Growth Strategy"),
                        timeframe=growth_plan.get("timeframe"),
                        plan_data=growth_plan,
                        status="draft"
                    )
                except Exception as e:
                    logger.warning(f"Failed to store growth plan: {e}")
            
            return {
                "success": True,
                "growth_plan": growth_plan,
                "stored_plan": stored_plan
            }
            
        except Exception as e:
            logger.error(f"Error creating growth strategy: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "growth_plan": None,
                "fallback_response": self._get_fallback_growth_strategy()
            }

    async def identify_opportunities(
        self,
        market_data: Dict[str, Any],
        business_data: Dict[str, Any],
        bmc_data: Dict[str, Any],
        current_performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Identify growth opportunities.
        
        Args:
            market_data: Market analysis data
            business_data: Business performance data
            bmc_data: Business Model Canvas data
            current_performance: Current performance metrics
            
        Returns:
            List of growth opportunities with analysis
        """
        try:
            logger.info("Identifying growth opportunities")
            
            # Prepare prompt
            prompt = GROWTH_ADVISOR_PROMPTS["IDENTIFY_OPPORTUNITIES"].format(
                market_data=self._format_market_data(market_data),
                business_data=self._format_business_data(business_data),
                bmc_data=self._format_bmc(bmc_data),
                current_performance=self._format_metrics(current_performance)
            )
            
            # Generate opportunities
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Parse opportunities
            opportunities = self._parse_opportunities_response(response)
            
            return {
                "success": True,
                "opportunities": opportunities,
                "total_opportunities": len(opportunities)
            }
            
        except Exception as e:
            logger.error(f"Error identifying opportunities: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "opportunities": []
            }

    async def generate_roadmap(
        self,
        strategy: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        timeframe: str,
        resources: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate implementation roadmap.
        
        Args:
            strategy: Growth strategy
            opportunities: List of growth opportunities
            timeframe: Implementation timeframe
            resources: Available resources
            
        Returns:
            Detailed implementation roadmap
        """
        try:
            logger.info("Generating implementation roadmap")
            
            # Prepare prompt
            prompt = GROWTH_ADVISOR_PROMPTS["GENERATE_ROADMAP"].format(
                strategy=self._format_strategy(strategy),
                opportunities=self._format_opportunities(opportunities),
                timeframe=timeframe,
                resources=self._format_resources(resources)
            )
            
            # Generate roadmap
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Parse roadmap
            roadmap = self._parse_roadmap_response(response)
            
            return {
                "success": True,
                "roadmap": roadmap
            }
            
        except Exception as e:
            logger.error(f"Error generating roadmap: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "roadmap": None
            }

    async def assess_risks(
        self,
        strategy: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        market_conditions: Dict[str, Any],
        capabilities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess risks for growth strategy.
        
        Args:
            strategy: Growth strategy
            opportunities: List of growth opportunities
            market_conditions: Current market conditions
            capabilities: Business capabilities
            
        Returns:
            Comprehensive risk assessment
        """
        try:
            logger.info("Assessing growth risks")
            
            # Prepare prompt
            prompt = GROWTH_ADVISOR_PROMPTS["ASSESS_RISKS"].format(
                strategy=self._format_strategy(strategy),
                opportunities=self._format_opportunities(opportunities),
                market_conditions=self._format_market_data(market_conditions),
                capabilities=self._format_capabilities(capabilities)
            )
            
            # Generate risk assessment
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Parse risk assessment
            risk_assessment = self._parse_risk_assessment_response(response)
            
            return {
                "success": True,
                "risk_assessment": risk_assessment
            }
            
        except Exception as e:
            logger.error(f"Error assessing risks: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "risk_assessment": None
            }

    async def calculate_growth_potential(
        self,
        business_data: Dict[str, Any],
        market_analysis: Dict[str, Any],
        competitive_landscape: Dict[str, Any],
        financial_performance: Dict[str, Any],
        historical_growth: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate growth potential score.
        
        Args:
            business_data: Business performance data
            market_analysis: Market analysis
            competitive_landscape: Competitive analysis
            financial_performance: Financial metrics
            historical_growth: Historical growth data
            
        Returns:
            Growth potential analysis with scores
        """
        try:
            logger.info("Calculating growth potential")
            
            # Prepare prompt
            prompt = GROWTH_ADVISOR_PROMPTS["CALCULATE_GROWTH_POTENTIAL"].format(
                business_data=self._format_business_data(business_data),
                market_analysis=self._format_market_data(market_analysis),
                competitive_landscape=self._format_competitive_data(competitive_landscape),
                financial_performance=self._format_financial_data(financial_performance),
                historical_growth=self._format_historical_growth(historical_growth)
            )
            
            # Generate growth potential analysis
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Parse growth potential
            growth_potential = self._parse_growth_potential_response(response)
            
            return {
                "success": True,
                "growth_potential": growth_potential
            }
            
        except Exception as e:
            logger.error(f"Error calculating growth potential: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "growth_potential": None
            }

    # Helper methods

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format business context for prompt"""
        if not context:
            return "No business context provided"
        return "\n".join([f"- {k}: {v}" for k, v in context.items()])

    def _format_bmc(self, bmc_data: Dict[str, Any]) -> str:
        """Format BMC data for prompt"""
        if not bmc_data:
            return "No BMC data provided"
        return "\n".join([f"- {k}: {v}" for k, v in bmc_data.items()])

    def _format_market_data(self, market_data: Dict[str, Any]) -> str:
        """Format market data for prompt"""
        if not market_data:
            return "No market data provided"
        return "\n".join([f"- {k}: {v}" for k, v in market_data.items()])

    def _format_financial_data(self, financial_data: Dict[str, Any]) -> str:
        """Format financial data for prompt"""
        if not financial_data:
            return "No financial data provided"
        return "\n".join([f"- {k}: {v}" for k, v in financial_data.items()])

    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format metrics for prompt"""
        if not metrics:
            return "No metrics provided"
        return "\n".join([f"- {k}: {v}" for k, v in metrics.items()])

    def _format_competitive_data(self, competitive_data: Dict[str, Any]) -> str:
        """Format competitive data for prompt"""
        if not competitive_data:
            return "No competitive data provided"
        return "\n".join([f"- {k}: {v}" for k, v in competitive_data.items()])

    def _format_business_data(self, business_data: Dict[str, Any]) -> str:
        """Format business data for prompt"""
        if not business_data:
            return "No business data provided"
        return "\n".join([f"- {k}: {v}" for k, v in business_data.items()])

    def _format_strategy(self, strategy: Dict[str, Any]) -> str:
        """Format strategy for prompt"""
        if not strategy:
            return "No strategy provided"
        return f"Title: {strategy.get('title', 'Unknown')}\nTimeframe: {strategy.get('timeframe', 'Not specified')}"

    def _format_opportunities(self, opportunities: List[Dict[str, Any]]) -> str:
        """Format opportunities for prompt"""
        if not opportunities:
            return "No opportunities provided"
        return "\n".join([f"- {opp.get('title', 'Unknown')}: {opp.get('type', 'Unknown')}" for opp in opportunities])

    def _format_resources(self, resources: Dict[str, Any]) -> str:
        """Format resources for prompt"""
        if not resources:
            return "No resources provided"
        return "\n".join([f"- {k}: {v}" for k, v in resources.items()])

    def _format_capabilities(self, capabilities: Dict[str, Any]) -> str:
        """Format capabilities for prompt"""
        if not capabilities:
            return "No capabilities provided"
        return "\n".join([f"- {k}: {v}" for k, v in capabilities.items()])

    def _format_historical_growth(self, historical_growth: List[Dict[str, Any]]) -> str:
        """Format historical growth for prompt"""
        if not historical_growth:
            return "No historical growth data"
        return "\n".join([f"- Period: {h.get('period', 'Unknown')}, Growth: {h.get('growth_rate', 'N/A')}" for h in historical_growth])

    def _parse_growth_strategy_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into growth strategy object"""
        return {
            "plan_id": f"gp_{uuid.uuid4().hex[:8]}",
            "title": response.get("strategy_overview", {}).get("title", "Growth Strategy"),
            "timeframe": response.get("strategy_overview", {}).get("timeframe", "6 months"),
            "overall_growth_potential": response.get("strategy_overview", {}).get("overall_growth_potential", 0.7),
            "growth_opportunities": response.get("growth_opportunities", []),
            "growth_channels": response.get("growth_channels", []),
            "implementation_roadmap": response.get("implementation_roadmap", []),
            "resource_requirements": response.get("resource_requirements", {}),
            "kpi_targets": response.get("kpi_targets", {}),
            "risk_assessment": response.get("risk_assessment", {})
        }

    def _parse_opportunities_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse AI response into opportunity objects"""
        opportunities = response.get("opportunities", [])
        if not isinstance(opportunities, list):
            opportunities = []
        
        parsed_opportunities = []
        for i, opp in enumerate(opportunities):
            parsed_opportunities.append({
                "id": f"opp_{i+1}",
                "title": opp.get("title", ""),
                "type": opp.get("type", "unknown"),
                "potential_revenue_impact": opp.get("potential_revenue_impact", ""),
                "confidence_score": opp.get("feasibility_analysis", {}).get("feasibility_score", 0.5),
                "required_investment": opp.get("feasibility_analysis", {}).get("required_investment", ""),
                "expected_roi": opp.get("feasibility_analysis", {}).get("expected_roi", ""),
                "time_to_market": opp.get("feasibility_analysis", {}).get("time_to_implement", ""),
                "key_actions": opp.get("implementation", {}).get("key_actions", []),
                "risks": opp.get("risk_assessment", {}).get("main_risks", []),
                "mitigation_strategies": opp.get("risk_assessment", {}).get("mitigation_strategies", [])
            })
        
        return parsed_opportunities

    def _parse_roadmap_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into roadmap object"""
        return {
            "phases": response.get("phases", []),
            "timeline": response.get("timeline", {}),
            "milestones": response.get("milestones", []),
            "dependencies": response.get("dependencies", []),
            "resource_allocation": response.get("resource_allocation", {})
        }

    def _parse_risk_assessment_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into risk assessment object"""
        return {
            "high_priority_risks": response.get("high_priority_risks", []),
            "medium_priority_risks": response.get("medium_priority_risks", []),
            "low_priority_risks": response.get("low_priority_risks", []),
            "risk_categories": response.get("risk_categories", {}),
            "overall_risk_level": response.get("overall_risk_assessment", {}).get("overall_risk_level", "medium"),
            "risk_management_recommendations": response.get("risk_management_recommendations", {})
        }

    def _parse_growth_potential_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into growth potential object"""
        return {
            "overall_score": response.get("overall_growth_potential_score", 0),
            "market_opportunity_score": response.get("market_opportunity_score", 0),
            "competitive_advantage_score": response.get("competitive_advantage_score", 0),
            "execution_capability_score": response.get("execution_capability_score", 0),
            "financial_capacity_score": response.get("financial_capacity_score", 0),
            "innovation_potential_score": response.get("innovation_potential_score", 0),
            "growth_potential_breakdown": response.get("growth_potential_breakdown", {}),
            "growth_scenarios": response.get("growth_scenarios", {}),
            "recommendations": response.get("recommendations", [])
        }

    def _get_fallback_response(self, action: str) -> Dict[str, Any]:
        """Get fallback response for failed actions"""
        fallbacks = {
            "create_growth_strategy": {
                "growth_plan": None,
                "message": "Unable to create growth strategy. Please provide more business context."
            },
            "identify_opportunities": {
                "opportunities": [],
                "message": "Unable to identify opportunities. Please provide more market data."
            },
            "generate_roadmap": {
                "roadmap": None,
                "message": "Unable to generate roadmap. Please provide more strategy details."
            },
            "assess_risks": {
                "risk_assessment": None,
                "message": "Unable to assess risks. Please provide more context."
            },
            "calculate_growth_potential": {
                "growth_potential": None,
                "message": "Unable to calculate growth potential. Please provide more data."
            }
        }
        return fallbacks.get(action, {"message": "Unknown action"})

    def _get_fallback_growth_strategy(self) -> Dict[str, Any]:
        """Get fallback growth strategy when AI fails"""
        return {
            "plan_id": f"gp_fallback_{uuid.uuid4().hex[:8]}",
            "title": "6-Month Growth Strategy",
            "timeframe": "6 months",
            "overall_growth_potential": 0.6,
            "growth_opportunities": [
                {
                    "id": "opp_1",
                    "title": "Market Expansion",
                    "type": "market_expansion",
                    "potential_revenue_impact": "$50,000",
                    "confidence_score": 0.7,
                    "required_investment": "$20,000",
                    "expected_roi": "250%",
                    "time_to_market": "3 months",
                    "key_actions": [
                        "Conduct market research",
                        "Develop marketing materials",
                        "Launch in new market"
                    ],
                    "risks": ["market_saturation", "competition"],
                    "mitigation_strategies": ["differentiate_offering", "competitive_pricing"]
                }
            ],
            "growth_channels": [
                {
                    "channel": "digital_marketing",
                    "priority": "high",
                    "expected_impact": "30% increase in leads",
                    "budget_allocation": "$10,000",
                    "tactics": ["SEO", "Content marketing", "Paid ads"]
                }
            ],
            "implementation_roadmap": [
                {
                    "phase": "Phase 1: Foundation",
                    "duration": "Month 1-2",
                    "objectives": ["Market research", "Team hiring"],
                    "deliverables": ["Research report", "Hired 2 sales reps"],
                    "success_criteria": ["Research completed", "Team onboarded"]
                }
            ],
            "resource_requirements": {
                "team": ["sales_manager", "marketing_specialist"],
                "budget": "$50,000",
                "tools": ["CRM_system", "analytics_platform"]
            },
            "kpi_targets": {
                "revenue_growth": "30%",
                "customer_acquisition": "100 new customers",
                "market_penetration": "3% in target segment"
            },
            "risk_assessment": {
                "high_risks": [
                    {
                        "risk": "Market entry barriers",
                        "probability": 0.5,
                        "impact": "medium",
                        "mitigation": "Partner with established players"
                    }
                ]
            }
        }
