"""Seed ideation templates and categories into the database"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, Base, engine, TemplateCategory, IdeationTemplate


async def seed_categories(db: AsyncSession):
    """Seed default template categories"""
    categories_data = [
        {
            "id": "cat_strategy",
            "user_id": "system",
            "name": "Strategy & Planning",
            "description": "Templates for strategic thinking and business planning",
            "color": "#3B82F6",
            "icon": "Target",
            "is_default": True,
            "template_count": 2
        },
        {
            "id": "cat_innovation",
            "user_id": "system",
            "name": "Innovation & Creativity",
            "description": "Templates for innovative thinking and creative problem solving",
            "color": "#8B5CF6",
            "icon": "Lightbulb",
            "is_default": True,
            "template_count": 4
        },
        {
            "id": "cat_analysis",
            "user_id": "system",
            "name": "Analysis & Research",
            "description": "Templates for market analysis and competitive research",
            "color": "#10B981",
            "icon": "ChartBar",
            "is_default": True,
            "template_count": 2
        }
    ]

    for cat_data in categories_data:
        existing = await db.execute(
            select(TemplateCategory).where(TemplateCategory.id == cat_data["id"])
        )
        if not existing.scalar_one_or_none():
            category = TemplateCategory(**cat_data)
            db.add(category)
            print(f"Created category: {cat_data['name']}")


async def seed_templates(db: AsyncSession):
    """Seed default ideation templates"""
    templates_data = [
        {
            "id": "tpl_scamper",
            "user_id": "system",
            "name": "SCAMPER",
            "description": "Systematic innovation technique using Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse",
            "framework": "scamper",
            "instructions": "Apply each SCAMPER technique to your topic systematically",
            "prompt_template": """Using the SCAMPER technique, generate innovative ideas for: {topic}

Instructions: {instructions}

Apply each SCAMPER dimension:
- Substitute: What can be replaced?
- Combine: What can be combined?
- Adapt: What can be adapted?
- Modify: What can be modified?
- Put to other uses: How else can it be used?
- Eliminate: What can be eliminated?
- Reverse: What can be reversed?

Generate {quantity} innovative ideas with impact, effort, feasibility, novelty, and value scores.

Industry: {industry}
Target Audience: {target_audience}
Innovation Level: {innovation_level}
Constraints: {constraints}""",
            "category_id": "cat_innovation",
            "is_public": True,
            "is_default": True,
            "tags": ["innovation", "creativity", "systematic"]
        },
        {
            "id": "tpl_mind_map",
            "user_id": "system",
            "name": "Mind Map",
            "description": "Visual thinking tool for exploring associations and connections around a central idea",
            "framework": "mind_map",
            "instructions": "Create a mind map by radiating outward from the central topic, connecting related ideas",
            "prompt_template": """Using Mind Mapping, explore and generate innovative ideas for: {topic}

Instructions: {instructions}

Create a mind map structure:
1. Central topic: {topic}
2. Main branches: Core aspects or dimensions
3. Sub-branches: Detailed ideas and connections
4. Cross-connections: Unexpected associations

Generate {quantity} innovative ideas from the mind map with impact, effort, feasibility, novelty, and value scores.

Industry: {industry}
Target Audience: {target_audience}
Innovation Level: {innovation_level}
Constraints: {constraints}""",
            "category_id": "cat_innovation",
            "is_public": True,
            "is_default": True,
            "tags": ["visual", "connections", "exploration"]
        },
        {
            "id": "tpl_swot",
            "user_id": "system",
            "name": "SWOT Analysis",
            "description": "Strategic planning tool analyzing Strengths, Weaknesses, Opportunities, Threats",
            "framework": "swot",
            "instructions": "Analyze the topic through four dimensions: Strengths, Weaknesses, Opportunities, Threats",
            "prompt_template": """Using SWOT Analysis, generate strategic ideas for: {topic}

Instructions: {instructions}

Analyze each dimension:
- Strengths: Internal advantages to leverage
- Weaknesses: Internal limitations to address
- Opportunities: External possibilities to pursue
- Threats: External challenges to mitigate

Generate {quantity} strategic ideas based on SWOT insights with impact, effort, feasibility, novelty, and value scores.

Industry: {industry}
Target Audience: {target_audience}
Innovation Level: {innovation_level}
Constraints: {constraints}""",
            "category_id": "cat_strategy",
            "is_public": True,
            "is_default": True,
            "tags": ["strategy", "planning", "analysis"]
        },
        {
            "id": "tpl_blue_ocean",
            "user_id": "system",
            "name": "Blue Ocean Strategy",
            "description": "Market innovation framework for creating uncontested market space",
            "framework": "blue_ocean",
            "instructions": "Identify how to create new market space by making competition irrelevant",
            "prompt_template": """Using Blue Ocean Strategy, generate disruptive ideas for: {topic}

Instructions: {instructions}

Apply the Four Actions Framework:
- Eliminate: Which factors should be eliminated?
- Reduce: Which factors should be reduced below industry standard?
- Raise: Which factors should be raised above industry standard?
- Create: Which factors should be created that never existed?

Generate {quantity} blue ocean ideas with impact, effort, feasibility, novelty, and value scores.

Industry: {industry}
Target Audience: {target_audience}
Innovation Level: {innovation_level}
Constraints: {constraints}""",
            "category_id": "cat_strategy",
            "is_public": True,
            "is_default": True,
            "tags": ["disruption", "market-creation", "differentiation"]
        },
        {
            "id": "tpl_lean_startup",
            "user_id": "system",
            "name": "Lean Startup",
            "description": "Methodology for developing businesses with rapid experimentation and validated learning",
            "framework": "lean_startup",
            "instructions": "Focus on MVP development, build-measure-learn cycles, and validated learning",
            "prompt_template": """Using Lean Startup methodology, generate testable ideas for: {topic}

Instructions: {instructions}

Apply Lean Startup principles:
- Build: What's the minimum viable product?
- Measure: What key metrics to track?
- Learn: What hypotheses to validate?
- Pivot: When and how to pivot?

Generate {quantity} lean startup ideas with impact, effort, feasibility, novelty, and value scores.

Industry: {industry}
Target Audience: {target_audience}
Innovation Level: {innovation_level}
Constraints: {constraints}""",
            "category_id": "cat_innovation",
            "is_public": True,
            "is_default": True,
            "tags": ["startup", "mvp", "validation"]
        },
        {
            "id": "tpl_design_thinking",
            "user_id": "system",
            "name": "Design Thinking",
            "description": "Human-centered innovation process focusing on empathy, ideation, and prototyping",
            "framework": "design_thinking",
            "instructions": "Follow the five stages: Empathize, Define, Ideate, Prototype, Test",
            "prompt_template": """Using Design Thinking, generate user-centered ideas for: {topic}

Instructions: {instructions}

Apply Design Thinking stages:
- Empathize: Understand user needs and pain points
- Define: Frame the problem statement
- Ideate: Generate diverse solutions
- Prototype: Create testable concepts
- Test: Validate with users

Generate {quantity} design thinking ideas with impact, effort, feasibility, novelty, and value scores.

Industry: {industry}
Target Audience: {target_audience}
Innovation Level: {innovation_level}
Constraints: {constraints}""",
            "category_id": "cat_innovation",
            "is_public": True,
            "is_default": True,
            "tags": ["user-centered", "empathy", "prototyping"]
        },
        {
            "id": "tpl_first_principles",
            "user_id": "system",
            "name": "First Principles",
            "description": "Problem-solving approach breaking down problems to fundamental truths and reasoning up",
            "framework": "first_principles",
            "instructions": "Break down the problem to its fundamental assumptions and build solutions from first principles",
            "prompt_template": """Using First Principles thinking, generate radical ideas for: {topic}

Instructions: {instructions}

Apply First Principles method:
1. Identify assumptions: What are we assuming?
2. Challenge assumptions: Are these assumptions valid?
3. Break down fundamentals: What are the core truths?
4. Reconstruct: Build solutions from fundamentals

Generate {quantity} first principles ideas with impact, effort, feasibility, novelty, and value scores.

Industry: {industry}
Target Audience: {target_audience}
Innovation Level: {innovation_level}
Constraints: {constraints}""",
            "category_id": "cat_innovation",
            "is_public": True,
            "is_default": True,
            "tags": ["radical", "fundamental", "reasoning"]
        },
        {
            "id": "tpl_reverse_engineering",
            "user_id": "system",
            "name": "Reverse Engineering",
            "description": "Analyzing successful solutions to understand and adapt their principles",
            "framework": "reverse_engineering",
            "instructions": "Study successful examples and reverse engineer their success factors",
            "prompt_template": """Using Reverse Engineering, generate ideas by analyzing: {topic}

Instructions: {instructions}

Apply Reverse Engineering approach:
1. Identify successful examples in this space
2. Analyze their success factors and mechanisms
3. Extract transferable principles
4. Adapt and apply to create new solutions

Generate {quantity} reverse engineered ideas with impact, effort, feasibility, novelty, and value scores.

Industry: {industry}
Target Audience: {target_audience}
Innovation Level: {innovation_level}
Constraints: {constraints}""",
            "category_id": "cat_analysis",
            "is_public": True,
            "is_default": True,
            "tags": ["analysis", "learning", "adaptation"]
        }
    ]

    for tpl_data in templates_data:
        existing = await db.execute(
            select(IdeationTemplate).where(IdeationTemplate.id == tpl_data["id"])
        )
        if not existing.scalar_one_or_none():
            template = IdeationTemplate(**tpl_data)
            db.add(template)
            print(f"Created template: {tpl_data['name']}")


async def main():
    """Main seeding function"""
    print("Starting ideation templates seeding...")
    
    async for db in get_db():
        try:
            await seed_categories(db)
            await seed_templates(db)
            await db.commit()
            print("\nSeeding completed successfully!")
            break
        except Exception as e:
            await db.rollback()
            print(f"\nError during seeding: {e}")
            raise


if __name__ == "__main__":
    from sqlalchemy import select
    asyncio.run(main())
