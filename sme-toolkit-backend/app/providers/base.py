"""Base classes for AI providers with fallback support"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Literal, TypedDict
from dataclasses import dataclass, field
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class ProviderModality(str, Enum):
    """Types of AI modalities"""
    LLM = "llm"
    IMAGE = "image"
    VIDEO = "video"


@dataclass
class RateLimits:
    """Rate limit configuration for a provider"""
    requests_per_minute: int = 60
    requests_per_day: int = 1000
    tokens_per_minute: int = 100000
    tokens_per_day: int = 1000000


@dataclass
class ProviderRequest:
    """Base request for any provider"""
    prompt: str
    user_id: str
    tier: str = "free"
    temperature: float = 0.7
    max_tokens: int = 2048
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMRequest(ProviderRequest):
    """Request for LLM providers"""
    system_prompt: Optional[str] = None
    response_format: Optional[Literal["text", "json"]] = "text"
    json_schema: Optional[Dict[str, Any]] = None


@dataclass
class ImageRequest(ProviderRequest):
    """Request for image generation providers"""
    style: Optional[str] = None
    aspect_ratio: str = "1:1"
    resolution: str = "1024x1024"
    reference_image: Optional[str] = None  # Base64 encoded


@dataclass
class VideoRequest(ProviderRequest):
    """Request for video generation providers"""
    duration: int = 5  # seconds
    resolution: str = "720p"
    aspect_ratio: str = "16:9"
    style: Optional[str] = None
    audio: bool = False
    reference_image: Optional[str] = None  # Base64 encoded


@dataclass
class ProviderResponse:
    """Base response from any provider"""
    success: bool
    provider_name: str
    content: Optional[str] = None
    error: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse(ProviderResponse):
    """Response from LLM providers"""
    tokens_used: int = 0


@dataclass
class ImageResponse(ProviderResponse):
    """Response from image providers"""
    image_data: Optional[str] = None  # Base64 encoded
    image_url: Optional[str] = None


@dataclass
class VideoResponse(ProviderResponse):
    """Response from video providers"""
    video_data: Optional[str] = None  # Base64 encoded
    video_url: Optional[str] = None
    job_id: Optional[str] = None  # For async generation
    status: str = "completed"  # pending, processing, completed, failed


class AIProvider(ABC):
    """Abstract base class for all AI providers"""

    name: str = "base"
    modality: ProviderModality = ProviderModality.LLM

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._is_configured = bool(api_key)

    @property
    def is_configured(self) -> bool:
        """Check if provider has valid configuration"""
        return self._is_configured

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is currently available (not rate limited, etc.)"""
        pass

    @abstractmethod
    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        """Execute a request against this provider"""
        pass

    def get_rate_limits(self) -> RateLimits:
        """Get rate limits for this provider"""
        return RateLimits()

    def __str__(self) -> str:
        return f"{self.name} ({self.modality.value})"


class LLMProvider(AIProvider):
    """Base class for LLM/text generation providers"""

    modality = ProviderModality.LLM

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """Generate text from a prompt"""
        pass

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate structured JSON output"""
        pass

    async def execute(self, request: ProviderRequest) -> LLMResponse:
        """Execute an LLM request"""
        try:
            if isinstance(request, LLMRequest) and request.response_format == "json":
                content = await self.generate_json(
                    prompt=request.prompt,
                    schema=request.json_schema,
                    system_prompt=request.system_prompt,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )
                return LLMResponse(
                    success=True,
                    provider_name=self.name,
                    content=str(content),
                    metadata={"json_response": content}
                )
            else:
                system_prompt = request.metadata.get("system_prompt") if isinstance(request, ProviderRequest) else None
                if isinstance(request, LLMRequest):
                    system_prompt = request.system_prompt

                content = await self.generate_text(
                    prompt=request.prompt,
                    system_prompt=system_prompt,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )
                return LLMResponse(
                    success=True,
                    provider_name=self.name,
                    content=content
                )
        except Exception as e:
            logger.error(f"LLM provider {self.name} error: {e}")
            return LLMResponse(
                success=False,
                provider_name=self.name,
                error=str(e)
            )


class ImageProvider(AIProvider):
    """Base class for image generation providers"""

    modality = ProviderModality.IMAGE

    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        style: Optional[str] = None,
        aspect_ratio: str = "1:1",
        resolution: str = "1024x1024",
        **kwargs
    ) -> str:
        """Generate an image and return base64 encoded data"""
        pass

    async def execute(self, request: ProviderRequest) -> ImageResponse:
        """Execute an image generation request"""
        try:
            if isinstance(request, ImageRequest):
                image_data = await self.generate_image(
                    prompt=request.prompt,
                    style=request.style,
                    aspect_ratio=request.aspect_ratio,
                    resolution=request.resolution,
                    reference_image=request.reference_image
                )
            else:
                image_data = await self.generate_image(
                    prompt=request.prompt,
                    style=request.metadata.get("style"),
                    aspect_ratio=request.metadata.get("aspect_ratio", "1:1"),
                    resolution=request.metadata.get("resolution", "1024x1024")
                )

            return ImageResponse(
                success=True,
                provider_name=self.name,
                image_data=image_data
            )
        except Exception as e:
            logger.error(f"Image provider {self.name} error: {e}")
            return ImageResponse(
                success=False,
                provider_name=self.name,
                error=str(e)
            )


class VideoProvider(AIProvider):
    """Base class for video generation providers"""

    modality = ProviderModality.VIDEO

    @abstractmethod
    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        audio: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a video and return result with URL or base64 data"""
        pass

    async def execute(self, request: ProviderRequest) -> VideoResponse:
        """Execute a video generation request"""
        try:
            if isinstance(request, VideoRequest):
                result = await self.generate_video(
                    prompt=request.prompt,
                    duration=request.duration,
                    resolution=request.resolution,
                    aspect_ratio=request.aspect_ratio,
                    audio=request.audio,
                    reference_image=request.reference_image
                )
            else:
                result = await self.generate_video(
                    prompt=request.prompt,
                    duration=request.metadata.get("duration", 5),
                    resolution=request.metadata.get("resolution", "720p"),
                    aspect_ratio=request.metadata.get("aspect_ratio", "16:9"),
                    audio=request.metadata.get("audio", False)
                )

            return VideoResponse(
                success=True,
                provider_name=self.name,
                video_url=result.get("video_url"),
                video_data=result.get("video_data"),
                job_id=result.get("job_id"),
                status=result.get("status", "completed")
            )
        except Exception as e:
            logger.error(f"Video provider {self.name} error: {e}")
            return VideoResponse(
                success=False,
                provider_name=self.name,
                error=str(e)
            )


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for fallback/testing"""

    name = "mock"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self._is_configured = True
        self.logger = logging.getLogger(__name__)

    async def is_available(self) -> bool:
        return True

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        return f"[Mock Response] This is a placeholder response for: {prompt[:100]}..."

    async def generate_json(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        self.logger.info(f"MockLLMProvider.generate_json - Prompt (first 300 chars): {prompt_lower[:300]}")
        
        template_mapping = {
            "scamper": "SCAMPER-based Innovation",
            "mind_map": "Mind Mapping",
            "swot": "SWOT Analysis",
            "blue_ocean": "Blue Ocean Strategy",
            "lean_startup": "Lean Startup",
            "design_thinking": "Design Thinking",
            "first_principles": "First Principles",
            "reverse_engineering": "Reverse Engineering"
        }
        
        detected_template = None
        for template_name, template_display in template_mapping.items():
            if template_name in prompt_lower:
                detected_template = template_name
                break
        
        self.logger.info(f"MockLLMProvider.generate_json - Detected template: {detected_template}")
        
        if detected_template:
            template_ideas = self._get_template_specific_ideas(detected_template)
            self.logger.info(f"MockLLMProvider.generate_json - Returning {len(template_ideas)} template-specific ideas")
            return {
                "ideas": template_ideas,
                "insights": [
                    f"{detected_template.replace('_', ' ').title()} framework applied successfully",
                    "Template-specific methodology enhances ideation quality",
                    "Structured approach leads to more comprehensive solutions"
                ],
                "recommendations": [
                    f"Continue using {detected_template.replace('_', ' ').title()} for related projects",
                    "Combine multiple templates for comprehensive analysis",
                    "Document insights for future reference"
                ]
            }
        elif "brainstorm" in prompt_lower or "ideas" in prompt_lower:
            self.logger.info(f"MockLLMProvider.generate_json - Returning default brainstorm ideas")
            return {
                "ideas": [
                    {
                        "id": "mock-idea-1",
                        "title": "Gamified Loyalty Program",
                        "description": "Implement a points-based loyalty system with challenges, leaderboards, and exclusive rewards to boost customer engagement and retention.",
                        "category": "product",
                        "impact": "high",
                        "effort": "medium",
                        "innovation_type": "disruptive",
                        "feasibility_score": 75,
                        "novelty_score": 80,
                        "value_score": 85,
                        "tags": ["loyalty", "gamification", "engagement"],
                        "implementation_steps": ["Design gamification mechanics", "Develop reward tiers", "Launch pilot program"],
                        "risks": ["May not appeal to all customer segments", "Requires ongoing content updates"],
                        "metrics": ["Customer retention rate", "Daily active users", "Reward redemption rate"]
                    },
                    {
                        "id": "mock-idea-2",
                        "title": "Personalized Recommendations",
                        "description": "Use AI-powered recommendation engine to provide personalized product suggestions based on browsing history and purchase patterns.",
                        "category": "service",
                        "impact": "high",
                        "effort": "high",
                        "innovation_type": "incremental",
                        "feasibility_score": 85,
                        "novelty_score": 60,
                        "value_score": 90,
                        "tags": ["ai", "personalization", "recommendations"],
                        "implementation_steps": ["Collect user behavior data", "Train ML models", "A/B test recommendations"],
                        "risks": ["Privacy concerns", "Cold start problem for new users"],
                        "metrics": ["Conversion rate", "Click-through rate", "Average order value"]
                    },
                    {
                        "id": "mock-idea-3",
                        "title": "Subscription Model",
                        "description": "Introduce a subscription-based model with exclusive benefits, free shipping, and early access to new products to create recurring revenue.",
                        "category": "business model",
                        "impact": "high",
                        "effort": "medium",
                        "innovation_type": "disruptive",
                        "feasibility_score": 80,
                        "novelty_score": 70,
                        "value_score": 95,
                        "tags": ["subscription", "revenue", "retention"],
                        "implementation_steps": ["Define subscription tiers", "Calculate pricing strategy", "Build subscription management system"],
                        "risks": ["Cannibalizes one-time purchases", "Churn management complexity"],
                        "metrics": ["Subscription rate", "Customer lifetime value", "Churn rate"]
                    }
                ],
                "insights": [
                    "Customer retention is 5x cheaper than acquisition",
                    "Personalization increases engagement by 40%",
                    "Loyalty programs can increase customer value by 30%"
                ],
                "recommendations": [
                    "Start with a pilot loyalty program to test engagement",
                    "Implement basic personalization before full AI integration",
                    "Design subscription tiers based on customer segments"
                ]
            }
        elif "trends" in prompt_lower:
            return {
                "trends": [
                    {
                        "trend": "AI-Powered Personalization",
                        "description": "Increasing use of artificial intelligence to deliver personalized experiences across all touchpoints.",
                        "relevance_score": 90,
                        "opportunities": ["Improved customer satisfaction", "Higher conversion rates", "Reduced cart abandonment"],
                        "threats": ["Data privacy regulations", "Implementation complexity"],
                        "timeframe": "growing"
                    },
                    {
                        "trend": "Social Commerce",
                        "description": "Integration of e-commerce directly into social media platforms.",
                        "relevance_score": 85,
                        "opportunities": ["Expanded reach", "Native checkout experience", "Influencer partnerships"],
                        "threats": ["Platform dependency", "Commission fees"],
                        "timeframe": "growing"
                    }
                ],
                "insights": [
                    "Personalization is becoming a customer expectation",
                    "Social commerce is reshaping the purchase journey",
                    "Mobile-first strategies are essential"
                ],
                "recommendations": [
                    "Invest in AI capabilities for personalization",
                    "Develop social media presence with commerce features",
                    "Optimize mobile experience across all channels"
                ]
            }
        elif "competitor" in prompt_lower:
            return {
                "competitors": [
                    {
                        "competitor": "Major Competitor A",
                        "strengths": ["Brand recognition", "Large product catalog", "Fast shipping"],
                        "weaknesses": ["Limited personalization", "Higher prices", "Poor mobile app"],
                        "strategies": ["Focus on personalized experience", "Competitive pricing", "Superior mobile UX"],
                        "opportunities": ["Capture dissatisfied customers", "Target underserved segments", "Leverage mobile-first approach"]
                    }
                ],
                "insights": [
                    "Competitors are strong in brand but weak in personalization",
                    "Mobile experience is a key differentiator",
                    "Customer service is an area for competitive advantage"
                ],
                "recommendations": [
                    "Differentiate through superior personalization",
                    "Invest in mobile-first customer experience",
                    "Develop customer service excellence program"
                ]
            }
        elif "opportunity" in prompt_lower:
            return {
                "opportunities": [
                    {
                        "opportunity": "Niche Subscription Service",
                        "market_size": "$5 billion (TAM), $1 billion (SAM), $50 million (SOM)",
                        "growth_rate": "25% CAGR",
                        "competition_level": "low",
                        "barriers_to_entry": ["Customer acquisition", "Supply chain", "Technology"],
                        "success_factors": ["Unique value proposition", "Strong community", "Flexible terms"]
                    }
                ],
                "insights": [
                    "Niche markets offer higher margins and lower competition",
                    "Subscription models provide predictable revenue",
                    "Community building is key to retention"
                ],
                "recommendations": [
                    "Research underserved customer segments",
                    "Develop unique value proposition",
                    "Build community features from day one"
                ]
            }
        elif "product innovation" in prompt_lower or "business model innovation" in prompt_lower:
            return {
                "ideas": [
                    {
                        "id": "mock-innovation-1",
                        "title": "AI-Powered Style Advisor",
                        "description": "Virtual styling assistant that uses computer vision and AI to recommend products based on user preferences and body type.",
                        "category": "product",
                        "impact": "high",
                        "effort": "high",
                        "innovation_type": "disruptive",
                        "feasibility_score": 70,
                        "novelty_score": 85,
                        "value_score": 90,
                        "tags": ["ai", "style", "personalization"],
                        "implementation_steps": ["Develop AI model", "Build user interface", "Train on diverse dataset"],
                        "risks": ["Algorithm bias", "User adoption", "Privacy concerns"],
                        "metrics": ["User engagement", "Conversion rate", "Customer satisfaction"]
                    }
                ],
                "insights": [
                    "AI-powered personalization is a key differentiator",
                    "Virtual try-on reduces returns",
                    "Data-driven insights improve product recommendations"
                ],
                "recommendations": [
                    "Start with basic recommendation features",
                    "Iterate based on user feedback",
                    "Ensure ethical AI practices"
                ]
            }
        
        result = {
            "ideas": [],
            "insights": ["Mock response - no specific action detected"],
            "recommendations": ["Provide more specific action or template"]
        }
        self.logger.info(f"MockLLMProvider.generate_json - Returning default mock response: {result}")
        return result
    
    def _get_template_specific_ideas(self, template: str) -> List[Dict[str, Any]]:
        """Generate template-specific ideas"""
        base_ideas = []
        
        if template == "scamper":
            base_ideas = [
                {
                    "id": "scamper-1",
                    "title": "Substitute: AI-Powered Chat Support",
                    "description": "Replace traditional customer service with AI chatbots for 24/7 support, reducing costs and improving response times.",
                    "category": "service",
                    "impact": "high",
                    "effort": "medium",
                    "innovation_type": "incremental",
                    "feasibility_score": 80,
                    "novelty_score": 65,
                    "value_score": 85,
                    "tags": ["ai", "customer-service", "automation"],
                    "implementation_steps": ["Select AI platform", "Train on FAQs", "Integrate with CRM"],
                    "risks": ["Customer resistance to bots", "Complex queries may fail"],
                    "metrics": ["Response time", "Resolution rate", "Cost savings"]
                },
                {
                    "id": "scamper-2",
                    "title": "Combine: Loyalty + Social Media",
                    "description": "Merge loyalty program with social sharing to reward customers for referrals and social engagement.",
                    "category": "marketing",
                    "impact": "medium",
                    "effort": "low",
                    "innovation_type": "incremental",
                    "feasibility_score": 90,
                    "novelty_score": 70,
                    "value_score": 80,
                    "tags": ["loyalty", "social", "referral"],
                    "implementation_steps": ["Design reward structure", "Add social sharing buttons", "Track referrals"],
                    "risks": ["Low adoption rates", "May attract wrong audience"],
                    "metrics": ["Referral rate", "Social engagement", "New customer acquisition"]
                },
                {
                    "id": "scamper-3",
                    "title": "Adapt: Mobile-First Experience",
                    "description": "Adapt desktop features for mobile-first design to capture on-the-go customers.",
                    "category": "product",
                    "impact": "high",
                    "effort": "medium",
                    "innovation_type": "incremental",
                    "feasibility_score": 85,
                    "novelty_score": 60,
                    "value_score": 90,
                    "tags": ["mobile", "ux", "responsive"],
                    "implementation_steps": ["Audit mobile experience", "Prioritize features", "Implement responsive design"],
                    "risks": ["Feature limitations on mobile", "Development time"],
                    "metrics": ["Mobile conversion rate", "Time on mobile site", "Bounce rate"]
                }
            ]
        elif template == "mind_map":
            base_ideas = [
                {
                    "id": "mindmap-1",
                    "title": "Customer Journey Mapping",
                    "description": "Visualize the entire customer experience from awareness to post-purchase, identifying pain points and opportunities.",
                    "category": "process",
                    "impact": "high",
                    "effort": "medium",
                    "innovation_type": "incremental",
                    "feasibility_score": 85,
                    "novelty_score": 70,
                    "value_score": 90,
                    "tags": ["journey", "mapping", "experience"],
                    "implementation_steps": ["Map touchpoints", "Identify pain points", "Design improvements"],
                    "risks": ["Complex analysis", "Resource intensive"],
                    "metrics": ["Customer satisfaction", "Conversion rate", "NPS"]
                },
                {
                    "id": "mindmap-2",
                    "title": "Retention Ecosystem",
                    "description": "Create interconnected retention strategies including loyalty, engagement, support, and community features.",
                    "category": "strategy",
                    "impact": "high",
                    "effort": "high",
                    "innovation_type": "disruptive",
                    "feasibility_score": 75,
                    "novelty_score": 85,
                    "value_score": 90,
                    "tags": ["retention", "ecosystem", "holistic"],
                    "implementation_steps": ["Map ecosystem components", "Build integrations", "Launch pilot"],
                    "risks": ["Complexity", "Coordination challenges"],
                    "metrics": ["Retention rate", "Engagement rate", "CLV"]
                },
                {
                    "id": "mindmap-3",
                    "title": "Innovation Hub",
                    "description": "Establish a centralized hub for testing and scaling new ideas across the organization.",
                    "category": "process",
                    "impact": "medium",
                    "effort": "high",
                    "innovation_type": "radical",
                    "feasibility_score": 70,
                    "novelty_score": 90,
                    "value_score": 80,
                    "tags": ["innovation", "hub", "scaling"],
                    "implementation_steps": ["Define hub structure", "Build team", "Establish processes"],
                    "risks": ["Cultural resistance", "Slow adoption"],
                    "metrics": ["Ideas generated", "Ideas implemented", "ROI of innovations"]
                }
            ]
        elif template == "swot":
            base_ideas = [
                {
                    "id": "swot-1",
                    "title": "Leverage Strength: Brand Trust",
                    "description": "Capitalize on strong brand reputation to launch premium customer retention features.",
                    "category": "product",
                    "impact": "high",
                    "effort": "medium",
                    "innovation_type": "incremental",
                    "feasibility_score": 85,
                    "novelty_score": 65,
                    "value_score": 90,
                    "tags": ["brand", "premium", "trust"],
                    "implementation_steps": ["Identify premium features", "Set pricing", "Launch to loyal customers"],
                    "risks": ["May alienate price-sensitive customers", "Feature expectations"],
                    "metrics": ["Premium adoption rate", "Revenue per customer", "Brand sentiment"]
                },
                {
                    "id": "swot-2",
                    "title": "Address Weakness: Limited Personalization",
                    "description": "Implement AI-powered personalization to overcome current personalization limitations.",
                    "category": "service",
                    "impact": "high",
                    "effort": "high",
                    "innovation_type": "disruptive",
                    "feasibility_score": 75,
                    "novelty_score": 80,
                    "value_score": 90,
                    "tags": ["personalization", "ai", "customization"],
                    "implementation_steps": ["Collect data", "Train models", "Implement personalization"],
                    "risks": ["Privacy concerns", "Algorithm bias"],
                    "metrics": ["Personalization engagement", "Conversion lift", "Customer satisfaction"]
                },
                {
                    "id": "swot-3",
                    "title": "Seize Opportunity: Mobile Commerce Growth",
                    "description": "Capture the growing mobile commerce trend with optimized mobile experiences.",
                    "category": "product",
                    "impact": "high",
                    "effort": "medium",
                    "innovation_type": "incremental",
                    "feasibility_score": 90,
                    "novelty_score": 70,
                    "value_score": 85,
                    "tags": ["mobile", "commerce", "growth"],
                    "implementation_steps": ["Audit mobile site", "Optimize checkout", "Add mobile features"],
                    "risks": ["Platform fragmentation", "Development cost"],
                    "metrics": ["Mobile conversion", "Mobile revenue share", "App adoption"]
                }
            ]
        elif template == "blue_ocean":
            base_ideas = [
                {
                    "id": "blueocean-1",
                    "title": "Subscription-First Commerce",
                    "description": "Create an uncontested market space with subscription-first purchasing model that eliminates traditional shopping friction.",
                    "category": "business model",
                    "impact": "high",
                    "effort": "high",
                    "innovation_type": "disruptive",
                    "feasibility_score": 70,
                    "novelty_score": 90,
                    "value_score": 85,
                    "tags": ["subscription", "blue-ocean", "uncontested"],
                    "implementation_steps": ["Design subscription tiers", "Build auto-fulfillment", "Launch pilot"],
                    "risks": ["Customer education needed", "Inventory management"],
                    "metrics": ["Subscription rate", "Churn rate", "CLV"]
                },
                {
                    "id": "blueocean-2",
                    "title": "Community-Driven Marketplace",
                    "description": "Build a marketplace where customers actively participate in product development and curation.",
                    "category": "platform",
                    "impact": "high",
                    "effort": "high",
                    "innovation_type": "radical",
                    "feasibility_score": 65,
                    "novelty_score": 95,
                    "value_score": 80,
                    "tags": ["community", "marketplace", "co-creation"],
                    "implementation_steps": ["Build community platform", "Design curation process", "Launch with initial products"],
                    "risks": ["Critical mass required", "Quality control"],
                    "metrics": ["Community engagement", "Co-created products", "User retention"]
                },
                {
                    "id": "blueocean-3",
                    "title": "Eco-Conscious Commerce",
                    "description": "Create a market space focused entirely on sustainable, eco-friendly products with transparent supply chains.",
                    "category": "business model",
                    "impact": "medium",
                    "effort": "medium",
                    "innovation_type": "disruptive",
                    "feasibility_score": 80,
                    "novelty_score": 85,
                    "value_score": 75,
                    "tags": ["sustainable", "eco", "transparency"],
                    "implementation_steps": ["Source eco-products", "Build transparency system", "Market to conscious consumers"],
                    "risks": ["Higher costs", "Limited product selection"],
                    "metrics": ["Eco-product sales", "Customer trust", "Brand advocacy"]
                }
            ]
        elif template == "lean_startup":
            base_ideas = [
                {
                    "id": "lean-1",
                    "title": "MVP: Predictive Churn Model",
                    "description": "Build minimum viable churn prediction model using basic customer data to identify at-risk customers.",
                    "category": "product",
                    "impact": "medium",
                    "effort": "medium",
                    "innovation_type": "incremental",
                    "feasibility_score": 80,
                    "novelty_score": 75,
                    "value_score": 85,
                    "tags": ["mvp", "churn", "prediction"],
                    "implementation_steps": ["Define churn indicators", "Build simple model", "Test with customer service"],
                    "risks": ["Model accuracy", "False positives"],
                    "metrics": ["Churn prediction accuracy", "Intervention success", "Retention improvement"]
                },
                {
                    "id": "lean-2",
                    "title": "Rapid A/B Testing Framework",
                    "description": "Implement lightweight A/B testing for retention features to quickly validate hypotheses.",
                    "category": "process",
                    "impact": "medium",
                    "effort": "low",
                    "innovation_type": "incremental",
                    "feasibility_score": 90,
                    "novelty_score": 70,
                    "value_score": 80,
                    "tags": ["ab-testing", "validation", "lean"],
                    "implementation_steps": ["Select testing tool", "Design first experiment", "Iterate based on results"],
                    "risks": ["Testing fatigue", "Inconclusive results"],
                    "metrics": ["Test iterations", "Conversion improvements", "Feature adoption"]
                },
                {
                    "id": "lean-3",
                    "title": "Customer Development Interviews",
                    "description": "Conduct structured customer interviews to validate retention problems before building solutions.",
                    "category": "research",
                    "impact": "high",
                    "effort": "low",
                    "innovation_type": "incremental",
                    "feasibility_score": 95,
                    "novelty_score": 65,
                    "value_score": 85,
                    "tags": ["customer-development", "interviews", "validation"],
                    "implementation_steps": ["Design interview guide", "Recruit customers", "Synthesize insights"],
                    "risks": ["Bias in interviews", "Small sample size"],
                    "metrics": ["Insights generated", "Validated problems", "Solution accuracy"]
                }
            ]
        elif template == "design_thinking":
            base_ideas = [
                {
                    "id": "dt-1",
                    "title": "Empathize: Customer Retention Journey",
                    "description": "Deep-dive into customer retention challenges through interviews, observation, and journey mapping.",
                    "category": "research",
                    "impact": "high",
                    "effort": "medium",
                    "innovation_type": "incremental",
                    "feasibility_score": 85,
                    "novelty_score": 70,
                    "value_score": 90,
                    "tags": ["empathy", "research", "journey"],
                    "implementation_steps": ["Conduct interviews", "Map journeys", "Identify pain points"],
                    "risks": ["Time intensive", "Subjective insights"],
                    "metrics": ["Customer insights", "Pain points identified", "Empathy score"]
                },
                {
                    "id": "dt-2",
                    "title": "Define: Retention Problem Statement",
                    "description": "Articulate specific retention problems with clear problem statements to guide solution development.",
                    "category": "strategy",
                    "impact": "medium",
                    "effort": "low",
                    "innovation_type": "incremental",
                    "feasibility_score": 95,
                    "novelty_score": 60,
                    "value_score": 80,
                    "tags": ["define", "problem-statement", "focus"],
                    "implementation_steps": ["Synthesize research", "Write problem statements", "Get stakeholder buy-in"],
                    "risks": ["Wrong problem focus", "Stakeholder misalignment"],
                    "metrics": ["Problem clarity", "Solution relevance", "Team alignment"]
                },
                {
                    "id": "dt-3",
                    "title": "Prototype: Quick Retention Solutions",
                    "description": "Create low-fidelity prototypes of retention features to test with customers before full development.",
                    "category": "product",
                    "impact": "medium",
                    "effort": "medium",
                    "innovation_type": "incremental",
                    "feasibility_score": 85,
                    "novelty_score": 75,
                    "value_score": 80,
                    "tags": ["prototype", "testing", "iteration"],
                    "implementation_steps": ["Design prototypes", "Test with customers", "Iterate based on feedback"],
                    "risks": ["Prototype bias", "Limited functionality"],
                    "metrics": ["Prototype iterations", "User feedback quality", "Feature validation"]
                }
            ]
        elif template == "first_principles":
            base_ideas = [
                {
                    "id": "fp-1",
                    "title": "Fundamental: Why Do Customers Leave?",
                    "description": "Challenge assumptions about churn by questioning the fundamental reasons customers disengage.",
                    "category": "strategy",
                    "impact": "high",
                    "effort": "low",
                    "innovation_type": "radical",
                    "feasibility_score": 90,
                    "novelty_score": 85,
                    "value_score": 85,
                    "tags": ["first-principles", "fundamental", "assumptions"],
                    "implementation_steps": ["Question assumptions", "Gather data", "Reframe problem"],
                    "risks": ["Uncomfortable truths", "Cognitive dissonance"],
                    "metrics": ["Assumptions challenged", "New insights", "Strategic pivot"]
                },
                {
                    "id": "fp-2",
                    "title": "Rebuild: Retention from Ground Up",
                    "description": "Design retention strategy from fundamental truths rather than copying competitors.",
                    "category": "strategy",
                    "impact": "high",
                    "effort": "high",
                    "innovation_type": "radical",
                    "feasibility_score": 70,
                    "novelty_score": 90,
                    "value_score": 80,
                    "tags": ["rebuild", "fundamental", "unique"],
                    "implementation_steps": ["Identify fundamentals", "Design unique approach", "Implement and measure"],
                    "risks": ["Unproven approach", "Resource intensive"],
                    "metrics": ["Retention improvement", "Differentiation", "Innovation score"]
                },
                {
                    "id": "fp-3",
                    "title": "Essential: Minimal Retention MVP",
                    "description": "Build only the essential retention features that truly matter, eliminating unnecessary complexity.",
                    "category": "product",
                    "impact": "medium",
                    "effort": "medium",
                    "innovation_type": "disruptive",
                    "feasibility_score": 85,
                    "novelty_score": 80,
                    "value_score": 85,
                    "tags": ["essential", "minimal", "focus"],
                    "implementation_steps": ["Identify essentials", "Remove non-essentials", "Build MVP"],
                    "risks": ["Over-simplification", "Missing value-add features"],
                    "metrics": ["Feature usage", "Retention impact", "Complexity reduction"]
                }
            ]
        elif template == "reverse_engineering":
            base_ideas = [
                {
                    "id": "re-1",
                    "title": "Study: Amazon's Prime Retention",
                    "description": "Analyze Amazon Prime's retention strategies and adapt core principles to your business.",
                    "category": "strategy",
                    "impact": "high",
                    "effort": "medium",
                    "innovation_type": "incremental",
                    "feasibility_score": 80,
                    "novelty_score": 70,
                    "value_score": 85,
                    "tags": ["benchmarking", "amazon", "prime"],
                    "implementation_steps": ["Study Prime model", "Extract principles", "Adapt to business"],
                    "risks": ["Different scale", "Different business model"],
                    "metrics": ["Adoption rate", "Retention impact", "Customer satisfaction"]
                },
                {
                    "id": "re-2",
                    "title": "Analyze: Netflix's Personalization",
                    "description": "Reverse-engineer Netflix's recommendation system to understand their retention mechanics.",
                    "category": "product",
                    "impact": "high",
                    "effort": "high",
                    "innovation_type": "disruptive",
                    "feasibility_score": 70,
                    "novelty_score": 85,
                    "value_score": 80,
                    "tags": ["netflix", "personalization", "recommendations"],
                    "implementation_steps": ["Study Netflix algorithms", "Design simplified version", "Implement and test"],
                    "risks": ["Complex implementation", "Data requirements"],
                    "metrics": ["Recommendation accuracy", "Engagement lift", "Retention improvement"]
                },
                {
                    "id": "re-3",
                    "title": "Adapt: Gaming Loyalty Systems",
                    "description": "Study successful gaming loyalty programs and apply their engagement principles to e-commerce.",
                    "category": "product",
                    "impact": "medium",
                    "effort": "medium",
                    "innovation_type": "disruptive",
                    "feasibility_score": 80,
                    "novelty_score": 85,
                    "value_score": 75,
                    "tags": ["gaming", "loyalty", "gamification"],
                    "implementation_steps": ["Study gaming systems", "Extract engagement principles", "Design e-commerce version"],
                    "risks": ["Different audience", "Cultural fit"],
                    "metrics": ["Engagement rate", "Loyalty adoption", "Retention improvement"]
                }
            ]
        
        return base_ideas


class MockImageProvider(ImageProvider):
    """Mock image provider for fallback/testing"""

    name = "mock"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self._is_configured = True

    async def is_available(self) -> bool:
        return True

    async def generate_image(
        self,
        prompt: str,
        style: Optional[str] = None,
        aspect_ratio: str = "1:1",
        resolution: str = "1024x1024",
        **kwargs
    ) -> str:
        # Return a 1x1 transparent PNG as base64
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


class MockVideoProvider(VideoProvider):
    """Mock video provider for fallback/testing"""

    name = "mock"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self._is_configured = True

    async def is_available(self) -> bool:
        return True

    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        audio: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        return {
            "status": "mock",
            "message": "Video generation is not available in mock mode",
            "prompt_preview": prompt[:100]
        }
