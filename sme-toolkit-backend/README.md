# SME Growth Toolkit - Backend API

Multi-agent AI backend for SME business tools powered by LangGraph and multiple AI providers with automatic fallback support.

## Features

### AI Agents
- **Business Model Canvas Generator** - Conversational BMC discovery
- **Lead Manager** - Scoring & email generation
- **Marketing Copywriter** - Content generation
- **Visual Generator** - Image creation/editing
- **Video Generator** - Scripts, storyboards, video
- **Strategy Advisor** - Multi-agent analysis with growth scoring

### Multi-Provider AI System
- **4 LLM Providers**: Groq, Gemini, Mistral, DeepSeek
- **3 Image Providers**: Gemini/Imagen, FLUX.2, Stability AI
- **3 Video Providers**: Veo 3, Kling AI, Nano Banana
- **Automatic Fallbacks**: Seamlessly switches if a provider fails
- **Tier-Based Access**: Different providers per subscription tier
- **Rate Limiting**: Per-user daily and per-minute limits

### Other Features
- **n8n Integration**: Webhook endpoints for workflow automation
- **JWT Authentication**: Secure API access
- **Async Job Queue**: SQLite-based job tracking

## Quick Start

### 1. Setup Environment

```bash
cd sme-toolkit-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET_KEY=your_secure_secret

# Optional - Enable provider fallbacks
GROQ_API_KEY=your_groq_api_key
MISTRAL_API_KEY=your_mistral_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
REPLICATE_API_KEY=your_replicate_api_key
STABILITY_API_KEY=your_stability_api_key
KLING_API_KEY=your_kling_api_key
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

### Get a JWT Token

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Default credentials:
- `admin` / `admin123`
- `n8n` / `n8n_webhook_secret`

## Subscription Tiers

| Tier | Price | LLM Requests | Images | Videos |
|------|-------|--------------|--------|--------|
| Free | $0 | 50/day | 10/day | - |
| SME | $19/mo | 500/day | 50/day | 5/day |
| Business | $49/mo | 2000/day | 200/day | 20/day |
| Enterprise | Custom | 10000/day | 1000/day | 100/day |

### Provider Access by Tier

| Tier | LLM Providers | Image Providers | Video Providers |
|------|---------------|-----------------|-----------------|
| Free | Groq, Mistral, DeepSeek | FLUX | - |
| SME | Gemini, Groq, Mistral | Gemini, FLUX | Veo Fast |
| Business | Gemini Pro, Gemini, Groq | Imagen 4, Nano Banana, FLUX | Veo 3, Kling |
| Enterprise | All | All | All |

## API Endpoints

### Subscription & Providers

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/subscription/tier` | GET | Get current tier and features |
| `/api/v1/subscription/usage` | GET | Get usage statistics |
| `/api/v1/subscription/tiers` | GET | List all available tiers |
| `/api/v1/subscription/upgrade` | POST | Upgrade tier |
| `/api/v1/providers/status` | GET | Provider availability |
| `/api/v1/providers/available` | GET | Providers for user's tier |

### Business Canvas

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/canvas/generate` | POST | Generate canvas |
| `/api/v1/canvas/enhance` | POST | Enhance description |
| `/api/v1/bmc/session` | POST | Start chat session |
| `/api/v1/bmc/message` | POST | Send chat message |
| `/api/v1/bmc/analyze` | POST | Run multi-agent analysis |

### Leads

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/leads/score` | POST | Score a lead |
| `/api/v1/leads/email` | POST | Generate cold email |
| `/api/v1/leads/analyze` | POST | Deep analysis |

### Content Generation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/copywriter/generate` | POST | Generate marketing copy |
| `/api/v1/visual/generate` | POST | Generate image |
| `/api/v1/visual/edit` | POST | Edit image |
| `/api/v1/video/script` | POST | Generate video script |
| `/api/v1/video/generate` | POST | Generate video |

### Strategy

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/strategy/generate` | POST | Generate strategic advice |
| `/api/v1/strategy/growth-plan` | POST | 6-month growth plan |
| `/api/v1/scoring/calculate` | POST | Calculate growth score |

## Project Structure

```
sme-toolkit-backend/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── auth.py                 # JWT authentication
│   ├── database.py             # SQLAlchemy models
│   ├── api/v1/
│   │   ├── router.py           # API routes
│   │   ├── webhooks.py         # n8n webhooks
│   │   └── endpoints/          # API endpoints
│   ├── agents/                 # LangGraph agents
│   │   ├── orchestrator.py
│   │   ├── bmc_orchestrator.py
│   │   ├── canvas_agent.py
│   │   ├── lead_agent.py
│   │   ├── copywriter_agent.py
│   │   ├── visual_agent.py
│   │   ├── video_agent.py
│   │   ├── strategy_agent.py
│   │   ├── growth_agent.py
│   │   ├── market_agent.py
│   │   ├── finance_agent.py
│   │   ├── operations_agent.py
│   │   └── ideation_agent.py
│   ├── providers/              # AI Provider System
│   │   ├── base.py             # Base classes
│   │   ├── router.py           # Provider routing
│   │   ├── rate_limiter.py     # Rate limiting
│   │   ├── llm/                # LLM providers
│   │   │   ├── groq_provider.py
│   │   │   ├── mistral_provider.py
│   │   │   ├── deepseek_provider.py
│   │   │   └── gemini_provider.py
│   │   ├── image/              # Image providers
│   │   │   ├── gemini_image_provider.py
│   │   │   ├── flux_provider.py
│   │   │   └── stability_provider.py
│   │   └── video/              # Video providers
│   │       ├── veo_provider.py
│   │       ├── kling_provider.py
│   │       └── nanobanana_provider.py
│   ├── services/               # Business logic
│   │   ├── tier_service.py
│   │   ├── growth_score_service.py
│   │   └── ...
│   ├── tools/                  # AI tools
│   ├── prompts/                # Prompt templates
│   └── schemas/                # Pydantic models
├── docs/
│   └── MULTI_PROVIDER_AI.md    # Provider documentation
├── requirements.txt
└── README.md
```

## Multi-Provider System

See [MULTI_PROVIDER_AI.md](docs/MULTI_PROVIDER_AI.md) for detailed documentation.

### Quick Example

```python
from app.providers.router import get_provider_router
from app.providers.base import LLMRequest

router = get_provider_router()

request = LLMRequest(
    prompt="Analyze this business idea",
    user_id="user123",
    tier="sme"
)

response = await router.route_llm_request(request, "user123", "sme")
print(f"Response from {response.provider_name}: {response.content}")
```

### Fallback Chain

```
Primary Provider → Secondary Provider → Tertiary Provider → Mock Response
```

If the primary provider fails (rate limited, error, etc.), the system automatically tries the next provider in the chain.

## Development

### Running Tests

```bash
pytest
```

### Adding a New Agent

1. Create agent in `app/agents/new_agent.py`
2. Add schemas in `app/schemas/new_agent.py`
3. Create prompts in `app/prompts/new_agent_prompts.py`
4. Add endpoint in `app/api/v1/endpoints/new_agent.py`
5. Register in `app/agents/orchestrator.py`
6. Add to router in `app/api/v1/router.py`

### Adding a New Provider

1. Create provider in `app/providers/{modality}/new_provider.py`
2. Implement required methods from base class
3. Add API key to `app/config.py`
4. Register in `app/providers/router.py`
5. Add to tier configuration

## Webhook Integration (n8n)

### Webhook Request Format

```json
{
  "action": "score",
  "data": {
    "lead": {
      "name": "John Smith",
      "company": "Acme Corp"
    }
  },
  "callback_url": "https://your-n8n.com/webhook/callback",
  "sync": true
}
```

### Available Webhooks

| Endpoint | Description |
|----------|-------------|
| `POST /webhook/canvas` | Generate Business Model Canvas |
| `POST /webhook/leads` | Lead scoring & email generation |
| `POST /webhook/copywriter` | Marketing copy generation |
| `POST /webhook/visual` | Image generation/editing |
| `POST /webhook/video` | Video scripts & generation |
| `POST /webhook/strategy` | Strategic business advice |

## License

Proprietary - All rights reserved.
