"""Conflict Resolution Strategy - Handle conflicting recommendations from agents"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConflictType(str, Enum):
    """Types of conflicts that can occur"""
    GOAL_CONFLICT = "goal_conflict"  # Growth vs cost reduction
    PRIORITY_CONFLICT = "priority_conflict"  # Different priorities for same action
    RESOURCE_CONFLICT = "resource_conflict"  # Competing resource allocation
    TIMELINE_CONFLICT = "timeline_conflict"  # Conflicting timelines
    STRATEGY_CONFLICT = "strategy_conflict"  # Different strategic approaches


class Conflict:
    """Represents a conflict between agent recommendations"""
    
    def __init__(
        self,
        conflict_type: ConflictType,
        agents_involved: List[str],
        description: str,
        severity: str = "medium",  # low, medium, high
        recommendations: Optional[List[Dict[str, Any]]] = None
    ):
        self.conflict_type = conflict_type
        self.agents_involved = agents_involved
        self.description = description
        self.severity = severity
        self.recommendations = recommendations or []
        self.resolution: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conflict to dictionary"""
        return {
            "conflict_type": self.conflict_type.value,
            "agents_involved": self.agents_involved,
            "description": self.description,
            "severity": self.severity,
            "recommendations": self.recommendations,
            "resolution": self.resolution
        }


class ConflictResolutionStrategy:
    """Strategy for resolving conflicts"""
    
    WEIGHTED_SCORING = "weighted_scoring"
    USER_PREFERENCE = "user_preference"
    HISTORICAL_SUCCESS = "historical_success"
    RISK_ASSESSMENT = "risk_assessment"
    COMPROMISE = "compromise"
    PRIORITY_BASED = "priority_based"


class ConflictResolver:
    """Main conflict resolution engine"""
    
    def __init__(self, user_preferences: Optional[Dict[str, Any]] = None):
        self.user_preferences = user_preferences or {}
        self.historical_success_rates: Dict[str, float] = {}
        self.conflicts: List[Conflict] = []
    
    def detect_conflicts(self, agent_results: Dict[str, Any]) -> List[Conflict]:
        """
        Detect conflicts between agent recommendations.
        
        Args:
            agent_results: Results from multiple agents
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Check for goal conflicts (growth vs cost reduction)
        conflicts.extend(self._detect_goal_conflicts(agent_results))
        
        # Check for priority conflicts
        conflicts.extend(self._detect_priority_conflicts(agent_results))
        
        # Check for resource conflicts
        conflicts.extend(self._detect_resource_conflicts(agent_results))
        
        # Check for timeline conflicts
        conflicts.extend(self._detect_timeline_conflicts(agent_results))
        
        # Check for strategy conflicts
        conflicts.extend(self._detect_strategy_conflicts(agent_results))
        
        self.conflicts = conflicts
        logger.info(f"Detected {len(conflicts)} conflicts")
        
        return conflicts
    
    def _detect_goal_conflicts(self, agent_results: Dict[str, Any]) -> List[Conflict]:
        """Detect conflicts between growth and cost reduction goals"""
        conflicts = []
        
        growth_result = agent_results.get("growth", {})
        costing_result = agent_results.get("costing", {})
        
        # Check if growth advisor recommends aggressive expansion
        # while costing advisor recommends cost cutting
        if growth_result and costing_result:
            growth_plan = growth_result.get("growth_plan", {})
            cost_analysis = costing_result.get("cost_structure", {})
            
            # Look for aggressive growth indicators
            growth_opportunities = growth_plan.get("growth_opportunities", [])
            aggressive_growth = any(
                opp.get("confidence_score", 0) > 0.8
                for opp in growth_opportunities
            )
            
            # Look for cost cutting indicators
            optimization_opps = cost_analysis.get("optimization_opportunities", [])
            aggressive_cost_cutting = any(
                opt.get("savings_percentage", 0) > 20
                for opt in optimization_opps
            )
            
            if aggressive_growth and aggressive_cost_cutting:
                conflicts.append(Conflict(
                    conflict_type=ConflictType.GOAL_CONFLICT,
                    agents_involved=["Growth Plan Advisor", "Costing Advisor"],
                    description="Aggressive growth recommendations conflict with aggressive cost-cutting measures",
                    severity="high",
                    recommendations=[
                        {
                            "source": "Growth Plan Advisor",
                            "recommendation": "Invest in growth opportunities",
                            "rationale": "High confidence growth opportunities identified"
                        },
                        {
                            "source": "Costing Advisor",
                            "recommendation": "Implement cost-cutting measures",
                            "rationale": "Significant cost savings available"
                        }
                    ]
                ))
        
        return conflicts
    
    def _detect_priority_conflicts(self, agent_results: Dict[str, Any]) -> List[Conflict]:
        """Detect conflicts in priority recommendations"""
        conflicts = []
        
        # Check if different agents recommend different priorities for similar actions
        goal_result = agent_results.get("goals", {})
        growth_result = agent_results.get("growth", {})
        
        if goal_result and growth_result:
            goals = goal_result.get("goals", [])
            growth_channels = growth_result.get("growth_plan", {}).get("growth_channels", [])
            
            # Look for conflicting priorities
            for goal in goals:
                goal_priority = goal.get("priority", "medium")
                goal_category = goal.get("category", "")
                
                # Check if growth advisor has different priority for similar area
                for channel in growth_channels:
                    channel_priority = channel.get("priority", "medium")
                    
                    # Simple heuristic: if priorities differ significantly
                    if (goal_priority == "high" and channel_priority == "low") or \
                       (goal_priority == "low" and channel_priority == "high"):
                        conflicts.append(Conflict(
                            conflict_type=ConflictType.PRIORITY_CONFLICT,
                            agents_involved=["Goal Advisor", "Growth Plan Advisor"],
                            description=f"Priority conflict for {goal_category} initiatives",
                            severity="medium",
                            recommendations=[
                                {
                                    "source": "Goal Advisor",
                                    "recommendation": f"Priority: {goal_priority}",
                                    "rationale": goal.get("description", "")
                                },
                                {
                                    "source": "Growth Plan Advisor",
                                    "recommendation": f"Priority: {channel_priority}",
                                    "rationale": channel.get("expected_impact", "")
                                }
                            ]
                        ))
        
        return conflicts
    
    def _detect_resource_conflicts(self, agent_results: Dict[str, Any]) -> List[Conflict]:
        """Detect conflicts in resource allocation"""
        conflicts = []
        
        growth_result = agent_results.get("growth", {})
        suggestion_result = agent_results.get("suggestions", {})
        
        if growth_result and suggestion_result:
            growth_resources = growth_result.get("growth_plan", {}).get("resource_requirements", {})
            suggestions = suggestion_result.get("business_suggestions", {}).get("new_opportunities", [])
            
            # Check if multiple initiatives require same resources
            team_needs = growth_resources.get("team", [])
            budget_needs = growth_resources.get("budget", "")
            
            for suggestion in suggestions:
                suggestion_resources = suggestion.get("required_resources", [])
                
                # Check for overlapping resource needs
                overlapping = set(team_needs) & set(suggestion_resources)
                if overlapping:
                    conflicts.append(Conflict(
                        conflict_type=ConflictType.RESOURCE_CONFLICT,
                        agents_involved=["Growth Plan Advisor", "Business Suggestion Agent"],
                        description=f"Resource conflict: {', '.join(overlapping)} needed by multiple initiatives",
                        severity="medium",
                        recommendations=[
                            {
                                "source": "Growth Plan Advisor",
                                "recommendation": f"Allocate resources to growth plan",
                                "rationale": "Growth plan requires these resources"
                            },
                            {
                                "source": "Business Suggestion Agent",
                                "recommendation": f"Allocate resources to {suggestion.get('title', 'suggestion')}",
                                "rationale": suggestion.get("description", "")
                            }
                        ]
                    ))
        
        return conflicts
    
    def _detect_timeline_conflicts(self, agent_results: Dict[str, Any]) -> List[Conflict]:
        """Detect conflicts in implementation timelines"""
        conflicts = []
        
        goal_result = agent_results.get("goals", {})
        growth_result = agent_results.get("growth", {})
        
        if goal_result and growth_result:
            goals = goal_result.get("goals", [])
            growth_roadmap = growth_result.get("growth_plan", {}).get("implementation_roadmap", [])
            
            # Check for overlapping timelines
            for goal in goals:
                goal_deadline = goal.get("estimated_completion")
                
                for phase in growth_roadmap:
                    phase_duration = phase.get("duration", "")
                    
                    # Simple heuristic: if both have tight timelines
                    if goal_deadline and "month" in phase_duration.lower():
                        conflicts.append(Conflict(
                            conflict_type=ConflictType.TIMELINE_CONFLICT,
                            agents_involved=["Goal Advisor", "Growth Plan Advisor"],
                            description=f"Timeline conflict: Goal deadline {goal_deadline} vs growth phase {phase_duration}",
                            severity="low",
                            recommendations=[
                                {
                                    "source": "Goal Advisor",
                                    "recommendation": f"Complete goal by {goal_deadline}",
                                    "rationale": "Goal deadline established"
                                },
                                {
                                    "source": "Growth Plan Advisor",
                                    "recommendation": f"Execute phase: {phase.get('phase', 'Unknown')}",
                                    "rationale": phase.get("description", "")
                                }
                            ]
                        ))
        
        return conflicts
    
    def _detect_strategy_conflicts(self, agent_results: Dict[str, Any]) -> List[Conflict]:
        """Detect conflicts in strategic approaches"""
        conflicts = []
        
        # Check for conflicting strategic directions
        growth_result = agent_results.get("growth", {})
        suggestion_result = agent_results.get("suggestions", {})
        
        if growth_result and suggestion_result:
            growth_opportunities = growth_result.get("growth_plan", {}).get("growth_opportunities", [])
            suggestions = suggestion_result.get("business_suggestions", {}).get("new_opportunities", [])
            
            # Check if growth focuses on expansion while suggestions focus on optimization
            expansion_focus = any(
                opp.get("type", "") == "market_expansion"
                for opp in growth_opportunities
            )
            
            optimization_focus = any(
                sug.get("type", "") == "product_innovation"
                for sug in suggestions
            )
            
            if expansion_focus and optimization_focus:
                conflicts.append(Conflict(
                    conflict_type=ConflictType.STRATEGY_CONFLICT,
                    agents_involved=["Growth Plan Advisor", "Business Suggestion Agent"],
                    description="Strategic conflict: Market expansion vs product innovation focus",
                    severity="medium",
                    recommendations=[
                        {
                            "source": "Growth Plan Advisor",
                            "recommendation": "Focus on market expansion",
                            "rationale": "High-potential expansion opportunities identified"
                        },
                        {
                            "source": "Business Suggestion Agent",
                            "recommendation": "Focus on product innovation",
                            "rationale": "Innovation opportunities available"
                        }
                    ]
                ))
        
        return conflicts
    
    def resolve_conflicts(
        self,
        conflicts: List[Conflict],
        strategy: str = ConflictResolutionStrategy.WEIGHTED_SCORING
    ) -> Dict[str, Any]:
        """
        Resolve conflicts using specified strategy.
        
        Args:
            conflicts: List of conflicts to resolve
            strategy: Resolution strategy to use
            
        Returns:
            Resolution results with recommendations
        """
        resolutions = {}
        
        for conflict in conflicts:
            if strategy == ConflictResolutionStrategy.WEIGHTED_SCORING:
                resolution = self._resolve_with_weighted_scoring(conflict)
            elif strategy == ConflictResolutionStrategy.USER_PREFERENCE:
                resolution = self._resolve_with_user_preference(conflict)
            elif strategy == ConflictResolutionStrategy.HISTORICAL_SUCCESS:
                resolution = self._resolve_with_historical_success(conflict)
            elif strategy == ConflictResolutionStrategy.RISK_ASSESSMENT:
                resolution = self._resolve_with_risk_assessment(conflict)
            elif strategy == ConflictResolutionStrategy.COMPROMISE:
                resolution = self._resolve_with_compromise(conflict)
            elif strategy == ConflictResolutionStrategy.PRIORITY_BASED:
                resolution = self._resolve_with_priority(conflict)
            else:
                resolution = self._resolve_with_weighted_scoring(conflict)
            
            conflict.resolution = resolution
            resolutions[conflict.conflict_type.value] = resolution
        
        logger.info(f"Resolved {len(resolutions)} conflicts using {strategy}")
        
        return {
            "total_conflicts": len(conflicts),
            "resolved_conflicts": len(resolutions),
            "strategy_used": strategy,
            "resolutions": resolutions
        }
    
    def _resolve_with_weighted_scoring(self, conflict: Conflict) -> Dict[str, Any]:
        """Resolve conflict using weighted scoring based on business priorities"""
        # Default weights (can be customized via user preferences)
        weights = self.user_preferences.get("weights", {
            "growth": 0.35,
            "cost_efficiency": 0.25,
            "feasibility": 0.20,
            "alignment": 0.20
        })
        
        # Score each recommendation
        scored_recommendations = []
        for rec in conflict.recommendations:
            score = 0.0
            
            # Simple scoring based on recommendation content
            source = rec.get("source", "")
            if "Growth" in source:
                score += weights.get("growth", 0.35)
            if "Costing" in source:
                score += weights.get("cost_efficiency", 0.25)
            
            # Add feasibility factor
            if "confidence_score" in rec:
                score *= rec["confidence_score"]
            
            scored_recommendations.append({
                **rec,
                "score": score
            })
        
        # Select highest scored recommendation
        best = max(scored_recommendations, key=lambda x: x.get("score", 0))
        
        return {
            "strategy": "weighted_scoring",
            "selected_recommendation": best,
            "weights_used": weights,
            "all_scores": scored_recommendations,
            "rationale": f"Selected recommendation with highest weighted score: {best.get('score', 0):.2f}"
        }
    
    def _resolve_with_user_preference(self, conflict: Conflict) -> Dict[str, Any]:
        """Resolve conflict using user preferences"""
        # Check if user has preference for this conflict type
        conflict_type = conflict.conflict_type.value
        user_pref = self.user_preferences.get(conflict_type, {})
        
        if user_pref:
            # Find recommendation matching user preference
            preferred_agent = user_pref.get("preferred_agent")
            for rec in conflict.recommendations:
                if preferred_agent in rec.get("source", ""):
                    return {
                        "strategy": "user_preference",
                        "selected_recommendation": rec,
                        "user_preference": user_pref,
                        "rationale": f"Selected based on user preference for {preferred_agent}"
                    }
        
        # Fallback to weighted scoring
        return self._resolve_with_weighted_scoring(conflict)
    
    def _resolve_with_historical_success(self, conflict: Conflict) -> Dict[str, Any]:
        """Resolve conflict using historical success rates"""
        # Score recommendations based on historical success
        scored_recommendations = []
        for rec in conflict.recommendations:
            source = rec.get("source", "")
            success_rate = self.historical_success_rates.get(source, 0.7)  # Default 70%
            
            scored_recommendations.append({
                **rec,
                "success_rate": success_rate,
                "score": success_rate
            })
        
        # Select highest success rate
        best = max(scored_recommendations, key=lambda x: x.get("score", 0))
        
        return {
            "strategy": "historical_success",
            "selected_recommendation": best,
            "success_rates": self.historical_success_rates,
            "rationale": f"Selected recommendation with highest historical success rate: {best.get('success_rate', 0):.2%}"
        }
    
    def _resolve_with_risk_assessment(self, conflict: Conflict) -> Dict[str, Any]:
        """Resolve conflict using risk assessment"""
        # Score recommendations based on risk level
        scored_recommendations = []
        for rec in conflict.recommendations:
            # Lower risk = higher score
            risk_level = rec.get("risk_level", "medium")
            risk_score = {
                "low": 1.0,
                "medium": 0.7,
                "high": 0.4
            }.get(risk_level, 0.7)
            
            scored_recommendations.append({
                **rec,
                "risk_level": risk_level,
                "score": risk_score
            })
        
        # Select lowest risk
        best = max(scored_recommendations, key=lambda x: x.get("score", 0))
        
        return {
            "strategy": "risk_assessment",
            "selected_recommendation": best,
            "rationale": f"Selected recommendation with lowest risk level: {best.get('risk_level', 'medium')}"
        }
    
    def _resolve_with_compromise(self, conflict: Conflict) -> Dict[str, Any]:
        """Resolve conflict by creating a compromise"""
        # Create a compromise recommendation
        if len(conflict.recommendations) >= 2:
            rec1 = conflict.recommendations[0]
            rec2 = conflict.recommendations[1]
            
            compromise = {
                "source": "Compromise",
                "recommendation": f"Combine {rec1.get('source')} and {rec2.get('source')} approaches",
                "rationale": f"Balanced approach addressing both {rec1.get('source')} and {rec2.get('source')} recommendations",
                "compromise_of": [rec1.get("source"), rec2.get("source")],
                "implementation": {
                    "phase_1": rec1.get("recommendation"),
                    "phase_2": rec2.get("recommendation")
                }
            }
            
            return {
                "strategy": "compromise",
                "selected_recommendation": compromise,
                "rationale": "Created compromise solution balancing both recommendations"
            }
        
        # Fallback to first recommendation
        return {
            "strategy": "compromise",
            "selected_recommendation": conflict.recommendations[0] if conflict.recommendations else {},
            "rationale": "Insufficient recommendations for compromise, selected first option"
        }
    
    def _resolve_with_priority(self, conflict: Conflict) -> Dict[str, Any]:
        """Resolve conflict based on priority levels"""
        # Score recommendations based on priority
        priority_scores = {
            "high": 1.0,
            "medium": 0.7,
            "low": 0.4
        }
        
        scored_recommendations = []
        for rec in conflict.recommendations:
            priority = rec.get("priority", "medium")
            score = priority_scores.get(priority, 0.7)
            
            scored_recommendations.append({
                **rec,
                "priority": priority,
                "score": score
            })
        
        # Select highest priority
        best = max(scored_recommendations, key=lambda x: x.get("score", 0))
        
        return {
            "strategy": "priority_based",
            "selected_recommendation": best,
            "rationale": f"Selected recommendation with highest priority: {best.get('priority', 'medium')}"
        }
    
    def update_historical_success(self, agent_name: str, success: bool) -> None:
        """Update historical success rate for an agent"""
        current_rate = self.historical_success_rates.get(agent_name, 0.7)
        
        # Simple moving average
        new_rate = (current_rate * 0.9) + (1.0 if success else 0.0) * 0.1
        self.historical_success_rates[agent_name] = new_rate
        
        logger.debug(f"Updated success rate for {agent_name}: {new_rate:.2%}")
    
    def get_conflict_summary(self) -> Dict[str, Any]:
        """Get summary of all detected conflicts"""
        return {
            "total_conflicts": len(self.conflicts),
            "by_type": {
                conflict_type.value: len([c for c in self.conflicts if c.conflict_type == conflict_type])
                for conflict_type in ConflictType
            },
            "by_severity": {
                "high": len([c for c in self.conflicts if c.severity == "high"]),
                "medium": len([c for c in self.conflicts if c.severity == "medium"]),
                "low": len([c for c in self.conflicts if c.severity == "low"])
            },
            "conflicts": [c.to_dict() for c in self.conflicts]
        }
