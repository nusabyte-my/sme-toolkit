# Multi-Modal AI Provider System

This document describes the multi-provider AI system with automatic fallbacks, tier-based access, and support for text, image, and video generation.

## Overview

The SME Toolkit uses a sophisticated provider routing system that:
- Automatically selects the best available AI provider based on user tier
- Falls back to alternative providers if the primary fails
- Enforces rate limits based on subscription tier
- Supports multiple modalities: LLM (text), Image, and Video generation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Provider Router                        │
│  (Selects provider based on tier, availability, fallback)   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ LLM Router  │  │Image Router │  │Video Router │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐        │
│  │  Providers  │  │  Providers  │  │  Providers  │        │
│  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │        │
│  │ │  Groq   │ │  │ │ Imagen  │ │  │ │  Veo 3  │ │        │
│  │ ├─────────┤ │  │ ├─────────┤ │  │ ├─────────┤ │        │
│  │ │ Gemini  │ │  │ │ FLUX.2  │ │  │ │Kling AI │ │        │
│  │ ├─────────┤ │  │ ├─────────┤ │  │ ├─────────┤ │        │
│  │ │ Mistral │ │  │ │Stability│ │  │ │  Nano   │ │        │
│  │ ├─────────┤ │  │ └─────────┘ │  │ │ Banana  │ │        │
│  │ │DeepSeek │ │  └─────────────┘  │ └─────────┘ │        │
│  │ └─────────┘ │                   └─────────────┘        │
│  └─────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

## Supported Providers

### LLM Providers

| Provider | Model | Free Tier | Speed | Best For |
|----------|-------|-----------|-------|----------|
| **Groq** | Llama 3.3 70B | 14,400 req/day | 300+ tok/sec | Speed-critical tasks |
| **Mistral** | mistral-small | 1B tokens/month | Moderate | Cost-effective quality |
| **DeepSeek** | deepseek-chat | Generous | Good | Reasoning tasks |
| **Gemini Flash** | gemini-2.0-flash | 1M tokens/min | Fast | General purpose |
| **Gemini Pro** | gemini-2.0-pro | Limited | Moderate | High-quality output |

### Image Providers

| Provider | Model | Quality | Best For |
|----------|-------|---------|----------|
| **Gemini Image** | gemini-2.0-flash-exp | Good | Quick generation |
| **Imagen 4** | imagen-4.0 | Excellent | High-quality images |
| **FLUX.2** | flux-schnell | High | Open-source, fast |
| **Stability AI** | SDXL | Good | Customizable |

### Video Providers

| Provider | Pricing | Quality | Max Duration |
|----------|---------|---------|--------------|
| **Veo 3** | $0.40-0.75/sec | 1080p HD | 8 sec (extendable) |
| **Veo 3 Fast** | $0.15/sec | 720p | 8 sec |
| **Kling AI** | Credit-based | Up to 1080p | 3 min |
| **Nano Banana** | Via Gemini | High | Variable |

## Configuration

### Environment Variables

Add the following to your `.env` file:

```env
# Primary Provider (Required)
GEMINI_API_KEY=your-gemini-api-key

# LLM Providers (Optional - enables fallbacks)
GROQ_API_KEY=your-groq-api-key
MISTRAL_API_KEY=your-mistral-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key

# Image Providers (Optional)
REPLICATE_API_KEY=your-replicate-api-key  # For FLUX.2
STABILITY_API_KEY=your-stability-api-key

# Video Providers (Optional)
KLING_API_KEY=your-kling-api-key
```

### Provider Priority

Configure provider priority in `config.py`:

```python
llm_provider_priority: str = "gemini,groq,mistral,deepseek"
image_provider_priority: str = "gemini,flux,stability"
video_provider_priority: str = "veo3,kling,nanobanana"
```

## Subscription Tiers

### Free Tier ($0)
- **LLM**: Groq → Mistral → DeepSeek (50 requests/day)
- **Image**: FLUX.2 (10 images/day)
- **Video**: Not available
- **Features**: Basic BMC, Lead Scoring, Copywriting, Visual Studio

### SME Tier ($19/month)
- **LLM**: Gemini Flash → Groq → Mistral (500 requests/day)
- **Image**: Gemini + FLUX (50 images/day)
- **Video**: Veo 3 Fast (5 videos/day, 10-sec max)
- **Features**: All Free features + BMC Analysis, Strategy Advisor, Growth Score, Video Studio, Analytics

### Business Tier ($49/month)
- **LLM**: Gemini Pro → Gemini Flash → Groq (2000 requests/day)
- **Image**: Imagen 4 + Nano Banana + FLUX (200 images/day)
- **Video**: Veo 3 + Kling AI (20 videos/day, 30-sec max)
- **Features**: All SME features + API Access, Priority Processing, Advanced Analytics

### Enterprise Tier (Custom)
- **LLM**: Full access to all providers (10000 requests/day)
- **Image**: Unlimited providers (1000 images/day)
- **Video**: All providers (100 videos/day, 60-sec max)
- **Features**: All features + White-label, SSO, Custom Integrations, Dedicated Support

## API Endpoints

### Subscription Management

```http
GET /api/v1/subscription/tier
```
Returns current tier, features, limits, and available providers.

```http
GET /api/v1/subscription/usage
```
Returns current usage statistics against daily limits.

```http
GET /api/v1/subscription/tiers
```
Returns all available tiers with pricing and features.

```http
POST /api/v1/subscription/upgrade
Content-Type: application/json

{
  "tier": "sme",
  "stripe_token": "tok_xxx"  // Optional for demo mode
}
```
Initiates tier upgrade.

### Provider Status

```http
GET /api/v1/providers/status
```
Returns status of all configured providers.

```http
GET /api/v1/providers/available
```
Returns providers available for the current user's tier.

```http
GET /api/v1/providers/info/{provider_name}
```
Returns detailed information about a specific provider.

## Usage Examples

### Python - Using the Provider Router

```python
from app.providers.router import get_provider_router
from app.providers.base import LLMRequest

router = get_provider_router()

# Make an LLM request
request = LLMRequest(
    prompt="Explain quantum computing",
    user_id="user123",
    tier="sme",
    temperature=0.7
)

response = await router.route_llm_request(request, "user123", "sme")

if response.success:
    print(f"Response from {response.provider_name}:")
    print(response.content)
else:
    print(f"Error: {response.error}")
```

### Frontend - Using TierContext

```tsx
import { useTier, FeatureGate } from './contexts/TierContext';

function MyComponent() {
  const { tier, checkFeature, usage } = useTier();

  return (
    <div>
      <p>Current tier: {tier}</p>
      <p>LLM requests remaining: {usage?.llm.remaining}</p>

      <FeatureGate feature="strategy_advisor">
        <StrategyAdvisor />
      </FeatureGate>
    </div>
  );
}
```

## Rate Limiting

Rate limits are enforced at two levels:
1. **Per-minute limits**: Prevents burst usage
2. **Daily limits**: Resets at midnight UTC

When a limit is reached:
- The API returns a `429 Too Many Requests` response
- The response includes time until reset
- The frontend displays an upgrade prompt

## Fallback Behavior

When a provider fails, the system automatically:
1. Logs the error
2. Tries the next provider in the priority list
3. Continues until success or all providers exhausted
4. Returns a mock response as final fallback (in development)

```
Primary Provider → Secondary Provider → Tertiary Provider → Mock Response
```

## Adding New Providers

### 1. Create Provider Class

```python
# app/providers/llm/new_provider.py
from app.providers.base import LLMProvider, RateLimits

class NewProvider(LLMProvider):
    name = "new_provider"

    async def is_available(self) -> bool:
        return self._is_configured

    async def generate_text(self, prompt: str, **kwargs) -> str:
        # Implementation
        pass

    async def generate_json(self, prompt: str, **kwargs) -> dict:
        # Implementation
        pass
```

### 2. Add to Router

```python
# In router.py _init_llm_providers()
if settings.new_provider_api_key:
    from app.providers.llm.new_provider import NewProvider
    self.llm_providers["new_provider"] = NewProvider(settings.new_provider_api_key)
```

### 3. Add to Tier Config

```python
# In router.py TIER_PROVIDER_CONFIG
"sme": {
    "llm": ["gemini", "groq", "new_provider", "mistral"],
    ...
}
```

## Monitoring

The system logs:
- Provider selection decisions
- Fallback events
- Rate limit violations
- Error details

Access logs via:
```python
import logging
logging.getLogger("app.providers").setLevel(logging.DEBUG)
```

## Troubleshooting

### Provider Not Available
- Check API key is set in `.env`
- Verify the provider package is installed
- Check provider status endpoint

### Rate Limit Exceeded
- Check usage endpoint for current consumption
- Consider upgrading tier
- Wait for daily reset (midnight UTC)

### Fallback Not Working
- Ensure fallback providers are configured
- Check provider priority order
- Verify fallback providers have valid API keys
