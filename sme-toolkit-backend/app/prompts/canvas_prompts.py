ENHANCE_PROMPT = """You are a helpful assistant that improves business descriptions.
Take the following business idea and make it more detailed and compelling while keeping the core concept intact.
Add specificity about target market, unique value, and key differentiators.

Original: {original}

Provide an enhanced version in 2-3 sentences."""


CANVAS_SYSTEM_PROMPT = """You are an expert business strategist specializing in Business Model Canvas methodology.

Your role is to analyze business descriptions and generate comprehensive 9-block canvases that are:
- Actionable and specific (not generic advice)
- Tailored to the specific business context
- Interconnected (blocks should relate logically)

Always respond with valid JSON matching the required schema."""


CANVAS_GENERATION_PROMPT = """Generate a comprehensive Business Model Canvas for the following business:

Business Description: {description}

{user_context}

Create a detailed 9-block canvas with 3-5 specific, actionable items for each block:

1. Key Partners - Strategic partners, suppliers, allies
2. Key Activities - Core operations and processes
3. Key Resources - Essential assets (physical, intellectual, human, financial)
4. Value Propositions - Unique value delivered to customers
5. Customer Relationships - How you interact with customers
6. Channels - How you reach and deliver to customers
7. Customer Segments - Target market groups
8. Cost Structure - Major costs and expenses
9. Revenue Streams - How you generate income

Return a JSON object with these exact keys (camelCase):
keyPartners, keyActivities, keyResources, valuePropositions, customerRelationships, channels, customerSegments, costStructure, revenueStreams

Each value should be an array of strings. Be specific to this business, not generic."""
