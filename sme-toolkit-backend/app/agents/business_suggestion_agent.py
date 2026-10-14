"""Business Suggestion Agent - Opportunity identification and recommendations"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.prompts.business_suggestion_prompts import BUSINESS_SUGGESTION_PROMPTS
from app.services.suggestion_service import SuggestionService
from app.database import SuggestionStatus

logger = logging.getLogger(__name__)


class BusinessSuggestionAgent(BaseAgent):
    """
    Agent for suggesting business opportunities, partnerships,
    market expansions, and innovation ideas.
    """

    def __init__(self, suggestion_service: Optional[SuggestionService] = None):
        self.suggestion_service = suggestion_service
        self.gemini_client = get_gemini_client()

    @property
    def name(self) -> str:
        return "Business Suggestion Agent"

    def get_actions(self) -> list:
        return [
            "suggest_opportunities",
            "identify_partnerships",
            "recommend_expansion",
            "propose_innovations",
            "calculate_feasibility"
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
            if action == "suggest_opportunities":
                return await self.suggest_opportunities(
                    business_context=input_data.get("business_context", {}),
                    market_data=input_data.get("market_data", {}),
                    bmc_data=input_data.get("bmc_data", {}),
                    capabilities=input_data.get("capabilities", {}),
                    industry_analysis=input_data.get("industry_analysis", {}),
                    business_profile_id=input_data.get("business_profile_id")
                )
            elif action == "identify_partnerships":
                return await self.identify_partnerships(
                    business_profile=input_data.get("business_profile", {}),
                    bmc_data=input_data.get("bmc_data", {}),
                    capabilities=input_data.get("capabilities", {}),
                    market_position=input_data.get("market_position", {})
                )
            elif action == "recommend_expansion":
                return await self.recommend_expansion(
                    market_data=input_data.get("market_data", {}),
                    capabilities=input_data.get("capabilities", {}),
                    bmc_data=input_data.get("bmc_data", {}),
                    competitive_position=input_data.get("competitive_position", {})
                )
            elif action == "propose_innovations":
                return await self.propose_innovations(
                    business_context=input_data.get("business_context", {}),
                    trends=input_data.get("trends", {}),
                    current_products=input_data.get("current_products", []),
                    customer_feedback=input_data.get("customer_feedback", {}),
                    competitive_landscape=input_data.get("competitive_landscape", {})
                )
            elif action == "calculate_feasibility":
                return await self.calculate_feasibility(
                    suggestion=input_data.get("suggestion", {}),
                    resources=input_data.get("resources", {}),
                    capabilities=input_data.get("capabilities", {}),
                    market_conditions=input_data.get("market_conditions", {}),
                    historical_performance=input_data.get("historical_performance", [])
                )
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": self.get_actions()
                }
        except Exception as e:
            logger.error(f"Error in BusinessSuggestionAgent.invoke: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "fallback_response": self._get_fallback_response(action)
            }

    async def suggest_opportunities(
        self,
        business_context: Dict[str, Any],
        market_data: Dict[str, Any],
        bmc_data: Dict[str, Any],
        capabilities: Dict[str, Any],
        industry_analysis: Dict[str, Any],
        business_profile_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Suggest new business opportunities.
        
        Args:
            business_context: Business context information
            market_data: Market analysis data
            bmc_data: Business Model Canvas data
            capabilities: Business capabilities
            industry_analysis: Industry analysis
            business_profile_id: Optional business profile ID for storage
            
        Returns:
            Business opportunities with analysis
        """
        try:
            logger.info("Suggesting business opportunities")
            
            # Prepare prompt
            prompt = BUSINESS_SUGGESTION_PROMPTS["SUGGEST_OPPORTUNITIES"].format(
                business_context=self._format_context(business_context),
                market_data=self._format_market_data(market_data),
                bmc_data=self._format_bmc(bmc_data),
                capabilities=self._format_capabilities(capabilities),
                industry_analysis=self._format_industry_analysis(industry_analysis)
            )
            
            # Generate opportunities using AI
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Parse opportunities
            opportunities = self._parse_opportunities_response(response)
            
            # Store suggestions if business_profile_id provided
            stored_suggestions = []
            if business_profile_id and self.suggestion_service:
                for opp in opportunities:
                    try:
                        stored_suggestion = await self.suggestion_service.create_suggestion(
                            business_profile_id=business_profile_id,
                            suggestion_type=opp.get("type", "new_revenue_stream"),
                            title=opp.get("title", ""),
                            description=opp.get("description"),
                            potential_value=self._parse_potential_value(opp.get("potential_revenue")),
                            feasibility_score=opp.get("feasibility_score", 0.5),
                            suggestion_data=opp,
                            status=SuggestionStatus.SUGGESTED
                        )
                        stored_suggestions.append(stored_suggestion)
                    except Exception as e:
                        logger.warning(f"Failed to store suggestion: {e}")
                        continue
            
            # Calculate prioritized recommendations
            prioritized = self._prioritize_opportunities(opportunities)
            
            return {
                "success": True,
                "business_suggestions": {
                    "new_opportunities": opportunities,
                    "partnership_opportunities": [],
                    "market_expansions": [],
                    "innovation_suggestions": [],
                    "prioritized_recommendations": prioritized
                },
                "stored_suggestions": stored_suggestions if stored_suggestions else None
            }
            
        except Exception as e:
            logger.error(f"Error suggesting opportunities: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "business_suggestions": None,
                "fallback_response": self._get_fallback_opportunities()
            }

    async def identify_partnerships(
        self,
        business_profile: Dict[str, Any],
        bmc_data: Dict[str, Any],
        capabilities: Dict[str, Any],
        market_position: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Identify partnership opportunities.
        
        Args:
            business_profile: Business profile information
            bmc_data: Business Model Canvas data
            capabilities: Business capabilities
            market_position: Current market position
            
        Returns:
            Partnership opportunities with analysis
        """
        try:
            logger.info("Identifying partnership opportunities")
            
            # Prepare prompt
            prompt = BUSINESS_SUGGESTION_PROMPTS["IDENTIFY_PARTNERSHIPS"].format(
                business_profile=self._format_business_profile(business_profile),
                bmc_data=self._format_bmc(bmc_data),
                capabilities=self._format_capabilities(capabilities),
                market_position=self._format_market_position(market_position)
            )
            
            # Generate partnerships
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Parse partnerships
            partnerships = self._parse_partnerships_response(response)
            
            return {
                "success": True,
                "partnership_opportunities": partnerships,
                "total_partnerships": len(partnerships)
            }
            
        except Exception as e:
            logger.error(f"Error identifying partnerships: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "partnership_opportunities": []
            }

    async def recommend_expansion(
        self,
        market_data: Dict[str, Any],
        capabilities: Dict[str, Any],
        bmc_data: Dict[str, Any],
        competitive_position: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recommend market expansion strategies.
        
        Args:
            market_data: Market analysis data
            capabilities: Business capabilities
            bmc_data: Business Model Canvas data
            competitive_position: Competitive position
            
        Returns:
            Market expansion strategies
        """
        try:
            logger.info("Recommending market expansions")
            
            # Prepare prompt
            prompt = BUSINESS_SUGGESTION_PROMPTS["RECOMMEND_EXPANSION"].format(
                market_data=self._format_market_data(market_data),
                capabilities=self._format_capabilities(capabilities),
                bmc_data=self._format_bmc(bmc_data),
                competitive_position=self._format_competitive_position(competitive_position)
            )
            
            # Generate expansions
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Parse expansions
            expansions = self._parse_expansions_response(response)
            
            return {
                "success": True,
                "market_expansions": expansions,
                "total_expansions": len(expansions)
            }
            
        except Exception as e:
            logger.error(f"Error recommending expansions: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "market_expansions": []
            }

    async def propose_innovations(
        self,
        business_context: Dict[str, Any],
        trends: Dict[str, Any],
        current_products: List[Dict[str, Any]],
        customer_feedback: Dict[str, Any],
        competitive_landscape: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Propose innovation ideas.
        
        Args:
            business_context: Business context
            trends: Market trends
            current_products: Current product/service offerings
            customer_feedback: Customer feedback data
            competitive_landscape: Competitive analysis
            
        Returns:
            Innovation suggestions
        """
        try:
            logger.info("Proposing innovations")
            
            # Prepare prompt
            prompt = BUSINESS_SUGGESTION_PROMPTS["PROPOSE_INNOVATIONS"].format(
                business_context=self._format_context(business_context),
                trends=self._format_trends(trends),
                current_products=self._format_products(current_products),
                customer_feedback=self._format_feedback(customer_feedback),
                competitive_landscape=self._format_competitive_landscape(competitive_landscape)
            )
            
            # Generate innovations
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Parse innovations
            innovations = self._parse_innovations_response(response)
            
            return {
                "success": True,
                "innovation_suggestions": innovations,
                "total_innovations": len(innovations)
            }
            
        except Exception as e:
            logger.error(f"Error proposing innovations: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "innovation_suggestions": []
            }

    async def calculate_feasibility(
        self,
        suggestion: Dict[str, Any],
        resources: Dict[str, Any],
        capabilities: Dict[str, Any],
        market_conditions: Dict[str, Any],
        historical_performance: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate feasibility score for a suggestion.
        
        Args:
            suggestion: Suggestion data
            resources: Available resources
            capabilities: Business capabilities
            market_conditions: Current market conditions
            historical_performance: Historical performance data
            
        Returns:
            Feasibility analysis with score
        """
        try:
            logger.info(f"Calculating feasibility for suggestion: {suggestion.get('title', 'Unknown')}")
            
            # Prepare prompt
            prompt = BUSINESS_SUGGESTION_PROMPTS["CALCULATE_FEASIBILITY"].format(
                suggestion=self._format_suggestion(suggestion),
                resources=self._format_resources(resources),
                capabilities=self._format_capabilities(capabilities),
                market_conditions=self._format_market_data(market_conditions),
                historical_performance=self._format_historical_performance(historical_performance)
            )
            
            # Generate feasibility analysis
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Structure feasibility data
            feasibility = {
                "overall_feasibility_score": response.get("overall_feasibility_score", 0),
                "resource_feasibility": response.get("resource_feasibility", {}),
                "technical_feasibility": response.get("technical_feasibility", {}),
                "market_feasibility": response.get("market_feasibility", {}),
                "operational_feasibility": response.get("operational_feasibility", {}),
                "financial_feasibility": response.get("financial_feasibility", {}),
                "risk_assessment": response.get("risk_assessment", {}),
                "success_probability": response.get("success_probability", 0),
                "recommendations": response.get("recommendations", [])
            }
            
            return {
                "success": True,
                "feasibility": feasibility
            }
            
        except Exception as e:
            logger.error(f"Error calculating feasibility: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "feasibility": {
                    "overall_feasibility_score": 0,
                    "resource_feasibility": {},
                    "technical_feasibility": {},
                    "market_feasibility": {},
                    "operational_feasibility": {},
                    "financial_feasibility": {},
                    "risk_assessment": {},
                    "success_probability": 0,
                    "recommendations": []
                }
            }

    # Helper methods

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format business context for prompt"""
        if not context:
            return "No business context provided"
        return "\n".join([f"- {k}: {v}" for k, v in context.items()])

    def _format_market_data(self, market_data: Dict[str, Any]) -> str:
        """Format market data for prompt"""
        if not market_data:
            return "No market data provided"
        return "\n".join([f"- {k}: {v}" for k, v in market_data.items()])

    def _format_bmc(self, bmc_data: Dict[str, Any]) -> str:
        """Format BMC data for prompt"""
        if not bmc_data:
            return "No BMC data provided"
        return "\n".join([f"- {k}: {v}" for k, v in bmc_data.items()])

    def _format_capabilities(self, capabilities: Dict[str, Any]) -> str:
        """Format capabilities for prompt"""
        if not capabilities:
            return "No capabilities provided"
        return "\n".join([f"- {k}: {v}" for k, v in capabilities.items()])

    def _format_industry_analysis(self, industry_analysis: Dict[str, Any]) -> str:
        """Format industry analysis for prompt"""
        if not industry_analysis:
            return "No industry analysis provided"
        return "\n".join([f"- {k}: {v}" for k, v in industry_analysis.items()])

    def _format_business_profile(self, business_profile: Dict[str, Any]) -> str:
        """Format business profile for prompt"""
        if not business_profile:
            return "No business profile provided"
        return "\n".join([f"- {k}: {v}" for k, v in business_profile.items()])

    def _format_market_position(self, market_position: Dict[str, Any]) -> str:
        """Format market position for prompt"""
        if not market_position:
            return "No market position provided"
        return "\n".join([f"- {k}: {v}" for k, v in market_position.items()])

    def _format_competitive_position(self, competitive_position: Dict[str, Any]) -> str:
        """Format competitive position for prompt"""
        if not competitive_position:
            return "No competitive position provided"
        return "\n".join([f"- {k}: {v}" for k, v in competitive_position.items()])

    def _format_trends(self, trends: Dict[str, Any]) -> str:
        """Format trends for prompt"""
        if not trends:
            return "No trends provided"
        return "\n".join([f"- {k}: {v}" for k, v in trends.items()])

    def _format_products(self, products: List[Dict[str, Any]]) -> str:
        """Format products for prompt"""
        if not products:
            return "No products provided"
        return "\n".join([f"- {p.get('name', 'Unknown')}: {p.get('description', 'No description')}" for p in products])

    def _format_feedback(self, feedback: Dict[str, Any]) -> str:
        """Format customer feedback for prompt"""
        if not feedback:
            return "No customer feedback provided"
        return "\n".join([f"- {k}: {v}" for k, v in feedback.items()])

    def _format_competitive_landscape(self, competitive_landscape: Dict[str, Any]) -> str:
        """Format competitive landscape for prompt"""
        if not competitive_landscape:
            return "No competitive landscape provided"
        return "\n".join([f"- {k}: {v}" for k, v in competitive_landscape.items()])

    def _format_suggestion(self, suggestion: Dict[str, Any]) -> str:
        """Format suggestion for prompt"""
        if not suggestion:
            return "No suggestion provided"
        return f"Title: {suggestion.get('title', 'Unknown')}\nDescription: {suggestion.get('description', 'No description')}"

    def _format_resources(self, resources: Dict[str, Any]) -> str:
        """Format resources for prompt"""
        if not resources:
            return "No resources provided"
        return "\n".join([f"- {k}: {v}" for k, v in resources.items()])

    def _format_historical_performance(self, performance: List[Dict[str, Any]]) -> str:
        """Format historical performance for prompt"""
        if not performance:
            return "No historical performance data"
        return "\n".join([f"- Initiative: {p.get('initiative', 'Unknown')}, Success: {p.get('success', 'N/A')}" for p in performance])

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
                "type": opp.get("type", "new_revenue_stream"),
                "description": opp.get("description", ""),
                "potential_revenue": opp.get("potential_revenue", ""),
                "investment_required": opp.get("investment_required", ""),
                "time_to_market": opp.get("time_to_market", ""),
                "feasibility_score": opp.get("feasibility_analysis", {}).get("feasibility_score", 0.5),
                "alignment_with_current_business": opp.get("feasibility_analysis", {}).get("alignment_with_current_business", 0.5),
                "key_advantages": opp.get("strategic_fit", {}).get("key_advantages", []),
                "implementation_steps": opp.get("implementation", {}).get("implementation_steps", []),
                "risks": opp.get("risk_assessment", {}).get("main_risks", []),
                "success_probability": opp.get("risk_assessment", {}).get("success_probability", 0.5)
            })
        
        return parsed_opportunities

    def _parse_partnerships_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse AI response into partnership objects"""
        partnerships = response.get("partnership_opportunities", [])
        if not isinstance(partnerships, list):
            partnerships = []
        
        parsed_partnerships = []
        for i, partner in enumerate(partnerships):
            parsed_partnerships.append({
                "id": f"partner_{i+1}",
                "title": partner.get("title", ""),
                "type": partner.get("type", "strategic"),
                "partner_type": partner.get("partner_type", ""),
                "potential_benefits": partner.get("potential_benefits", []),
                "required_commitment": partner.get("partnership_structure", {}).get("required_commitment", ""),
                "estimated_value": partner.get("strategic_value", {}).get("estimated_value", ""),
                "alignment_score": partner.get("strategic_value", {}).get("alignment_score", 0.5)
            })
        
        return parsed_partnerships

    def _parse_expansions_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse AI response into expansion objects"""
        expansions = response.get("expansion_strategies", [])
        if not isinstance(expansions, list):
            expansions = []
        
        parsed_expansions = []
        for i, exp in enumerate(expansions):
            parsed_expansions.append({
                "id": f"exp_{i+1}",
                "title": exp.get("title", ""),
                "type": exp.get("type", "market_expansion"),
                "target_market": exp.get("market_analysis", {}).get("target_market", ""),
                "market_size": exp.get("market_analysis", {}).get("market_size", ""),
                "growth_rate": exp.get("market_analysis", {}).get("growth_rate", ""),
                "entry_strategy": exp.get("expansion_strategy", {}).get("entry_strategy", ""),
                "required_investments": exp.get("expansion_strategy", {}).get("required_investments", []),
                "competitive_advantage": exp.get("competitive_advantage", ""),
                "timeline": exp.get("financial_projections", {}).get("timeline", ""),
                "potential_revenue": exp.get("financial_projections", {}).get("potential_revenue", "")
            })
        
        return parsed_expansions

    def _parse_innovations_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse AI response into innovation objects"""
        innovations = response.get("innovation_ideas", [])
        if not isinstance(innovations, list):
            innovations = []
        
        parsed_innovations = []
        for i, inn in enumerate(innovations):
            parsed_innovations.append({
                "id": f"inn_{i+1}",
                "title": inn.get("title", ""),
                "type": inn.get("type", "product_innovation"),
                "description": inn.get("description", ""),
                "development_effort": inn.get("development_assessment", {}).get("development_effort", "medium"),
                "potential_impact": inn.get("impact_analysis", {}).get("potential_impact", ""),
                "required_resources": inn.get("implementation", {}).get("required_resources", []),
                "competitive_advantage": inn.get("competitive_advantage", "")
            })
        
        return parsed_innovations

    def _prioritize_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize opportunities based on feasibility and alignment"""
        # Calculate priority score for each opportunity
        for opp in opportunities:
            feasibility = opp.get("feasibility_score", 0.5)
            alignment = opp.get("alignment_with_current_business", 0.5)
            # Priority score = (feasibility * 0.6) + (alignment * 0.4)
            opp["priority_score"] = (feasibility * 0.6) + (alignment * 0.4)
        
        # Sort by priority score (descending)
        sorted_opportunities = sorted(opportunities, key=lambda x: x.get("priority_score", 0), reverse=True)
        
        # Create prioritized recommendations
        prioritized = []
        for i, opp in enumerate(sorted_opportunities[:10]):  # Top 10
            prioritized.append({
                "rank": i + 1,
                "suggestion_id": opp.get("id", ""),
                "reason": f"High feasibility ({opp.get('feasibility_score', 0):.2f}) and strong alignment ({opp.get('alignment_with_current_business', 0):.2f})",
                "expected_value": opp.get("potential_revenue", "")
            })
        
        return prioritized

    def _parse_potential_value(self, value_str: str) -> Optional[float]:
        """Parse potential value from string to float"""
        if not value_str:
            return None
        try:
            # Extract numeric value from string (e.g., "$200,000/year" -> 200000)
            import re
            match = re.search(r'[\d,]+\.?\d*', value_str.replace(',', ''))
            if match:
                return float(match.group())
        except:
            return None

    def _get_fallback_response(self, action: str) -> Dict[str, Any]:
        """Get fallback response for failed actions"""
        fallbacks = {
            "suggest_opportunities": {
                "business_suggestions": None,
                "message": "Unable to suggest opportunities. Please provide more business context."
            },
            "identify_partnerships": {
                "partnership_opportunities": [],
                "message": "Unable to identify partnerships. Please provide more business profile data."
            },
            "recommend_expansion": {
                "market_expansions": [],
                "message": "Unable to recommend expansions. Please provide more market data."
            },
            "propose_innovations": {
                "innovation_suggestions": [],
                "message": "Unable to propose innovations. Please provide more trend data."
            },
            "calculate_feasibility": {
                "feasibility": None,
                "message": "Unable to calculate feasibility. Please provide more suggestion details."
            }
        }
        return fallbacks.get(action, {"message": "Unknown action"})

    def _get_fallback_opportunities(self) -> Dict[str, Any]:
        """Get fallback opportunities when AI fails"""
        return {
            "new_opportunities": [
                {
                    "id": "fallback_1",
                    "title": "B2B Subscription Service",
                    "type": "new_revenue_stream",
                    "description": "Launch a subscription-based service for enterprise clients",
                    "potential_revenue": "$200,000/year",
                    "investment_required": "$50,000",
                    "time_to_market": "4 months",
                    "feasibility_score": 0.85,
                    "alignment_with_current_business": 0.90,
                    "key_advantages": [
                        "Leverages existing technology",
                        "Utilizes current customer base",
                        "Creates recurring revenue"
                    ],
                    "implementation_steps": [
                        "Develop enterprise features",
                        "Create pricing tiers",
                        "Build sales team for B2B",
                        "Establish support infrastructure"
                    ],
                    "risks": ["longer_sales_cycle", "higher_support_costs"],
                    "success_probability": 0.75
                }
            ],
            "partnership_opportunities": [],
            "market_expansions": [],
            "innovation_suggestions": [],
            "prioritized_recommendations": [
                {
                    "rank": 1,
                    "suggestion_id": "fallback_1",
                    "reason": "Highest ROI and alignment with current business",
                    "expected_value": "$200,000/year"
                }
            ]
        }
