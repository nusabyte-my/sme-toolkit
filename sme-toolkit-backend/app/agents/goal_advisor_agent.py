"""Goal Advisor Agent - SMART goal generation and tracking"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.prompts.goal_advisor_prompts import GOAL_ADVISOR_PROMPTS
from app.services.goal_service import GoalService
from app.database import GoalPriority, GoalStatus

logger = logging.getLogger(__name__)


class GoalAdvisorAgent(BaseAgent):
    """
    Agent for generating SMART goals, aligning with BMC, tracking progress,
    and providing goal recommendations.
    """

    def __init__(self, goal_service: Optional[GoalService] = None):
        self.goal_service = goal_service
        self.gemini_client = get_gemini_client()

    @property
    def name(self) -> str:
        return "Goal Advisor Agent"

    def get_actions(self) -> list:
        return [
            "generate_smart_goals",
            "align_with_bmc",
            "track_progress",
            "recommend_goals",
            "calculate_feasibility"
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
            if action == "generate_smart_goals":
                return await self.generate_smart_goals(
                    business_context=input_data.get("business_context", {}),
                    bmc_data=input_data.get("bmc_data", {}),
                    metrics=input_data.get("metrics", {}),
                    resources=input_data.get("resources", {}),
                    business_profile_id=input_data.get("business_profile_id")
                )
            elif action == "align_with_bmc":
                return await self.align_with_bmc(
                    goal=input_data.get("goal"),
                    bmc_data=input_data.get("bmc_data", {})
                )
            elif action == "track_progress":
                return await self.track_progress(
                    goal_id=input_data.get("goal_id"),
                    current_metrics=input_data.get("current_metrics", {})
                )
            elif action == "recommend_goals":
                return await self.recommend_goals(
                    business_context=input_data.get("business_context", {}),
                    bmc_data=input_data.get("bmc_data", {}),
                    current_goals=input_data.get("current_goals", []),
                    business_stage=input_data.get("business_stage", "growth"),
                    industry=input_data.get("industry", "general")
                )
            elif action == "calculate_feasibility":
                return await self.calculate_feasibility(
                    goal=input_data.get("goal"),
                    resources=input_data.get("resources", {}),
                    metrics=input_data.get("metrics", {}),
                    historical_performance=input_data.get("historical_performance", [])
                )
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": self.get_actions()
                }
        except Exception as e:
            logger.error(f"Error in GoalAdvisorAgent.invoke: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "fallback_response": self._get_fallback_response(action)
            }

    async def generate_smart_goals(
        self,
        business_context: Dict[str, Any],
        bmc_data: Dict[str, Any],
        metrics: Dict[str, Any],
        resources: Dict[str, Any],
        business_profile_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate SMART goals based on business context.
        
        Args:
            business_context: Business context information
            bmc_data: Business Model Canvas data
            metrics: Current business metrics
            resources: Available resources
            business_profile_id: Optional business profile ID for storage
            
        Returns:
            Generated goals with SMART criteria
        """
        try:
            logger.info("Generating SMART goals")
            
            # Prepare prompt
            prompt = GOAL_ADVISOR_PROMPTS["GENERATE_SMART_GOALS"].format(
                business_context=self._format_context(business_context),
                bmc_data=self._format_bmc(bmc_data),
                metrics=self._format_metrics(metrics),
                resources=self._format_resources(resources)
            )
            
            # Generate goals using AI
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Parse and structure goals
            goals = self._parse_goals_response(response)
            
            # Store goals if business_profile_id provided
            stored_goals = []
            if business_profile_id and self.goal_service:
                for goal_data in goals:
                    try:
                        stored_goal = await self.goal_service.create_goal(
                            business_profile_id=business_profile_id,
                            title=goal_data.get("title", ""),
                            description=goal_data.get("description"),
                            category=goal_data.get("category"),
                            priority=self._parse_priority(goal_data.get("priority", "medium")),
                            deadline=self._parse_date(goal_data.get("estimated_completion")),
                            smart_criteria=goal_data.get("smart_criteria"),
                            bmc_alignment=goal_data.get("bmc_alignment"),
                            milestones=goal_data.get("key_milestones"),
                            success_metrics=goal_data.get("success_metrics")
                        )
                        stored_goals.append(stored_goal)
                    except Exception as e:
                        logger.warning(f"Failed to store goal: {e}")
                        continue
            
            # Calculate goal analysis
            goal_analysis = self._calculate_goal_analysis(goals, bmc_data)
            
            return {
                "success": True,
                "goals": goals,
                "stored_goals": stored_goals if stored_goals else None,
                "goal_analysis": goal_analysis
            }
            
        except Exception as e:
            logger.error(f"Error generating SMART goals: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "goals": [],
                "fallback_response": self._get_fallback_goals(business_context)
            }

    async def align_with_bmc(
        self,
        goal: Dict[str, Any],
        bmc_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze goal alignment with Business Model Canvas.
        
        Args:
            goal: Goal data
            bmc_data: Business Model Canvas data
            
        Returns:
            Alignment analysis with scores and recommendations
        """
        try:
            logger.info(f"Analyzing BMC alignment for goal: {goal.get('title', 'Unknown')}")
            
            # Prepare prompt
            prompt = GOAL_ADVISOR_PROMPTS["ALIGN_WITH_BMC"].format(
                goal_title=goal.get("title", ""),
                goal_description=goal.get("description", ""),
                bmc_data=self._format_bmc(bmc_data)
            )
            
            # Generate alignment analysis
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Structure alignment data
            alignment = {
                "aligned_blocks": response.get("aligned_blocks", []),
                "alignment_score": response.get("alignment_score", 0),
                "alignment_rationale": response.get("alignment_rationale", ""),
                "gaps": response.get("gaps", []),
                "recommendations": response.get("recommendations", [])
            }
            
            return {
                "success": True,
                "alignment": alignment
            }
            
        except Exception as e:
            logger.error(f"Error analyzing BMC alignment: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "alignment": {
                    "aligned_blocks": [],
                    "alignment_score": 0,
                    "alignment_rationale": "Unable to analyze alignment",
                    "gaps": [],
                    "recommendations": []
                }
            }

    async def track_progress(
        self,
        goal_id: str,
        current_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Track goal progress and provide recommendations.
        
        Args:
            goal_id: Goal ID
            current_metrics: Current business metrics
            
        Returns:
            Progress report with recommendations
        """
        try:
            logger.info(f"Tracking progress for goal: {goal_id}")
            
            # Get goal data
            goal = None
            if self.goal_service:
                goal = await self.goal_service.get_goal(goal_id)
            
            if not goal:
                return {
                    "success": False,
                    "error": f"Goal {goal_id} not found",
                    "progress_report": None
                }
            
            # Prepare prompt
            prompt = GOAL_ADVISOR_PROMPTS["TRACK_PROGRESS"].format(
                goal_title=goal.get("title", ""),
                progress=goal.get("progress", 0),
                deadline=goal.get("deadline", "Not set"),
                milestones=self._format_milestones(goal.get("milestones", [])),
                success_metrics=self._format_list(goal.get("success_metrics", [])),
                current_metrics=self._format_metrics(current_metrics)
            )
            
            # Generate progress analysis
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Structure progress report
            progress_report = {
                "goal_id": goal_id,
                "overall_assessment": response.get("overall_progress_assessment", "unknown"),
                "milestone_progress": response.get("milestone_progress", []),
                "metric_analysis": response.get("metric_analysis", {}),
                "progress_score": response.get("progress_score", 0),
                "recommendations": response.get("recommendations", []),
                "risk_assessment": response.get("risk_assessment", {}),
                "adjustment_suggestions": response.get("adjustment_suggestions", [])
            }
            
            return {
                "success": True,
                "progress_report": progress_report
            }
            
        except Exception as e:
            logger.error(f"Error tracking progress: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "progress_report": None
            }

    async def recommend_goals(
        self,
        business_context: Dict[str, Any],
        bmc_data: Dict[str, Any],
        current_goals: List[Dict[str, Any]],
        business_stage: str = "growth",
        industry: str = "general"
    ) -> Dict[str, Any]:
        """
        Generate goal recommendations based on business context.
        
        Args:
            business_context: Business context information
            bmc_data: Business Model Canvas data
            current_goals: List of existing goals
            business_stage: Business stage (startup, growth, established)
            industry: Industry type
            
        Returns:
            Goal recommendations with feasibility scores
        """
        try:
            logger.info("Generating goal recommendations")
            
            # Prepare prompt
            prompt = GOAL_ADVISOR_PROMPTS["RECOMMEND_GOALS"].format(
                business_context=self._format_context(business_context),
                bmc_data=self._format_bmc(bmc_data),
                current_goals=self._format_goals_list(current_goals),
                business_stage=business_stage,
                industry=industry
            )
            
            # Generate recommendations
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Parse recommendations
            recommendations = self._parse_recommendations_response(response)
            
            return {
                "success": True,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error generating goal recommendations: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "recommendations": []
            }

    async def calculate_feasibility(
        self,
        goal: Dict[str, Any],
        resources: Dict[str, Any],
        metrics: Dict[str, Any],
        historical_performance: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate feasibility score for a goal.
        
        Args:
            goal: Goal data
            resources: Available resources
            metrics: Current business metrics
            historical_performance: Historical goal performance data
            
        Returns:
            Feasibility analysis with score and recommendations
        """
        try:
            logger.info(f"Calculating feasibility for goal: {goal.get('title', 'Unknown')}")
            
            # Prepare prompt
            prompt = GOAL_ADVISOR_PROMPTS["CALCULATE_FEASIBILITY"].format(
                goal_title=goal.get("title", ""),
                goal_description=goal.get("description", ""),
                required_resources=self._format_resources(goal.get("required_resources", {})),
                timeline=goal.get("timeline", "Not specified"),
                available_resources=self._format_resources(resources),
                metrics=self._format_metrics(metrics),
                historical_performance=self._format_historical_performance(historical_performance)
            )
            
            # Generate feasibility analysis
            response = await self.gemini_client.generate_json(
                prompt=prompt,
                use_pro=True
            )
            
            # Structure feasibility data
            feasibility = {
                "feasibility_score": response.get("feasibility_score", 0),
                "resource_analysis": response.get("resource_analysis", {}),
                "timeline_analysis": response.get("timeline_analysis", {}),
                "risk_factors": response.get("risk_factors", []),
                "success_probability": response.get("success_probability", 0),
                "recommendations": response.get("recommendations", []),
                "alternative_approaches": response.get("alternative_approaches", [])
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
                    "feasibility_score": 0,
                    "resource_analysis": {},
                    "timeline_analysis": {},
                    "risk_factors": [],
                    "success_probability": 0,
                    "recommendations": [],
                    "alternative_approaches": []
                }
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

    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format metrics for prompt"""
        if not metrics:
            return "No metrics provided"
        return "\n".join([f"- {k}: {v}" for k, v in metrics.items()])

    def _format_resources(self, resources: Dict[str, Any]) -> str:
        """Format resources for prompt"""
        if not resources:
            return "No resources provided"
        return "\n".join([f"- {k}: {v}" for k, v in resources.items()])

    def _format_milestones(self, milestones: List[Dict[str, Any]]) -> str:
        """Format milestones for prompt"""
        if not milestones:
            return "No milestones"
        return "\n".join([f"- {m.get('milestone', 'Unknown')}: {m.get('target_date', 'No date')}" for m in milestones])

    def _format_list(self, items: List[str]) -> str:
        """Format list for prompt"""
        if not items:
            return "None"
        return "\n".join([f"- {item}" for item in items])

    def _format_goals_list(self, goals: List[Dict[str, Any]]) -> str:
        """Format goals list for prompt"""
        if not goals:
            return "No current goals"
        return "\n".join([f"- {g.get('title', 'Unknown')}: {g.get('description', 'No description')}" for g in goals])

    def _format_historical_performance(self, performance: List[Dict[str, Any]]) -> str:
        """Format historical performance for prompt"""
        if not performance:
            return "No historical performance data"
        return "\n".join([f"- Goal: {p.get('goal_title', 'Unknown')}, Success: {p.get('success', 'N/A')}" for p in performance])

    def _parse_goals_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse AI response into goal objects"""
        goals = response.get("goals", [])
        if not isinstance(goals, list):
            goals = []
        
        parsed_goals = []
        for i, goal in enumerate(goals):
            parsed_goals.append({
                "id": f"goal_{i+1}",
                "title": goal.get("title", ""),
                "description": goal.get("description", ""),
                "category": goal.get("category", "general"),
                "smart_criteria": goal.get("smart_criteria", {}),
                "bmc_alignment": goal.get("bmc_alignment", {}),
                "priority": goal.get("priority", "medium"),
                "estimated_completion": goal.get("estimated_completion"),
                "key_milestones": goal.get("key_milestones", []),
                "required_resources": goal.get("required_resources", []),
                "potential_obstacles": goal.get("potential_obstacles", []),
                "success_metrics": goal.get("success_metrics", [])
            })
        
        return parsed_goals

    def _parse_recommendations_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse AI response into recommendation objects"""
        recommendations = response.get("recommendations", [])
        if not isinstance(recommendations, list):
            recommendations = []
        
        parsed_recommendations = []
        for i, rec in enumerate(recommendations):
            parsed_recommendations.append({
                "id": f"rec_{i+1}",
                "title": rec.get("goal_title", ""),
                "description": rec.get("description", ""),
                "category": rec.get("category", "general"),
                "priority": rec.get("priority", "medium"),
                "rationale": rec.get("rationale", ""),
                "expected_impact": rec.get("expected_impact", ""),
                "feasibility": rec.get("feasibility", 0),
                "dependencies": rec.get("dependencies", []),
                "timeline": rec.get("timeline", "")
            })
        
        return parsed_recommendations

    def _parse_priority(self, priority_str: str) -> GoalPriority:
        """Parse priority string to enum"""
        priority_map = {
            "high": GoalPriority.HIGH,
            "medium": GoalPriority.MEDIUM,
            "low": GoalPriority.LOW
        }
        return priority_map.get(priority_str.lower(), GoalPriority.MEDIUM)

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except:
            return None

    def _calculate_goal_analysis(
        self,
        goals: List[Dict[str, Any]],
        bmc_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate goal analysis statistics"""
        total_goals = len(goals)
        
        # Count by category
        by_category = {}
        for goal in goals:
            category = goal.get("category", "uncategorized")
            by_category[category] = by_category.get(category, 0) + 1
        
        # Calculate average alignment score
        alignment_scores = [goal.get("bmc_alignment", {}).get("alignment_score", 0) for goal in goals]
        avg_alignment = sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0
        
        # Calculate average feasibility
        feasibility_scores = [goal.get("feasibility", 0) for goal in goals if "feasibility" in goal]
        avg_feasibility = sum(feasibility_scores) / len(feasibility_scores) if feasibility_scores else 0
        
        return {
            "total_goals": total_goals,
            "by_category": by_category,
            "alignment_score": round(avg_alignment, 2),
            "feasibility_score": round(avg_feasibility, 2),
            "recommendations": [
                "Review goals quarterly to ensure alignment with business objectives",
                "Break down large goals into smaller, manageable milestones",
                "Ensure each goal has clear success metrics"
            ]
        }

    def _get_fallback_response(self, action: str) -> Dict[str, Any]:
        """Get fallback response for failed actions"""
        fallbacks = {
            "generate_smart_goals": {
                "goals": [],
                "message": "Unable to generate goals. Please provide more business context."
            },
            "align_with_bmc": {
                "alignment": {
                    "aligned_blocks": [],
                    "alignment_score": 0,
                    "message": "Unable to analyze alignment"
                }
            },
            "track_progress": {
                "progress_report": {
                    "message": "Unable to track progress"
                }
            },
            "recommend_goals": {
                "recommendations": [],
                "message": "Unable to generate recommendations"
            },
            "calculate_feasibility": {
                "feasibility": {
                    "feasibility_score": 0,
                    "message": "Unable to calculate feasibility"
                }
            }
        }
        return fallbacks.get(action, {"message": "Unknown action"})

    def _get_fallback_goals(self, business_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get fallback goals when AI fails"""
        return [
            {
                "id": "fallback_1",
                "title": "Increase Revenue",
                "description": "Focus on increasing monthly revenue through sales and marketing efforts",
                "category": "financial",
                "priority": "high",
                "smart_criteria": {
                    "specific": "Increase monthly revenue by 20%",
                    "measurable": "Track through revenue reports",
                    "achievable": "Based on current growth trends",
                    "relevant": "Supports business expansion",
                    "time_bound": "Within 6 months"
                },
                "bmc_alignment": {
                    "aligned_blocks": ["revenue_streams"],
                    "alignment_score": 0.7,
                    "gaps": []
                },
                "estimated_completion": "2024-06-30",
                "key_milestones": [
                    {
                        "milestone": "Reach 10% increase",
                        "target_date": "2024-03-31",
                        "metrics": ["monthly_revenue"]
                    }
                ],
                "required_resources": ["marketing_budget", "sales_team"],
                "potential_obstacles": ["market_competition", "economic_conditions"],
                "success_metrics": ["monthly_revenue", "customer_acquisition"]
            }
        ]
