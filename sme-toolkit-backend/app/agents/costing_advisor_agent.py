"""Costing Advisor Agent - Cost analysis and pricing strategies"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.prompts.costing_advisor_prompts import COSTING_ADVISOR_PROMPTS
from app.services.costing_service import CostingService

logger = logging.getLogger(__name__)


class CostingAdvisorAgent(BaseAgent):
    """
    Agent for analyzing cost structures, developing pricing strategies,
    identifying optimization opportunities, and performing break-even analysis.
    """

    def __init__(self, costing_service: Optional[CostingService] = None):
        self.costing_service = costing_service
        self.gemini_client = get_gemini_client()

    @property
    def name(self) -> str:
        return "Costing Advisor Agent"

    def get_actions(self) -> list:
        return [
            "analyze_cost_structure",
            "develop_pricing_strategy",
            "identify_optimization_opportunities",
            "break_even_analysis",
            "calculate_profitability_metrics"
        ]

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for agent.
        
        Args:
            input_data: Dictionary containing action type and parameters
            
        Returns:
            Agent response with results
        """
        action = input_data.get("action")
        
        try:
            if action == "analyze_cost_structure":
                return await self.analyze_cost_structure(
                    financial_data=input_data.get("financial_data", {}),
                    cost_breakdown=input_data.get("cost_breakdown", {}),
                    bmc_data=input_data.get("bmc_data", {}),
                    operational_metrics=input_data.get("operational_metrics", {}),
                    business_profile_id=input_data.get("business_profile_id")
                )
            elif action == "develop_pricing_strategy":
                return await self.develop_pricing_strategy(
                    cost_data=input_data.get("cost_data", {}),
                    market_pricing=input_data.get("market_pricing", {}),
                    competitor_pricing=input_data.get("competitor_pricing", {}),
                    bmc_data=input_data.get("bmc_data", {}),
                    value_proposition=input_data.get("value_proposition", "")
                )
            elif action == "identify_optimization_opportunities":
                return await self.identify_optimization_opportunities(
                    cost_data=input_data.get("cost_data", {}),
                    operational_data=input_data.get("operational_data", {}),
                    industry_benchmarks=input_data.get("industry_benchmarks", {}),
                    business_processes=input_data.get("business_processes", {})
                )
            elif action == "break_even_analysis":
                return await self.break_even_analysis(
                    cost_data=input_data.get("cost_data", {}),
                    pricing=input_data.get("pricing", {}),
                    revenue_data=input_data.get("revenue_data", {})
                )
            elif action == "calculate_profitability_metrics":
                return await self.calculate_profitability_metrics(
                    financial_data=input_data.get("financial_data", {}),
                    revenue_data=input_data.get("revenue_data", {}),
                    cost_data=input_data.get("cost_data", {}),
                    bmc_data=input_data.get("bmc_data", {})
                )
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": self.get_actions()
                }
        except Exception as e:
            logger.error(f"Error in CostingAdvisorAgent.invoke: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "fallback_response": self._get_fallback_response(action)
            }

    async def analyze_cost_structure(
        self,
        financial_data: Dict[str, Any],
        cost_breakdown: Dict[str, Any],
        bmc_data: Dict[str, Any],
        operational_metrics: Dict[str, Any],
        business_profile_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze cost structure.
        
        Args:
            financial_data: Financial data
            cost_breakdown: Cost breakdown
            bmc_data: Business Model Canvas data
            operational_metrics: Operational metrics
            business_profile_id: Optional business profile ID for storage
            
        Returns:
            Cost structure analysis
        """
        try:
            logger.info("Analyzing cost structure")
            
            # Prepare prompt
            prompt = COSTING_ADVISOR_PROMPTS["ANALYZE_COST_STRUCTURE"].format(
                financial_data=self._format_financial_data(financial_data),
                cost_breakdown=self._format_cost_breakdown(cost_breakdown),
                bmc_data=self._format_bmc(bmc_data),
                operational_metrics=self._format_metrics(operational_metrics)
            )
            
            # Generate cost structure analysis
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Structure cost analysis
            cost_structure = self._parse_cost_structure_response(response)
            
            # Store costing analysis if business_profile_id provided
            stored_analysis = None
            if business_profile_id and self.costing_service:
                try:
                    stored_analysis = await self.costing_service.create_costing_analysis(
                        business_profile_id=business_profile_id,
                        cost_structure=cost_structure,
                        pricing_strategies=None,
                        optimization_opportunities=None,
                        break_even_analysis=None
                    )
                except Exception as e:
                    logger.warning(f"Failed to store costing analysis: {e}")
            
            return {
                "success": True,
                "cost_structure": cost_structure,
                "stored_analysis": stored_analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing cost structure: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "cost_structure": None,
                "fallback_response": self._get_fallback_cost_structure()
            }

    async def develop_pricing_strategy(
        self,
        cost_data: Dict[str, Any],
        market_pricing: Dict[str, Any],
        competitor_pricing: Dict[str, Any],
        bmc_data: Dict[str, Any],
        value_proposition: str
    ) -> Dict[str, Any]:
        """
        Develop pricing strategies.
        
        Args:
            cost_data: Cost data
            market_pricing: Market pricing data
            competitor_pricing: Competitor pricing
            bmc_data: Business Model Canvas data
            value_proposition: Value proposition
            
        Returns:
            Pricing strategies with recommendations
        """
        try:
            logger.info("Developing pricing strategies")
            
            # Prepare prompt
            prompt = COSTING_ADVISOR_PROMPTS["DEVELOP_PRICING_STRATEGY"].format(
                cost_data=self._format_cost_data(cost_data),
                market_pricing=self._format_market_pricing(market_pricing),
                competitor_pricing=self._format_competitor_pricing(competitor_pricing),
                bmc_data=self._format_bmc(bmc_data),
                value_proposition=value_proposition
            )
            
            # Generate pricing strategies
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Parse pricing strategies
            pricing_strategies = self._parse_pricing_strategies_response(response)
            
            return {
                "success": True,
                "pricing_strategies": pricing_strategies,
                "recommendation": response.get("final_recommendation", {})
            }
            
        except Exception as e:
            logger.error(f"Error developing pricing strategies: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "pricing_strategies": [],
                "recommendation": {}
            }

    async def identify_optimization_opportunities(
        self,
        cost_data: Dict[str, Any],
        operational_data: Dict[str, Any],
        industry_benchmarks: Dict[str, Any],
        business_processes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Identify cost optimization opportunities.
        
        Args:
            cost_data: Cost data
            operational_data: Operational data
            industry_benchmarks: Industry benchmarks
            business_processes: Business process information
            
        Returns:
            List of optimization opportunities
        """
        try:
            logger.info("Identifying optimization opportunities")
            
            # Prepare prompt
            prompt = COSTING_ADVISOR_PROMPTS["IDENTIFY_OPTIMIZATION_OPPORTUNITIES"].format(
                cost_data=self._format_cost_data(cost_data),
                operational_data=self._format_operational_data(operational_data),
                industry_benchmarks=self._format_benchmarks(industry_benchmarks),
                business_processes=self._format_processes(business_processes)
            )
            
            # Generate optimization opportunities
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Parse optimization opportunities
            opportunities = self._parse_optimization_opportunities_response(response)
            
            return {
                "success": True,
                "optimization_opportunities": opportunities,
                "total_opportunities": len(opportunities),
                "total_potential_savings": self._calculate_total_savings(opportunities)
            }
            
        except Exception as e:
            logger.error(f"Error identifying optimization opportunities: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "optimization_opportunities": []
            }

    async def break_even_analysis(
        self,
        cost_data: Dict[str, Any],
        pricing: Dict[str, Any],
        revenue_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform break-even analysis.
        
        Args:
            cost_data: Cost data
            pricing: Pricing information
            revenue_data: Revenue data
            
        Returns:
            Break-even analysis with scenarios
        """
        try:
            logger.info("Performing break-even analysis")
            
            # Prepare prompt
            prompt = COSTING_ADVISOR_PROMPTS["BREAK_EVEN_ANALYSIS"].format(
                cost_data=self._format_cost_data(cost_data),
                pricing=self._format_pricing(pricing),
                revenue_data=self._format_revenue_data(revenue_data)
            )
            
            # Generate break-even analysis
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Parse break-even analysis
            break_even = self._parse_break_even_response(response)
            
            return {
                "success": True,
                "break_even_analysis": break_even
            }
            
        except Exception as e:
            logger.error(f"Error performing break-even analysis: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "break_even_analysis": None
            }

    async def calculate_profitability_metrics(
        self,
        financial_data: Dict[str, Any],
        revenue_data: Dict[str, Any],
        cost_data: Dict[str, Any],
        bmc_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate profitability metrics.
        
        Args:
            financial_data: Financial data
            revenue_data: Revenue data
            cost_data: Cost data
            bmc_data: Business Model Canvas data
            
        Returns:
            Comprehensive profitability metrics
        """
        try:
            logger.info("Calculating profitability metrics")
            
            # Prepare prompt
            prompt = COSTING_ADVISOR_PROMPTS["CALCULATE_PROFITABILITY_METRICS"].format(
                financial_data=self._format_financial_data(financial_data),
                revenue_data=self._format_revenue_data(revenue_data),
                cost_data=self._format_cost_data(cost_data),
                bmc_data=self._format_bmc(bmc_data)
            )
            
            # Generate profitability metrics
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Parse profitability metrics
            profitability = self._parse_profitability_response(response)
            
            return {
                "success": True,
                "profitability_metrics": profitability
            }
            
        except Exception as e:
            logger.error(f"Error calculating profitability metrics: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "profitability_metrics": None
            }

    # Helper methods

    def _format_financial_data(self, financial_data: Dict[str, Any]) -> str:
        """Format financial data for prompt"""
        if not financial_data:
            return "No financial data provided"
        return "\n".join([f"- {k}: {v}" for k, v in financial_data.items()])

    def _format_cost_breakdown(self, cost_breakdown: Dict[str, Any]) -> str:
        """Format cost breakdown for prompt"""
        if not cost_breakdown:
            return "No cost breakdown provided"
        return "\n".join([f"- {k}: {v}" for k, v in cost_breakdown.items()])

    def _format_bmc(self, bmc_data: Dict[str, Any]) -> str:
        """Format BMC data for prompt"""
        if not bmc_data:
            return "No BMC data provided"
        return "\n".join([f"- {k}: {v}" for k, v in bmc_data.items()])

    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format metrics for prompt"""
        if not metrics:
            return "No metrics provided"
        return "\n".join([f"- {k}: {v}" for k, v in metrics.items()])

    def _format_cost_data(self, cost_data: Dict[str, Any]) -> str:
        """Format cost data for prompt"""
        if not cost_data:
            return "No cost data provided"
        return "\n".join([f"- {k}: {v}" for k, v in cost_data.items()])

    def _format_market_pricing(self, market_pricing: Dict[str, Any]) -> str:
        """Format market pricing for prompt"""
        if not market_pricing:
            return "No market pricing provided"
        return "\n".join([f"- {k}: {v}" for k, v in market_pricing.items()])

    def _format_competitor_pricing(self, competitor_pricing: Dict[str, Any]) -> str:
        """Format competitor pricing for prompt"""
        if not competitor_pricing:
            return "No competitor pricing provided"
        return "\n".join([f"- {k}: {v}" for k, v in competitor_pricing.items()])

    def _format_operational_data(self, operational_data: Dict[str, Any]) -> str:
        """Format operational data for prompt"""
        if not operational_data:
            return "No operational data provided"
        return "\n".join([f"- {k}: {v}" for k, v in operational_data.items()])

    def _format_benchmarks(self, benchmarks: Dict[str, Any]) -> str:
        """Format benchmarks for prompt"""
        if not benchmarks:
            return "No benchmarks provided"
        return "\n".join([f"- {k}: {v}" for k, v in benchmarks.items()])

    def _format_processes(self, processes: Dict[str, Any]) -> str:
        """Format business processes for prompt"""
        if not processes:
            return "No business processes provided"
        return "\n".join([f"- {k}: {v}" for k, v in processes.items()])

    def _format_pricing(self, pricing: Dict[str, Any]) -> str:
        """Format pricing for prompt"""
        if not pricing:
            return "No pricing provided"
        return "\n".join([f"- {k}: {v}" for k, v in pricing.items()])

    def _format_revenue_data(self, revenue_data: Dict[str, Any]) -> str:
        """Format revenue data for prompt"""
        if not revenue_data:
            return "No revenue data provided"
        return "\n".join([f"- {k}: {v}" for k, v in revenue_data.items()])

    def _parse_cost_structure_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into cost structure object"""
        return {
            "fixed_costs": response.get("fixed_costs_analysis", {}),
            "variable_costs": response.get("variable_costs_analysis", {}),
            "total_monthly_cost": response.get("total_cost_summary", {}).get("total_monthly_costs", 0),
            "cost_per_unit": response.get("total_cost_summary", {}).get("cost_per_unit", 0),
            "cost_structure_assessment": response.get("cost_structure_assessment", {}),
            "cost_drivers": response.get("cost_drivers", []),
            "recommendations": response.get("recommendations", [])
        }

    def _parse_pricing_strategies_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse AI response into pricing strategy objects"""
        strategies = []
        
        # Strategy 1: Value-Based
        if "strategy_1" in response:
            s1 = response["strategy_1"]
            strategies.append({
                "strategy": "value_based_pricing",
                "recommended_price": s1.get("recommended_price", ""),
                "rationale": s1.get("rationale", ""),
                "expected_margin": s1.get("expected_margin", ""),
                "market_position": s1.get("market_position", ""),
                "target_customers": s1.get("target_customers", "")
            })
        
        # Strategy 2: Competitive
        if "strategy_2" in response:
            s2 = response["strategy_2"]
            strategies.append({
                "strategy": "competitive_pricing",
                "recommended_price": s2.get("recommended_price", ""),
                "rationale": s2.get("rationale", ""),
                "expected_margin": s2.get("expected_margin", ""),
                "market_position": s2.get("market_position", ""),
                "target_customers": s2.get("target_customers", "")
            })
        
        # Strategy 3: Cost-Plus (optional)
        if "strategy_3" in response:
            s3 = response["strategy_3"]
            strategies.append({
                "strategy": "cost_plus_pricing",
                "recommended_price": s3.get("recommended_price", ""),
                "rationale": s3.get("rationale", ""),
                "expected_margin": s3.get("expected_margin", ""),
                "market_position": s3.get("market_position", ""),
                "target_customers": s3.get("target_customers", "")
            })
        
        return strategies

    def _parse_optimization_opportunities_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse AI response into optimization opportunity objects"""
        opportunities = response.get("optimization_opportunities", [])
        if not isinstance(opportunities, list):
            opportunities = []
        
        parsed_opportunities = []
        for i, opp in enumerate(opportunities):
            parsed_opportunities.append({
                "id": f"opt_{i+1}",
                "area": opp.get("area", ""),
                "current_cost": opp.get("current_cost", ""),
                "potential_savings": opp.get("potential_savings", ""),
                "savings_percentage": opp.get("savings_percentage", 0),
                "actions": opp.get("actions_required", {}).get("specific_actions", []),
                "implementation_effort": opp.get("implementation", {}).get("implementation_effort", "medium"),
                "time_to_impact": opp.get("implementation", {}).get("time_to_impact", ""),
                "priority_score": opp.get("prioritization", {}).get("priority_score", 0)
            })
        
        return parsed_opportunities

    def _parse_break_even_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into break-even analysis object"""
        return {
            "current_break_even_point": response.get("current_break_even_point", {}),
            "cost_structure_analysis": response.get("cost_structure_analysis", {}),
            "break_even_scenarios": response.get("break_even_scenarios", {}),
            "margin_of_safety": response.get("margin_of_safety", {}),
            "sensitivity_analysis": response.get("sensitivity_analysis", {}),
            "profitability_analysis": response.get("profitability_analysis", {}),
            "recommendations": response.get("recommendations", [])
        }

    def _parse_profitability_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into profitability metrics object"""
        return {
            "gross_profitability": response.get("gross_profitability", {}),
            "operating_profitability": response.get("operating_profitability", {}),
            "net_profitability": response.get("net_profitability", {}),
            "profitability_ratios": response.get("profitability_ratios", {}),
            "unit_economics": response.get("unit_economics", {}),
            "customer_economics": response.get("customer_economics", {}),
            "profitability_trends": response.get("profitability_trends", {}),
            "profitability_assessment": response.get("profitability_assessment", {}),
            "recommendations": response.get("recommendations", [])
        }

    def _calculate_total_savings(self, opportunities: List[Dict[str, Any]]) -> float:
        """Calculate total potential savings from opportunities"""
        total = 0.0
        for opp in opportunities:
            savings_str = opp.get("potential_savings", "0")
            # Extract numeric value from string (e.g., "$1,200/month" -> 1200)
            try:
                import re
                match = re.search(r'[\d,]+\.?\d*', savings_str.replace(',', ''))
                if match:
                    total += float(match.group())
            except:
                pass
        return total

    def _get_fallback_response(self, action: str) -> Dict[str, Any]:
        """Get fallback response for failed actions"""
        fallbacks = {
            "analyze_cost_structure": {
                "cost_structure": None,
                "message": "Unable to analyze cost structure. Please provide more financial data."
            },
            "develop_pricing_strategy": {
                "pricing_strategies": [],
                "message": "Unable to develop pricing strategies. Please provide more cost and market data."
            },
            "identify_optimization_opportunities": {
                "optimization_opportunities": [],
                "message": "Unable to identify optimization opportunities. Please provide more operational data."
            },
            "break_even_analysis": {
                "break_even_analysis": None,
                "message": "Unable to perform break-even analysis. Please provide more cost and pricing data."
            },
            "calculate_profitability_metrics": {
                "profitability_metrics": None,
                "message": "Unable to calculate profitability metrics. Please provide more financial data."
            }
        }
        return fallbacks.get(action, {"message": "Unknown action"})

    def _get_fallback_cost_structure(self) -> Dict[str, Any]:
        """Get fallback cost structure when AI fails"""
        return {
            "fixed_costs": {
                "total": "$25,000/month",
                "breakdown": [
                    {"category": "rent", "amount": "$8,000", "percentage": 32},
                    {"category": "salaries", "amount": "$15,000", "percentage": 60},
                    {"category": "software", "amount": "$2,000", "percentage": 8}
                ]
            },
            "variable_costs": {
                "total": "$15,000/month",
                "breakdown": [
                    {"category": "materials", "amount": "$8,000", "percentage": 53},
                    {"category": "shipping", "amount": "$4,000", "percentage": 27},
                    {"category": "commissions", "amount": "$3,000", "percentage": 20}
                ]
            },
            "total_monthly_cost": "$40,000",
            "cost_per_unit": "$20",
            "cost_structure_assessment": {
                "fixed_vs_variable_ratio": "62.5% fixed, 37.5% variable",
                "cost_efficiency_score": 70,
                "cost_competitiveness": "average"
            },
            "cost_drivers": [
                {"driver": "Labor costs", "impact": "high"},
                {"driver": "Material costs", "impact": "medium"}
            ],
            "recommendations": [
                "Review fixed costs for optimization opportunities",
                "Negotiate better rates with suppliers",
                "Consider automation to reduce labor costs"
            ]
        }
