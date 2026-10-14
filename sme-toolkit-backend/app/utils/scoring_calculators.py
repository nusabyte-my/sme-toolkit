"""Scoring calculation utilities for different score types"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ScoringCalculator:
    """Base class for scoring calculators"""
    
    @staticmethod
    def normalize_score(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
        """
        Normalize a value to 0-100 range.
        
        Args:
            value: Value to normalize
            min_val: Minimum expected value
            max_val: Maximum expected value
            
        Returns:
            Normalized score (0-100)
        """
        if max_val == min_val:
            return 50.0
        
        normalized = ((value - min_val) / (max_val - min_val)) * 100
        return max(0.0, min(100.0, normalized))
    
    @staticmethod
    def calculate_weighted_average(scores: Dict[str, float], weights: Dict[str, float]) -> float:
        """
        Calculate weighted average of scores.
        
        Args:
            scores: Dictionary of score names to values
            weights: Dictionary of score names to weights
            
        Returns:
            Weighted average score
        """
        total_weight = 0.0
        weighted_sum = 0.0
        
        for score_name, score_value in scores.items():
            weight = weights.get(score_name, 0.0)
            weighted_sum += score_value * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_sum / total_weight
    
    @staticmethod
    def apply_multiplier(score: float, multiplier: float) -> float:
        """
        Apply a multiplier to a score.
        
        Args:
            score: Base score
            multiplier: Multiplier (typically 0.5 to 1.5)
            
        Returns:
            Adjusted score
        """
        adjusted = score * multiplier
        return max(0.0, min(100.0, adjusted))
    
    @staticmethod
    def get_score_level(score: float, thresholds: Dict[str, tuple]) -> str:
        """
        Get score level based on thresholds.
        
        Args:
            score: Score value
            thresholds: Dictionary of level names to (min, max) tuples
            
        Returns:
            Score level
        """
        for level, (min_val, max_val) in thresholds.items():
            if min_val <= score <= max_val:
                return level
        
        # Default to lowest level
        return list(thresholds.keys())[0]


class BusinessHealthCalculator:
    """Calculate Business Health Score (0-100)"""
    
    WEIGHTS = {
        "financial": 0.30,
        "operational": 0.25,
        "customer": 0.20,
        "market": 0.15,
        "innovation": 0.10
    }
    
    THRESHOLDS = {
        "critical": (0, 40),
        "needs_improvement": (41, 60),
        "good": (61, 80),
        "excellent": (81, 100)
    }
    
    @staticmethod
    def calculate(profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate business health score.
        
        Args:
            profile_data: Business profile and analysis data
            
        Returns:
            Score data with sub-metrics
        """
        # Extract or calculate sub-metrics
        financial_score = BusinessHealthCalculator._calculate_financial_score(profile_data)
        operational_score = BusinessHealthCalculator._calculate_operational_score(profile_data)
        customer_score = BusinessHealthCalculator._calculate_customer_score(profile_data)
        market_score = BusinessHealthCalculator._calculate_market_score(profile_data)
        innovation_score = BusinessHealthCalculator._calculate_innovation_score(profile_data)
        
        # Calculate weighted average
        sub_scores = {
            "financial": financial_score,
            "operational": operational_score,
            "customer": customer_score,
            "market": market_score,
            "innovation": innovation_score
        }
        
        overall_score = ScoringCalculator.calculate_weighted_average(
            sub_scores,
            BusinessHealthCalculator.WEIGHTS
        )
        
        # Get score level
        level = ScoringCalculator.get_score_level(
            overall_score,
            BusinessHealthCalculator.THRESHOLDS
        )
        
        return {
            "overall_score": round(overall_score, 2),
            "level": level,
            "sub_metrics": {
                "financial": {
                    "score": round(financial_score, 2),
                    "weight": BusinessHealthCalculator.WEIGHTS["financial"],
                    "factors": ["Revenue growth", "Profitability", "Cash flow", "Debt ratio"]
                },
                "operational": {
                    "score": round(operational_score, 2),
                    "weight": BusinessHealthCalculator.WEIGHTS["operational"],
                    "factors": ["Efficiency", "Productivity", "Quality", "Scalability"]
                },
                "customer": {
                    "score": round(customer_score, 2),
                    "weight": BusinessHealthCalculator.WEIGHTS["customer"],
                    "factors": ["Satisfaction", "Retention", "Acquisition cost", "Lifetime value"]
                },
                "market": {
                    "score": round(market_score, 2),
                    "weight": BusinessHealthCalculator.WEIGHTS["market"],
                    "factors": ["Market share", "Brand awareness", "Competitive position"]
                },
                "innovation": {
                    "score": round(innovation_score, 2),
                    "weight": BusinessHealthCalculator.WEIGHTS["innovation"],
                    "factors": ["R&D investment", "New products", "Process improvements"]
                }
            },
            "interpretation": BusinessHealthCalculator._interpret_score(overall_score, level)
        }
    
    @staticmethod
    def _calculate_financial_score(profile_data: Dict[str, Any]) -> float:
        """Calculate financial health sub-score"""
        # Extract financial metrics from profile data
        financials = profile_data.get("financials", {})
        
        revenue_growth = financials.get("revenue_growth", 0.0)
        profitability = financials.get("profitability", 0.0)
        cash_flow = financials.get("cash_flow", 0.0)
        debt_ratio = financials.get("debt_ratio", 0.0)
        
        # Normalize each metric
        revenue_score = ScoringCalculator.normalize_score(revenue_growth, -20, 50)
        profit_score = ScoringCalculator.normalize_score(profitability, 0, 30)
        cash_score = ScoringCalculator.normalize_score(cash_flow, -100, 100)
        debt_score = ScoringCalculator.normalize_score(100 - debt_ratio, 0, 100)  # Invert debt ratio
        
        # Average the scores
        return (revenue_score + profit_score + cash_score + debt_score) / 4
    
    @staticmethod
    def _calculate_operational_score(profile_data: Dict[str, Any]) -> float:
        """Calculate operational efficiency sub-score"""
        operations = profile_data.get("operations", {})
        
        efficiency = operations.get("efficiency", 50.0)
        productivity = operations.get("productivity", 50.0)
        quality = operations.get("quality", 50.0)
        scalability = operations.get("scalability", 50.0)
        
        return (efficiency + productivity + quality + scalability) / 4
    
    @staticmethod
    def _calculate_customer_score(profile_data: Dict[str, Any]) -> float:
        """Calculate customer satisfaction sub-score"""
        customer = profile_data.get("customer", {})
        
        satisfaction = customer.get("satisfaction", 50.0)
        retention = customer.get("retention", 50.0)
        acquisition_cost = customer.get("acquisition_cost", 50.0)
        lifetime_value = customer.get("lifetime_value", 50.0)
        
        return (satisfaction + retention + acquisition_cost + lifetime_value) / 4
    
    @staticmethod
    def _calculate_market_score(profile_data: Dict[str, Any]) -> float:
        """Calculate market position sub-score"""
        market = profile_data.get("market", {})
        
        market_share = market.get("market_share", 0.0)
        brand_awareness = market.get("brand_awareness", 50.0)
        competitive_position = market.get("competitive_position", 50.0)
        
        share_score = ScoringCalculator.normalize_score(market_share, 0, 50)
        return (share_score + brand_awareness + competitive_position) / 3
    
    @staticmethod
    def _calculate_innovation_score(profile_data: Dict[str, Any]) -> float:
        """Calculate innovation readiness sub-score"""
        innovation = profile_data.get("innovation", {})
        
        rd_investment = innovation.get("rd_investment", 0.0)
        new_products = innovation.get("new_products", 0.0)
        process_improvements = innovation.get("process_improvements", 0.0)
        
        rd_score = ScoringCalculator.normalize_score(rd_investment, 0, 20)
        products_score = ScoringCalculator.normalize_score(new_products, 0, 10)
        process_score = ScoringCalculator.normalize_score(process_improvements, 0, 10)
        
        return (rd_score + products_score + process_score) / 3
    
    @staticmethod
    def _interpret_score(score: float, level: str) -> str:
        """Interpret the score"""
        interpretations = {
            "critical": "Critical - Immediate action required",
            "needs_improvement": "Needs Improvement - Significant issues requiring attention",
            "good": "Good - Strong performance with minor improvements needed",
            "excellent": "Excellent - Business is thriving"
        }
        return interpretations.get(level, "Unknown")


class GrowthPotentialCalculator:
    """Calculate Growth Potential Score (0-100)"""
    
    WEIGHTS = {
        "market_opportunity": 0.35,
        "competitive_advantage": 0.25,
        "execution_capability": 0.20,
        "financial_resources": 0.15,
        "innovation": 0.05
    }
    
    THRESHOLDS = {
        "low": (0, 40),
        "moderate": (41, 60),
        "high": (61, 80),
        "very_high": (81, 100)
    }
    
    @staticmethod
    def calculate(profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate growth potential score"""
        market_score = GrowthPotentialCalculator._calculate_market_opportunity(profile_data)
        competitive_score = GrowthPotentialCalculator._calculate_competitive_advantage(profile_data)
        execution_score = GrowthPotentialCalculator._calculate_execution_capability(profile_data)
        financial_score = GrowthPotentialCalculator._calculate_financial_resources(profile_data)
        innovation_score = GrowthPotentialCalculator._calculate_innovation_potential(profile_data)
        
        sub_scores = {
            "market_opportunity": market_score,
            "competitive_advantage": competitive_score,
            "execution_capability": execution_score,
            "financial_resources": financial_score,
            "innovation": innovation_score
        }
        
        overall_score = ScoringCalculator.calculate_weighted_average(
            sub_scores,
            GrowthPotentialCalculator.WEIGHTS
        )
        
        # Apply opportunity multiplier based on market opportunity
        opportunity_multiplier = 1.0 + (market_score - 50) / 200  # 0.75 to 1.25
        overall_score = ScoringCalculator.apply_multiplier(overall_score, opportunity_multiplier)
        
        level = ScoringCalculator.get_score_level(
            overall_score,
            GrowthPotentialCalculator.THRESHOLDS
        )
        
        return {
            "overall_score": round(overall_score, 2),
            "level": level,
            "sub_metrics": {
                "market_opportunity": {
                    "score": round(market_score, 2),
                    "weight": GrowthPotentialCalculator.WEIGHTS["market_opportunity"],
                    "factors": ["Market size", "Growth rate", "Trends"]
                },
                "competitive_advantage": {
                    "score": round(competitive_score, 2),
                    "weight": GrowthPotentialCalculator.WEIGHTS["competitive_advantage"],
                    "factors": ["Unique value proposition", "Barriers to entry"]
                },
                "execution_capability": {
                    "score": round(execution_score, 2),
                    "weight": GrowthPotentialCalculator.WEIGHTS["execution_capability"],
                    "factors": ["Team", "Processes", "Technology"]
                },
                "financial_resources": {
                    "score": round(financial_score, 2),
                    "weight": GrowthPotentialCalculator.WEIGHTS["financial_resources"],
                    "factors": ["Funding", "Cash flow", "Profitability"]
                },
                "innovation": {
                    "score": round(innovation_score, 2),
                    "weight": GrowthPotentialCalculator.WEIGHTS["innovation"],
                    "factors": ["R&D", "New products", "Patents"]
                }
            },
            "interpretation": GrowthPotentialCalculator._interpret_score(overall_score, level)
        }
    
    @staticmethod
    def _calculate_market_opportunity(profile_data: Dict[str, Any]) -> float:
        """Calculate market opportunity sub-score"""
        market = profile_data.get("market", {})
        
        market_size = market.get("market_size", 0.0)
        growth_rate = market.get("growth_rate", 0.0)
        trends = market.get("trends", 50.0)
        
        size_score = ScoringCalculator.normalize_score(market_size, 0, 1000)  # In millions
        growth_score = ScoringCalculator.normalize_score(growth_rate, -10, 50)
        
        return (size_score + growth_score + trends) / 3
    
    @staticmethod
    def _calculate_competitive_advantage(profile_data: Dict[str, Any]) -> float:
        """Calculate competitive advantage sub-score"""
        competitive = profile_data.get("competitive", {})
        
        value_proposition = competitive.get("value_proposition", 50.0)
        barriers_to_entry = competitive.get("barriers_to_entry", 50.0)
        
        return (value_proposition + barriers_to_entry) / 2
    
    @staticmethod
    def _calculate_execution_capability(profile_data: Dict[str, Any]) -> float:
        """Calculate execution capability sub-score"""
        execution = profile_data.get("execution", {})
        
        team = execution.get("team", 50.0)
        processes = execution.get("processes", 50.0)
        technology = execution.get("technology", 50.0)
        
        return (team + processes + technology) / 3
    
    @staticmethod
    def _calculate_financial_resources(profile_data: Dict[str, Any]) -> float:
        """Calculate financial resources sub-score"""
        financials = profile_data.get("financials", {})
        
        funding = financials.get("funding", 0.0)
        cash_flow = financials.get("cash_flow", 0.0)
        profitability = financials.get("profitability", 0.0)
        
        funding_score = ScoringCalculator.normalize_score(funding, 0, 10)  # In millions
        cash_score = ScoringCalculator.normalize_score(cash_flow, -100, 100)
        profit_score = ScoringCalculator.normalize_score(profitability, 0, 30)
        
        return (funding_score + cash_score + profit_score) / 3
    
    @staticmethod
    def _calculate_innovation_potential(profile_data: Dict[str, Any]) -> float:
        """Calculate innovation potential sub-score"""
        innovation = profile_data.get("innovation", {})
        
        rd = innovation.get("rd_investment", 0.0)
        new_products = innovation.get("new_products", 0.0)
        patents = innovation.get("patents", 0.0)
        
        rd_score = ScoringCalculator.normalize_score(rd, 0, 20)
        products_score = ScoringCalculator.normalize_score(new_products, 0, 10)
        patents_score = ScoringCalculator.normalize_score(patents, 0, 10)
        
        return (rd_score + products_score + patents_score) / 3
    
    @staticmethod
    def _interpret_score(score: float, level: str) -> str:
        """Interpret the score"""
        interpretations = {
            "low": "Low - Growth challenges",
            "moderate": "Moderate - Limited growth opportunities",
            "high": "High - Strong growth prospects",
            "very_high": "Very High - Excellent growth potential"
        }
        return interpretations.get(level, "Unknown")


class FinancialStabilityCalculator:
    """Calculate Financial Stability Score (0-100)"""
    
    WEIGHTS = {
        "revenue": 0.30,
        "profitability": 0.25,
        "cash_flow": 0.20,
        "debt": 0.15,
        "funding": 0.10
    }
    
    THRESHOLDS = {
        "unstable": (0, 40),
        "moderate_risk": (41, 60),
        "stable": (61, 80),
        "very_stable": (81, 100)
    }
    
    @staticmethod
    def calculate(profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial stability score"""
        revenue_score = FinancialStabilityCalculator._calculate_revenue_score(profile_data)
        profitability_score = FinancialStabilityCalculator._calculate_profitability_score(profile_data)
        cash_flow_score = FinancialStabilityCalculator._calculate_cash_flow_score(profile_data)
        debt_score = FinancialStabilityCalculator._calculate_debt_score(profile_data)
        funding_score = FinancialStabilityCalculator._calculate_funding_score(profile_data)
        
        sub_scores = {
            "revenue": revenue_score,
            "profitability": profitability_score,
            "cash_flow": cash_flow_score,
            "debt": debt_score,
            "funding": funding_score
        }
        
        overall_score = ScoringCalculator.calculate_weighted_average(
            sub_scores,
            FinancialStabilityCalculator.WEIGHTS
        )
        
        # Apply stability factor
        stability_factor = 1.0
        if cash_flow_score < 50 or debt_score < 50:
            stability_factor = 0.9
        
        overall_score = ScoringCalculator.apply_multiplier(overall_score, stability_factor)
        
        level = ScoringCalculator.get_score_level(
            overall_score,
            FinancialStabilityCalculator.THRESHOLDS
        )
        
        return {
            "overall_score": round(overall_score, 2),
            "level": level,
            "sub_metrics": {
                "revenue": {
                    "score": round(revenue_score, 2),
                    "weight": FinancialStabilityCalculator.WEIGHTS["revenue"],
                    "factors": ["Revenue growth", "Revenue diversity", "Recurring revenue"]
                },
                "profitability": {
                    "score": round(profitability_score, 2),
                    "weight": FinancialStabilityCalculator.WEIGHTS["profitability"],
                    "factors": ["Gross margin", "Net margin", "EBITDA"]
                },
                "cash_flow": {
                    "score": round(cash_flow_score, 2),
                    "weight": FinancialStabilityCalculator.WEIGHTS["cash_flow"],
                    "factors": ["Operating cash flow", "Free cash flow", "Cash reserves"]
                },
                "debt": {
                    "score": round(debt_score, 2),
                    "weight": FinancialStabilityCalculator.WEIGHTS["debt"],
                    "factors": ["Debt-to-equity", "Interest coverage", "Debt service"]
                },
                "funding": {
                    "score": round(funding_score, 2),
                    "weight": FinancialStabilityCalculator.WEIGHTS["funding"],
                    "factors": ["Funding runway", "Investor confidence", "Access to capital"]
                }
            },
            "interpretation": FinancialStabilityCalculator._interpret_score(overall_score, level)
        }
    
    @staticmethod
    def _calculate_revenue_score(profile_data: Dict[str, Any]) -> float:
        """Calculate revenue stability sub-score"""
        financials = profile_data.get("financials", {})
        
        revenue_growth = financials.get("revenue_growth", 0.0)
        revenue_diversity = financials.get("revenue_diversity", 50.0)
        recurring_revenue = financials.get("recurring_revenue", 0.0)
        
        growth_score = ScoringCalculator.normalize_score(revenue_growth, -20, 50)
        diversity_score = revenue_diversity
        recurring_score = ScoringCalculator.normalize_score(recurring_revenue, 0, 100)
        
        return (growth_score + diversity_score + recurring_score) / 3
    
    @staticmethod
    def _calculate_profitability_score(profile_data: Dict[str, Any]) -> float:
        """Calculate profitability sub-score"""
        financials = profile_data.get("financials", {})
        
        gross_margin = financials.get("gross_margin", 0.0)
        net_margin = financials.get("net_margin", 0.0)
        ebitda = financials.get("ebitda", 0.0)
        
        gross_score = ScoringCalculator.normalize_score(gross_margin, 0, 50)
        net_score = ScoringCalculator.normalize_score(net_margin, -10, 30)
        ebitda_score = ScoringCalculator.normalize_score(ebitda, -10, 30)
        
        return (gross_score + net_score + ebitda_score) / 3
    
    @staticmethod
    def _calculate_cash_flow_score(profile_data: Dict[str, Any]) -> float:
        """Calculate cash flow health sub-score"""
        financials = profile_data.get("financials", {})
        
        operating_cash_flow = financials.get("operating_cash_flow", 0.0)
        free_cash_flow = financials.get("free_cash_flow", 0.0)
        cash_reserves = financials.get("cash_reserves", 0.0)
        
        operating_score = ScoringCalculator.normalize_score(operating_cash_flow, -100, 100)
        free_score = ScoringCalculator.normalize_score(free_cash_flow, -100, 100)
        reserves_score = ScoringCalculator.normalize_score(cash_reserves, 0, 1000)  # In thousands
        
        return (operating_score + free_score + reserves_score) / 3
    
    @staticmethod
    def _calculate_debt_score(profile_data: Dict[str, Any]) -> float:
        """Calculate debt management sub-score"""
        financials = profile_data.get("financials", {})
        
        debt_to_equity = financials.get("debt_to_equity", 0.0)
        interest_coverage = financials.get("interest_coverage", 0.0)
        debt_service = financials.get("debt_service", 0.0)
        
        dte_score = ScoringCalculator.normalize_score(100 - debt_to_equity, 0, 100)  # Invert
        ic_score = ScoringCalculator.normalize_score(interest_coverage, 0, 10)
        ds_score = ScoringCalculator.normalize_score(100 - debt_service, 0, 100)  # Invert
        
        return (dte_score + ic_score + ds_score) / 3
    
    @staticmethod
    def _calculate_funding_score(profile_data: Dict[str, Any]) -> float:
        """Calculate funding readiness sub-score"""
        financials = profile_data.get("financials", {})
        
        funding_runway = financials.get("funding_runway", 0.0)
        investor_confidence = financials.get("investor_confidence", 50.0)
        access_to_capital = financials.get("access_to_capital", 50.0)
        
        runway_score = ScoringCalculator.normalize_score(funding_runway, 0, 24)  # In months
        confidence_score = investor_confidence
        access_score = access_to_capital
        
        return (runway_score + confidence_score + access_score) / 3
    
    @staticmethod
    def _interpret_score(score: float, level: str) -> str:
        """Interpret the score"""
        interpretations = {
            "unstable": "Unstable - Financial instability",
            "moderate_risk": "Moderate Risk - Some financial concerns",
            "stable": "Stable - Adequate financial health",
            "very_stable": "Very Stable - Strong financial position"
        }
        return interpretations.get(level, "Unknown")


class MarketPositionCalculator:
    """Calculate Market Position Score (0-100)"""
    
    WEIGHTS = {
        "market_share": 0.30,
        "brand_strength": 0.25,
        "market_positioning": 0.20,
        "customer_loyalty": 0.15,
        "market_influence": 0.10
    }
    
    THRESHOLDS = {
        "weak": (0, 40),
        "developing": (41, 60),
        "strong": (61, 80),
        "dominant": (81, 100)
    }
    
    @staticmethod
    def calculate(profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate market position score"""
        share_score = MarketPositionCalculator._calculate_market_share(profile_data)
        brand_score = MarketPositionCalculator._calculate_brand_strength(profile_data)
        positioning_score = MarketPositionCalculator._calculate_market_positioning(profile_data)
        loyalty_score = MarketPositionCalculator._calculate_customer_loyalty(profile_data)
        influence_score = MarketPositionCalculator._calculate_market_influence(profile_data)
        
        sub_scores = {
            "market_share": share_score,
            "brand_strength": brand_score,
            "market_positioning": positioning_score,
            "customer_loyalty": loyalty_score,
            "market_influence": influence_score
        }
        
        overall_score = ScoringCalculator.calculate_weighted_average(
            sub_scores,
            MarketPositionCalculator.WEIGHTS
        )
        
        # Apply market size adjustment
        market_size = profile_data.get("market", {}).get("market_size", 100)
        size_adjustment = 1.0
        if market_size < 50:  # Small market
            size_adjustment = 1.1
        elif market_size > 500:  # Large market
            size_adjustment = 0.9
        
        overall_score = ScoringCalculator.apply_multiplier(overall_score, size_adjustment)
        
        level = ScoringCalculator.get_score_level(
            overall_score,
            MarketPositionCalculator.THRESHOLDS
        )
        
        return {
            "overall_score": round(overall_score, 2),
            "level": level,
            "sub_metrics": {
                "market_share": {
                    "score": round(share_score, 2),
                    "weight": MarketPositionCalculator.WEIGHTS["market_share"],
                    "factors": ["Current share", "Share growth", "Share in segments"]
                },
                "brand_strength": {
                    "score": round(brand_score, 2),
                    "weight": MarketPositionCalculator.WEIGHTS["brand_strength"],
                    "factors": ["Brand awareness", "Brand perception", "Brand equity"]
                },
                "market_positioning": {
                    "score": round(positioning_score, 2),
                    "weight": MarketPositionCalculator.WEIGHTS["market_positioning"],
                    "factors": ["Differentiation", "Value proposition", "Pricing power"]
                },
                "customer_loyalty": {
                    "score": round(loyalty_score, 2),
                    "weight": MarketPositionCalculator.WEIGHTS["customer_loyalty"],
                    "factors": ["Retention rate", "NPS", "Repeat purchase rate"]
                },
                "market_influence": {
                    "score": round(influence_score, 2),
                    "weight": MarketPositionCalculator.WEIGHTS["market_influence"],
                    "factors": ["Thought leadership", "Partnerships", "Ecosystem"]
                }
            },
            "interpretation": MarketPositionCalculator._interpret_score(overall_score, level)
        }
    
    @staticmethod
    def _calculate_market_share(profile_data: Dict[str, Any]) -> float:
        """Calculate market share sub-score"""
        market = profile_data.get("market", {})
        
        current_share = market.get("market_share", 0.0)
        share_growth = market.get("share_growth", 0.0)
        segment_share = market.get("segment_share", 0.0)
        
        current_score = ScoringCalculator.normalize_score(current_share, 0, 50)
        growth_score = ScoringCalculator.normalize_score(share_growth, -10, 20)
        segment_score = ScoringCalculator.normalize_score(segment_share, 0, 30)
        
        return (current_score + growth_score + segment_score) / 3
    
    @staticmethod
    def _calculate_brand_strength(profile_data: Dict[str, Any]) -> float:
        """Calculate brand strength sub-score"""
        market = profile_data.get("market", {})
        
        brand_awareness = market.get("brand_awareness", 50.0)
        brand_perception = market.get("brand_perception", 50.0)
        brand_equity = market.get("brand_equity", 50.0)
        
        return (brand_awareness + brand_perception + brand_equity) / 3
    
    @staticmethod
    def _calculate_market_positioning(profile_data: Dict[str, Any]) -> float:
        """Calculate market positioning sub-score"""
        market = profile_data.get("market", {})
        
        differentiation = market.get("differentiation", 50.0)
        value_proposition = market.get("value_proposition", 50.0)
        pricing_power = market.get("pricing_power", 50.0)
        
        return (differentiation + value_proposition + pricing_power) / 3
    
    @staticmethod
    def _calculate_customer_loyalty(profile_data: Dict[str, Any]) -> float:
        """Calculate customer loyalty sub-score"""
        customer = profile_data.get("customer", {})
        
        retention_rate = customer.get("retention", 50.0)
        nps = customer.get("nps", 0.0)
        repeat_purchase = customer.get("repeat_purchase", 50.0)
        
        retention_score = retention_rate
        nps_score = ScoringCalculator.normalize_score(nps, -100, 100)
        repeat_score = repeat_purchase
        
        return (retention_score + nps_score + repeat_score) / 3
    
    @staticmethod
    def _calculate_market_influence(profile_data: Dict[str, Any]) -> float:
        """Calculate market influence sub-score"""
        market = profile_data.get("market", {})
        
        thought_leadership = market.get("thought_leadership", 50.0)
        partnerships = market.get("partnerships", 50.0)
        ecosystem = market.get("ecosystem", 50.0)
        
        return (thought_leadership + partnerships + ecosystem) / 3
    
    @staticmethod
    def _interpret_score(score: float, level: str) -> str:
        """Interpret the score"""
        interpretations = {
            "weak": "Weak - Weak market presence",
            "developing": "Developing - Developing market position",
            "strong": "Strong - Competitive market presence",
            "dominant": "Dominant - Market leader"
        }
        return interpretations.get(level, "Unknown")


class OperationalEfficiencyCalculator:
    """Calculate Operational Efficiency Score (0-100)"""
    
    WEIGHTS = {
        "process_efficiency": 0.30,
        "resource_utilization": 0.25,
        "cost_efficiency": 0.20,
        "quality": 0.15,
        "scalability": 0.10
    }
    
    THRESHOLDS = {
        "inefficient": (0, 40),
        "needs_improvement": (41, 60),
        "efficient": (61, 80),
        "highly_efficient": (81, 100)
    }
    
    @staticmethod
    def calculate(profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate operational efficiency score"""
        process_score = OperationalEfficiencyCalculator._calculate_process_efficiency(profile_data)
        resource_score = OperationalEfficiencyCalculator._calculate_resource_utilization(profile_data)
        cost_score = OperationalEfficiencyCalculator._calculate_cost_efficiency(profile_data)
        quality_score = OperationalEfficiencyCalculator._calculate_quality(profile_data)
        scalability_score = OperationalEfficiencyCalculator._calculate_scalability(profile_data)
        
        sub_scores = {
            "process_efficiency": process_score,
            "resource_utilization": resource_score,
            "cost_efficiency": cost_score,
            "quality": quality_score,
            "scalability": scalability_score
        }
        
        overall_score = ScoringCalculator.calculate_weighted_average(
            sub_scores,
            OperationalEfficiencyCalculator.WEIGHTS
        )
        
        # Apply efficiency multiplier
        efficiency_multiplier = 1.0
        if quality_score > 80 and process_score > 80:
            efficiency_multiplier = 1.05
        
        overall_score = ScoringCalculator.apply_multiplier(overall_score, efficiency_multiplier)
        
        level = ScoringCalculator.get_score_level(
            overall_score,
            OperationalEfficiencyCalculator.THRESHOLDS
        )
        
        return {
            "overall_score": round(overall_score, 2),
            "level": level,
            "sub_metrics": {
                "process_efficiency": {
                    "score": round(process_score, 2),
                    "weight": OperationalEfficiencyCalculator.WEIGHTS["process_efficiency"],
                    "factors": ["Cycle time", "Throughput", "Process automation"]
                },
                "resource_utilization": {
                    "score": round(resource_score, 2),
                    "weight": OperationalEfficiencyCalculator.WEIGHTS["resource_utilization"],
                    "factors": ["Employee productivity", "Asset utilization", "Capacity utilization"]
                },
                "cost_efficiency": {
                    "score": round(cost_score, 2),
                    "weight": OperationalEfficiencyCalculator.WEIGHTS["cost_efficiency"],
                    "factors": ["Cost per unit", "Overhead ratio", "Waste reduction"]
                },
                "quality": {
                    "score": round(quality_score, 2),
                    "weight": OperationalEfficiencyCalculator.WEIGHTS["quality"],
                    "factors": ["Defect rate", "Customer complaints", "Quality certifications"]
                },
                "scalability": {
                    "score": round(scalability_score, 2),
                    "weight": OperationalEfficiencyCalculator.WEIGHTS["scalability"],
                    "factors": ["System capacity", "Process scalability", "Team scalability"]
                }
            },
            "interpretation": OperationalEfficiencyCalculator._interpret_score(overall_score, level)
        }
    
    @staticmethod
    def _calculate_process_efficiency(profile_data: Dict[str, Any]) -> float:
        """Calculate process efficiency sub-score"""
        operations = profile_data.get("operations", {})
        
        cycle_time = operations.get("cycle_time", 50.0)
        throughput = operations.get("throughput", 50.0)
        automation = operations.get("automation", 50.0)
        
        cycle_score = ScoringCalculator.normalize_score(100 - cycle_time, 0, 100)  # Invert
        throughput_score = throughput
        automation_score = automation
        
        return (cycle_score + throughput_score + automation_score) / 3
    
    @staticmethod
    def _calculate_resource_utilization(profile_data: Dict[str, Any]) -> float:
        """Calculate resource utilization sub-score"""
        operations = profile_data.get("operations", {})
        
        employee_productivity = operations.get("employee_productivity", 50.0)
        asset_utilization = operations.get("asset_utilization", 50.0)
        capacity_utilization = operations.get("capacity_utilization", 50.0)
        
        return (employee_productivity + asset_utilization + capacity_utilization) / 3
    
    @staticmethod
    def _calculate_cost_efficiency(profile_data: Dict[str, Any]) -> float:
        """Calculate cost efficiency sub-score"""
        operations = profile_data.get("operations", {})
        
        cost_per_unit = operations.get("cost_per_unit", 50.0)
        overhead_ratio = operations.get("overhead_ratio", 50.0)
        waste_reduction = operations.get("waste_reduction", 50.0)
        
        unit_score = ScoringCalculator.normalize_score(100 - cost_per_unit, 0, 100)  # Invert
        overhead_score = ScoringCalculator.normalize_score(100 - overhead_ratio, 0, 100)  # Invert
        waste_score = waste_reduction
        
        return (unit_score + overhead_score + waste_score) / 3
    
    @staticmethod
    def _calculate_quality(profile_data: Dict[str, Any]) -> float:
        """Calculate quality sub-score"""
        operations = profile_data.get("operations", {})
        
        defect_rate = operations.get("defect_rate", 50.0)
        customer_complaints = operations.get("customer_complaints", 50.0)
        quality_certifications = operations.get("quality_certifications", 50.0)
        
        defect_score = ScoringCalculator.normalize_score(100 - defect_rate, 0, 100)  # Invert
        complaint_score = ScoringCalculator.normalize_score(100 - customer_complaints, 0, 100)  # Invert
        certification_score = quality_certifications
        
        return (defect_score + complaint_score + certification_score) / 3
    
    @staticmethod
    def _calculate_scalability(profile_data: Dict[str, Any]) -> float:
        """Calculate scalability sub-score"""
        operations = profile_data.get("operations", {})
        
        system_capacity = operations.get("system_capacity", 50.0)
        process_scalability = operations.get("process_scalability", 50.0)
        team_scalability = operations.get("team_scalability", 50.0)
        
        return (system_capacity + process_scalability + team_scalability) / 3
    
    @staticmethod
    def _interpret_score(score: float, level: str) -> str:
        """Interpret the score"""
        interpretations = {
            "inefficient": "Inefficient - Inefficient operations",
            "needs_improvement": "Needs Improvement - Room for improvement",
            "efficient": "Efficient - Adequate efficiency",
            "highly_efficient": "Highly Efficient - Highly efficient operations"
        }
        return interpretations.get(level, "Unknown")


class InnovationReadinessCalculator:
    """Calculate Innovation Readiness Score (0-100)"""
    
    WEIGHTS = {
        "rd_investment": 0.30,
        "innovation_culture": 0.25,
        "technology_adoption": 0.20,
        "idea_generation": 0.15,
        "success_rate": 0.10
    }
    
    THRESHOLDS = {
        "not_ready": (0, 40),
        "developing": (41, 60),
        "ready": (61, 80),
        "highly_ready": (81, 100)
    }
    
    @staticmethod
    def calculate(profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate innovation readiness score"""
        rd_score = InnovationReadinessCalculator._calculate_rd_investment(profile_data)
        culture_score = InnovationReadinessCalculator._calculate_innovation_culture(profile_data)
        tech_score = InnovationReadinessCalculator._calculate_technology_adoption(profile_data)
        idea_score = InnovationReadinessCalculator._calculate_idea_generation(profile_data)
        success_score = InnovationReadinessCalculator._calculate_success_rate(profile_data)
        
        sub_scores = {
            "rd_investment": rd_score,
            "innovation_culture": culture_score,
            "technology_adoption": tech_score,
            "idea_generation": idea_score,
            "success_rate": success_score
        }
        
        overall_score = ScoringCalculator.calculate_weighted_average(
            sub_scores,
            InnovationReadinessCalculator.WEIGHTS
        )
        
        # Apply innovation potential factor
        innovation_factor = 1.0
        if rd_score > 70 and culture_score > 70:
            innovation_factor = 1.1
        
        overall_score = ScoringCalculator.apply_multiplier(overall_score, innovation_factor)
        
        level = ScoringCalculator.get_score_level(
            overall_score,
            InnovationReadinessCalculator.THRESHOLDS
        )
        
        return {
            "overall_score": round(overall_score, 2),
            "level": level,
            "sub_metrics": {
                "rd_investment": {
                    "score": round(rd_score, 2),
                    "weight": InnovationReadinessCalculator.WEIGHTS["rd_investment"],
                    "factors": ["R&D budget", "R&D as % of revenue", "R&D team size"]
                },
                "innovation_culture": {
                    "score": round(culture_score, 2),
                    "weight": InnovationReadinessCalculator.WEIGHTS["innovation_culture"],
                    "factors": ["Employee engagement", "Risk tolerance", "Collaboration"]
                },
                "technology_adoption": {
                    "score": round(tech_score, 2),
                    "weight": InnovationReadinessCalculator.WEIGHTS["technology_adoption"],
                    "factors": ["Tech stack modernization", "Automation", "AI/ML usage"]
                },
                "idea_generation": {
                    "score": round(idea_score, 2),
                    "weight": InnovationReadinessCalculator.WEIGHTS["idea_generation"],
                    "factors": ["Ideas per employee", "Idea pipeline", "Innovation programs"]
                },
                "success_rate": {
                    "score": round(success_score, 2),
                    "weight": InnovationReadinessCalculator.WEIGHTS["success_rate"],
                    "factors": ["Innovation success rate", "Time to market", "ROI on innovation"]
                }
            },
            "interpretation": InnovationReadinessCalculator._interpret_score(overall_score, level)
        }
    
    @staticmethod
    def _calculate_rd_investment(profile_data: Dict[str, Any]) -> float:
        """Calculate R&D investment sub-score"""
        innovation = profile_data.get("innovation", {})
        
        rd_budget = innovation.get("rd_budget", 0.0)
        rd_percentage = innovation.get("rd_percentage", 0.0)
        rd_team_size = innovation.get("rd_team_size", 0.0)
        
        budget_score = ScoringCalculator.normalize_score(rd_budget, 0, 10)  # In millions
        percentage_score = ScoringCalculator.normalize_score(rd_percentage, 0, 20)
        team_score = ScoringCalculator.normalize_score(rd_team_size, 0, 50)
        
        return (budget_score + percentage_score + team_score) / 3
    
    @staticmethod
    def _calculate_innovation_culture(profile_data: Dict[str, Any]) -> float:
        """Calculate innovation culture sub-score"""
        innovation = profile_data.get("innovation", {})
        
        employee_engagement = innovation.get("employee_engagement", 50.0)
        risk_tolerance = innovation.get("risk_tolerance", 50.0)
        collaboration = innovation.get("collaboration", 50.0)
        
        return (employee_engagement + risk_tolerance + collaboration) / 3
    
    @staticmethod
    def _calculate_technology_adoption(profile_data: Dict[str, Any]) -> float:
        """Calculate technology adoption sub-score"""
        innovation = profile_data.get("innovation", {})
        
        tech_modernization = innovation.get("tech_modernization", 50.0)
        automation = innovation.get("automation", 50.0)
        ai_ml_usage = innovation.get("ai_ml_usage", 50.0)
        
        return (tech_modernization + automation + ai_ml_usage) / 3
    
    @staticmethod
    def _calculate_idea_generation(profile_data: Dict[str, Any]) -> float:
        """Calculate idea generation sub-score"""
        innovation = profile_data.get("innovation", {})
        
        ideas_per_employee = innovation.get("ideas_per_employee", 0.0)
        idea_pipeline = innovation.get("idea_pipeline", 50.0)
        innovation_programs = innovation.get("innovation_programs", 50.0)
        
        ideas_score = ScoringCalculator.normalize_score(ideas_per_employee, 0, 10)
        pipeline_score = idea_pipeline
        programs_score = innovation_programs
        
        return (ideas_score + pipeline_score + programs_score) / 3
    
    @staticmethod
    def _calculate_success_rate(profile_data: Dict[str, Any]) -> float:
        """Calculate innovation success rate sub-score"""
        innovation = profile_data.get("innovation", {})
        
        success_rate = innovation.get("success_rate", 0.0)
        time_to_market = innovation.get("time_to_market", 50.0)
        roi = innovation.get("roi", 0.0)
        
        success_score = ScoringCalculator.normalize_score(success_rate, 0, 100)
        time_score = ScoringCalculator.normalize_score(100 - time_to_market, 0, 100)  # Invert
        roi_score = ScoringCalculator.normalize_score(roi, -50, 200)
        
        return (success_score + time_score + roi_score) / 3
    
    @staticmethod
    def _interpret_score(score: float, level: str) -> str:
        """Interpret the score"""
        interpretations = {
            "not_ready": "Not Ready - Limited innovation capability",
            "developing": "Developing - Developing innovation culture",
            "ready": "Ready - Adequate innovation readiness",
            "highly_ready": "Highly Ready - Innovation leader"
        }
        return interpretations.get(level, "Unknown")
