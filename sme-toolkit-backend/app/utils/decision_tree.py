"""Decision Tree Implementation - Intelligent agent selection logic"""

from typing import Dict, Any, List, Optional, Set
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RequestType(str, Enum):
    """Types of user requests"""
    GOAL_SETTING = "goal_setting"
    GROWTH_PLANNING = "growth_planning"
    COST_ANALYSIS = "cost_analysis"
    BUSINESS_SUGGESTIONS = "business_suggestions"
    COMPREHENSIVE_ANALYSIS = "comprehensive_analysis"
    PROGRESS_TRACKING = "progress_tracking"
    FEASIBILITY_ASSESSMENT = "feasibility_assessment"
    STRATEGY_REVIEW = "strategy_review"


class AgentType(str, Enum):
    """Available advisor agents"""
    GOAL_ADVISOR = "goal_advisor"
    GROWTH_ADVISOR = "growth_advisor"
    COSTING_ADVISOR = "costing_advisor"
    SUGGESTION_ADVISOR = "suggestion_advisor"


class BusinessStage(str, Enum):
    """Business development stages"""
    STARTUP = "startup"
    GROWTH = "growth"
    ESTABLISHED = "established"


class DecisionFactor:
    """Represents a factor in the decision tree"""
    
    def __init__(
        self,
        name: str,
        weight: float,
        threshold: Optional[float] = None,
        required: bool = False
    ):
        self.name = name
        self.weight = weight
        self.threshold = threshold
        self.required = required
    
    def evaluate(self, context: Dict[str, Any]) -> float:
        """Evaluate this factor against context"""
        value = context.get(self.name, 0)
        
        if self.threshold is not None:
            # Binary evaluation: 1 if above threshold, 0 otherwise
            return 1.0 if value >= self.threshold else 0.0
        
        # Normalized evaluation (0-1)
        return min(1.0, max(0.0, float(value)))
    
    def is_satisfied(self, context: Dict[str, Any]) -> bool:
        """Check if this factor is satisfied"""
        if not self.required:
            return True
        
        return self.evaluate(context) > 0


class DecisionNode:
    """Node in the decision tree"""
    
    def __init__(
        self,
        name: str,
        factor: Optional[DecisionFactor] = None,
        children: Optional[Dict[str, 'DecisionNode']] = None,
        agents: Optional[List[AgentType]] = None,
        execution_mode: str = "parallel",
        priority: float = 1.0
    ):
        self.name = name
        self.factor = factor
        self.children = children or {}
        self.agents = agents or []
        self.execution_mode = execution_mode
        self.priority = priority
    
    def evaluate(self, context: Dict[str, Any]) -> Optional[List[AgentType]]:
        """Evaluate this node and return agents to execute"""
        # If this node has agents, return them
        if self.agents:
            return self.agents
        
        # If this node has a factor, evaluate it
        if self.factor:
            score = self.factor.evaluate(context)
            
            # If factor is not satisfied, return None
            if score == 0 and self.factor.required:
                return None
            
            # If factor is satisfied, evaluate children
            if score > 0:
                # Find best matching child
                best_child = None
                best_score = 0
                
                for child_name, child in self.children.items():
                    child_score = self._evaluate_child(child, context)
                    if child_score > best_score:
                        best_score = child_score
                        best_child = child
                
                if best_child:
                    return best_child.evaluate(context)
        
        return None
    
    def _evaluate_child(self, child: 'DecisionNode', context: Dict[str, Any]) -> float:
        """Evaluate a child node"""
        if child.factor:
            return child.factor.evaluate(context) * child.priority
        return child.priority


class DecisionTree:
    """Decision tree for intelligent agent selection"""
    
    def __init__(self):
        self.root = self._build_decision_tree()
        self.execution_history: List[Dict[str, Any]] = []
    
    def _build_decision_tree(self) -> DecisionNode:
        """Build decision tree structure"""
        # Root node - request type
        root = DecisionNode(
            name="request_type",
            factor=DecisionFactor("request_type", weight=1.0, required=True),
            children={}
        )
        
        # Goal Setting branch
        goal_node = DecisionNode(
            name="goal_setting",
            agents=[AgentType.GOAL_ADVISOR],
            execution_mode="sequential",
            priority=1.0
        )
        root.children[RequestType.GOAL_SETTING.value] = goal_node
        
        # Growth Planning branch
        growth_node = DecisionNode(
            name="growth_planning",
            factor=DecisionFactor("has_bmc_data", weight=0.8, threshold=0.5),
            children={}
        )
        
        # Has BMC data
        growth_with_bmc = DecisionNode(
            name="growth_with_bmc",
            agents=[AgentType.GROWTH_ADVISOR],
            execution_mode="sequential",
            priority=1.0
        )
        growth_node.children["has_bmc"] = growth_with_bmc
        
        # No BMC data
        growth_without_bmc = DecisionNode(
            name="growth_without_bmc",
            agents=[AgentType.GOAL_ADVISOR, AgentType.GROWTH_ADVISOR],
            execution_mode="sequential",
            priority=0.5
        )
        growth_node.children["no_bmc"] = growth_without_bmc
        
        root.children[RequestType.GROWTH_PLANNING.value] = growth_node
        
        # Cost Analysis branch
        cost_node = DecisionNode(
            name="cost_analysis",
            agents=[AgentType.COSTING_ADVISOR],
            execution_mode="sequential",
            priority=1.0
        )
        root.children[RequestType.COST_ANALYSIS.value] = cost_node
        
        # Business Suggestions branch
        suggestion_node = DecisionNode(
            name="business_suggestions",
            factor=DecisionFactor("has_market_data", weight=0.7, threshold=0.5),
            children={}
        )
        
        # Has market data
        suggestion_with_market = DecisionNode(
            name="suggestion_with_market",
            agents=[AgentType.SUGGESTION_ADVISOR],
            execution_mode="sequential",
            priority=1.0
        )
        suggestion_node.children["has_market"] = suggestion_with_market
        
        # No market data
        suggestion_without_market = DecisionNode(
            name="suggestion_without_market",
            agents=[AgentType.GOAL_ADVISOR, AgentType.SUGGESTION_ADVISOR],
            execution_mode="sequential",
            priority=0.6
        )
        suggestion_node.children["no_market"] = suggestion_without_market
        
        root.children[RequestType.BUSINESS_SUGGESTIONS.value] = suggestion_node
        
        # Comprehensive Analysis branch
        comprehensive_node = DecisionNode(
            name="comprehensive_analysis",
            factor=DecisionFactor("analysis_depth", weight=1.0),
            children={}
        )
        
        # Quick analysis
        quick_node = DecisionNode(
            name="quick_analysis",
            agents=[
                AgentType.GOAL_ADVISOR,
                AgentType.GROWTH_ADVISOR
            ],
            execution_mode="parallel",
            priority=0.8
        )
        comprehensive_node.children["quick"] = quick_node
        
        # Deep analysis
        deep_node = DecisionNode(
            name="deep_analysis",
            agents=[
                AgentType.GOAL_ADVISOR,
                AgentType.GROWTH_ADVISOR,
                AgentType.COSTING_ADVISOR,
                AgentType.SUGGESTION_ADVISOR
            ],
            execution_mode="sequential",
            priority=1.0
        )
        comprehensive_node.children["deep"] = deep_node
        
        root.children[RequestType.COMPREHENSIVE_ANALYSIS.value] = comprehensive_node
        
        # Progress Tracking branch
        progress_node = DecisionNode(
            name="progress_tracking",
            agents=[AgentType.GOAL_ADVISOR],
            execution_mode="sequential",
            priority=1.0
        )
        root.children[RequestType.PROGRESS_TRACKING.value] = progress_node
        
        # Feasibility Assessment branch
        feasibility_node = DecisionNode(
            name="feasibility_assessment",
            agents=[
                AgentType.GOAL_ADVISOR,
                AgentType.COSTING_ADVISOR
            ],
            execution_mode="sequential",
            priority=1.0
        )
        root.children[RequestType.FEASIBILITY_ASSESSMENT.value] = feasibility_node
        
        # Strategy Review branch
        strategy_node = DecisionNode(
            name="strategy_review",
            factor=DecisionFactor("business_stage", weight=1.0),
            children={}
        )
        
        # Startup stage
        startup_node = DecisionNode(
            name="startup_strategy",
            agents=[
                AgentType.GOAL_ADVISOR,
                AgentType.GROWTH_ADVISOR,
                AgentType.SUGGESTION_ADVISOR
            ],
            execution_mode="parallel",
            priority=1.0
        )
        strategy_node.children["startup"] = startup_node
        
        # Growth stage
        growth_stage_node = DecisionNode(
            name="growth_strategy",
            agents=[
                AgentType.GOAL_ADVISOR,
                AgentType.GROWTH_ADVISOR,
                AgentType.COSTING_ADVISOR
            ],
            execution_mode="parallel",
            priority=1.0
        )
        strategy_node.children["growth"] = growth_stage_node
        
        # Established stage
        established_node = DecisionNode(
            name="established_strategy",
            agents=[
                AgentType.GROWTH_ADVISOR,
                AgentType.COSTING_ADVISOR,
                AgentType.SUGGESTION_ADVISOR
            ],
            execution_mode="parallel",
            priority=1.0
        )
        strategy_node.children["established"] = established_node
        
        root.children[RequestType.STRATEGY_REVIEW.value] = strategy_node
        
        return root
    
    def determine_agents(
        self,
        request_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine which agents to execute based on request and context.
        
        Args:
            request_type: Type of user request
            context: Business context and available data
            
        Returns:
            Dictionary with agents, execution mode, and rationale
        """
        # Build evaluation context
        eval_context = {
            "request_type": request_type,
            "has_bmc_data": 1.0 if context.get("bmc_data") else 0.0,
            "has_market_data": 1.0 if context.get("market_data") else 0.0,
            "has_financial_data": 1.0 if context.get("financial_data") else 0.0,
            "analysis_depth": context.get("analysis_depth", "deep"),
            "business_stage": context.get("business_stage", "growth"),
            "resource_constraints": context.get("resource_constraints", 0.0),
            "time_constraints": context.get("time_constraints", 0.0)
        }
        
        # Evaluate decision tree
        agents = self.root.evaluate(eval_context)
        
        if not agents:
            # Fallback to comprehensive analysis
            agents = [
                AgentType.GOAL_ADVISOR,
                AgentType.GROWTH_ADVISOR,
                AgentType.COSTING_ADVISOR,
                AgentType.SUGGESTION_ADVISOR
            ]
            execution_mode = "sequential"
            rationale = "No specific match, using comprehensive analysis"
        else:
            # Find node that returned these agents
            execution_mode = self._find_execution_mode(agents, eval_context)
            rationale = self._generate_rationale(agents, eval_context)
        
        # Record decision
        decision_record = {
            "request_type": request_type,
            "context": eval_context,
            "selected_agents": [a.value for a in agents],
            "execution_mode": execution_mode,
            "rationale": rationale,
            "timestamp": context.get("timestamp")
        }
        self.execution_history.append(decision_record)
        
        logger.info(f"Decision tree selected agents: {[a.value for a in agents]}")
        
        return {
            "agents": agents,
            "execution_mode": execution_mode,
            "rationale": rationale,
            "decision_factors": eval_context
        }
    
    def _find_execution_mode(
        self,
        agents: List[AgentType],
        context: Dict[str, Any]
    ) -> str:
        """Determine execution mode based on agents and context"""
        # If only one agent, sequential
        if len(agents) == 1:
            return "sequential"
        
        # If multiple agents and no dependencies, parallel
        if not self._has_dependencies(agents):
            return "parallel"
        
        # If dependencies exist, sequential
        return "sequential"
    
    def _has_dependencies(self, agents: List[AgentType]) -> bool:
        """Check if agents have dependencies"""
        # Define dependencies
        dependencies = {
            AgentType.GROWTH_ADVISOR: [AgentType.GOAL_ADVISOR],
            AgentType.COSTING_ADVISOR: [AgentType.GROWTH_ADVISOR],
            AgentType.SUGGESTION_ADVISOR: [AgentType.GROWTH_ADVISOR, AgentType.GOAL_ADVISOR]
        }
        
        agent_set = set(agents)
        
        for agent in agents:
            required = dependencies.get(agent, [])
            if not all(req in agent_set for req in required):
                return True
        
        return False
    
    def _generate_rationale(
        self,
        agents: List[AgentType],
        context: Dict[str, Any]
    ) -> str:
        """Generate rationale for agent selection"""
        rationales = []
        
        # Request type rationale
        request_type = context.get("request_type", "")
        rationales.append(f"Request type: {request_type}")
        
        # Data availability rationale
        if context.get("has_bmc_data", 0) > 0:
            rationales.append("BMC data available")
        if context.get("has_market_data", 0) > 0:
            rationales.append("Market data available")
        if context.get("has_financial_data", 0) > 0:
            rationales.append("Financial data available")
        
        # Business stage rationale
        business_stage = context.get("business_stage", "")
        if business_stage:
            rationales.append(f"Business stage: {business_stage}")
        
        # Agent-specific rationale
        agent_names = [a.value for a in agents]
        rationales.append(f"Selected agents: {', '.join(agent_names)}")
        
        return "; ".join(rationales)
    
    def optimize_execution_order(
        self,
        agents: List[AgentType],
        context: Dict[str, Any]
    ) -> List[AgentType]:
        """
        Optimize execution order of agents.
        
        Args:
            agents: List of agents to execute
            context: Business context
            
        Returns:
            Optimized list of agents in execution order
        """
        # Define dependencies
        dependencies = {
            AgentType.GROWTH_ADVISOR: [AgentType.GOAL_ADVISOR],
            AgentType.COSTING_ADVISOR: [AgentType.GROWTH_ADVISOR],
            AgentType.SUGGESTION_ADVISOR: [AgentType.GROWTH_ADVISOR, AgentType.GOAL_ADVISOR]
        }
        
        # Topological sort based on dependencies
        ordered = []
        remaining = set(agents)
        
        while remaining:
            # Find agents with no unmet dependencies
            ready = [
                agent for agent in remaining
                if all(dep in ordered for dep in dependencies.get(agent, []))
            ]
            
            if not ready:
                # Circular dependency, break
                ordered.extend(list(remaining))
                break
            
            # Sort ready agents by priority
            ready_sorted = sorted(
                ready,
                key=lambda a: self._get_agent_priority(a, context),
                reverse=True
            )
            
            # Add highest priority ready agent
            ordered.append(ready_sorted[0])
            remaining.remove(ready_sorted[0])
        
        return ordered
    
    def _get_agent_priority(self, agent: AgentType, context: Dict[str, Any]) -> float:
        """Get priority score for an agent"""
        priorities = {
            AgentType.GOAL_ADVISOR: 0.9,
            AgentType.GROWTH_ADVISOR: 0.85,
            AgentType.COSTING_ADVISOR: 0.8,
            AgentType.SUGGESTION_ADVISOR: 0.75
        }
        
        base_priority = priorities.get(agent, 0.7)
        
        # Adjust based on business stage
        business_stage = context.get("business_stage", "")
        if business_stage == "startup" and agent == AgentType.GROWTH_ADVISOR:
            base_priority *= 1.1
        elif business_stage == "established" and agent == AgentType.COSTING_ADVISOR:
            base_priority *= 1.1
        
        return base_priority
    
    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        return self.execution_history[-limit:]
    
    def get_decision_statistics(self) -> Dict[str, Any]:
        """Get statistics about decision tree usage"""
        if not self.execution_history:
            return {
                "total_decisions": 0,
                "agent_usage": {},
                "execution_mode_usage": {}
            }
        
        agent_usage = {}
        execution_mode_usage = {}
        
        for record in self.execution_history:
            # Count agent usage
            for agent in record.get("selected_agents", []):
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
            
            # Count execution mode usage
            mode = record.get("execution_mode", "")
            execution_mode_usage[mode] = execution_mode_usage.get(mode, 0) + 1
        
        return {
            "total_decisions": len(self.execution_history),
            "agent_usage": agent_usage,
            "execution_mode_usage": execution_mode_usage,
            "most_used_agent": max(agent_usage.items(), key=lambda x: x[1])[0] if agent_usage else None,
            "most_used_mode": max(execution_mode_usage.items(), key=lambda x: x[1])[0] if execution_mode_usage else None
        }


class AgentSelector:
    """High-level agent selection interface"""
    
    def __init__(self):
        self.decision_tree = DecisionTree()
    
    def select_agents(
        self,
        user_request: str,
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Select agents based on user request and business context.
        
        Args:
            user_request: Natural language user request
            business_context: Business profile and available data
            
        Returns:
            Selection result with agents and execution plan
        """
        # Determine request type
        request_type = self._classify_request(user_request)
        
        # Use decision tree to determine agents
        decision = self.decision_tree.determine_agents(request_type, business_context)
        
        # Optimize execution order
        agents = decision["agents"]
        if decision["execution_mode"] == "sequential":
            agents = self.decision_tree.optimize_execution_order(agents, business_context)
        
        return {
            "request_type": request_type,
            "agents": agents,
            "execution_mode": decision["execution_mode"],
            "execution_order": [a.value for a in agents] if decision["execution_mode"] == "sequential" else None,
            "rationale": decision["rationale"],
            "decision_factors": decision["decision_factors"]
        }
    
    def _classify_request(self, user_request: str) -> str:
        """Classify user request into request type"""
        request_lower = user_request.lower()
        
        # Keywords for each request type
        keywords = {
            RequestType.GOAL_SETTING.value: ["goal", "objective", "target", "set goal"],
            RequestType.GROWTH_PLANNING.value: ["growth", "expand", "scale", "grow", "growth plan"],
            RequestType.COST_ANALYSIS.value: ["cost", "price", "pricing", "expense", "budget"],
            RequestType.BUSINESS_SUGGESTIONS.value: ["suggest", "recommend", "opportunity", "idea", "innovation"],
            RequestType.COMPREHENSIVE_ANALYSIS.value: ["analyze", "comprehensive", "full analysis", "complete"],
            RequestType.PROGRESS_TRACKING.value: ["progress", "track", "status", "how are we doing"],
            RequestType.FEASIBILITY_ASSESSMENT.value: ["feasible", "can we", "is it possible", "viability"],
            RequestType.STRATEGY_REVIEW.value: ["strategy", "review", "assess", "evaluate"]
        }
        
        # Find best matching request type
        best_match = RequestType.COMPREHENSIVE_ANALYSIS.value
        best_score = 0
        
        for req_type, words in keywords.items():
            score = sum(1 for word in words if word in request_lower)
            if score > best_score:
                best_score = score
                best_match = req_type
        
        logger.info(f"Classified request as: {best_match}")
        
        return best_match
