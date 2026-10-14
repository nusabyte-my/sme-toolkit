# SME Toolkit - Complete Setup Guide

This guide walks you through setting up the SME Toolkit with the multi-provider AI system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [API Keys Configuration](#api-keys-configuration)
6. [Provider Configuration](#provider-configuration)
7. [Testing the Setup](#testing-the-setup)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Minimum Version | Check Command |
|----------|----------------|---------------|
| Node.js | 18.x | `node --version` |
| npm | 9.x | `npm --version` |
| Python | 3.10+ | `python --version` |
| pip | 21.x | `pip --version` |

### Required API Keys

At minimum, you need **one** AI provider API key to run the system:

| Provider | Required | Get API Key |
|----------|----------|-------------|
| Google Gemini | Recommended | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| Groq | Alternative | [Groq Console](https://console.groq.com/) |

---

## Quick Start

### 1-Minute Setup (Minimal)

```bash
# Clone and enter directory
cd SME-toolkit

# Backend
cd sme-toolkit-backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
echo GEMINI_API_KEY=your_key_here > .env
echo JWT_SECRET_KEY=your_secret_here >> .env
python -m uvicorn app.main:app --port 8000

# Frontend (new terminal)
cd SME-toolkit
npm install
npm run dev
```

---

## Backend Setup

### Step 1: Create Virtual Environment

```bash
cd sme-toolkit-backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

If you encounter errors, try:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment

Create a `.env` file in the `sme-toolkit-backend` directory:

```bash
cp .env.example .env
```

Or create manually:

```env
# ========================================
# REQUIRED CONFIGURATION
# ========================================

# Primary AI Provider (at least one required)
GEMINI_API_KEY=your_gemini_api_key_here

# JWT Secret (generate a secure random string)
JWT_SECRET_KEY=your_super_secure_secret_key_here

# ========================================
# OPTIONAL: LLM PROVIDER FALLBACKS
# ========================================

# Groq - Free tier: 14,400 requests/day
# Get key: https://console.groq.com/
GROQ_API_KEY=

# Mistral - Free tier: 1B tokens/month
# Get key: https://console.mistral.ai/
MISTRAL_API_KEY=

# DeepSeek - Generous free tier
# Get key: https://platform.deepseek.com/
DEEPSEEK_API_KEY=

# ========================================
# OPTIONAL: IMAGE GENERATION PROVIDERS
# ========================================

# Replicate (for FLUX.2) - Pay-per-use
# Get key: https://replicate.com/account/api-tokens
REPLICATE_API_KEY=

# Stability AI - Pay-per-use
# Get key: https://platform.stability.ai/
STABILITY_API_KEY=

# ========================================
# OPTIONAL: VIDEO GENERATION PROVIDERS
# ========================================

# Kling AI - Credit-based
# Get key: https://klingai.com/
KLING_API_KEY=

# ========================================
# PROVIDER PRIORITY (Optional)
# ========================================

# Order of fallback preference
LLM_PROVIDER_PRIORITY=gemini,groq,mistral,deepseek
IMAGE_PROVIDER_PRIORITY=gemini,flux,stability
VIDEO_PROVIDER_PRIORITY=veo3,kling,nanobanana

# ========================================
# DATABASE (Optional - defaults to SQLite)
# ========================================

# DATABASE_URL=sqlite:///./sme_toolkit.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/sme_toolkit

# ========================================
# CACHE (Optional - defaults to in-memory)
# ========================================

# REDIS_URL=redis://localhost:6379/0
```

### Step 4: Initialize Database

The database is automatically initialized on first run. To manually initialize:

```bash
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

### Step 5: Run the Server

**Development mode:**
```bash
python -m uvicorn app.main:app --reload --port 8000
```

**Production mode:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 6: Verify Backend

Visit http://localhost:8000/docs to see the Swagger API documentation.

Test the API:

```bash
# Get auth token
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Check provider status (use token from above)
curl http://localhost:8000/api/v1/providers/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Frontend Setup

### Step 1: Install Dependencies

```bash
cd SME-toolkit
npm install
```

### Step 2: Configure Environment

Create `.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Step 3: Run Development Server

```bash
npm run dev
```

The frontend will be available at http://localhost:5173

### Step 4: Build for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

---

## API Keys Configuration

### Google Gemini (Recommended)

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key to your `.env` file

**Provides:**
- LLM (Gemini Flash, Gemini Pro)
- Image Generation (Gemini Image, Imagen 4)
- Video Generation (Veo 3)

### Groq (Free Alternative)

1. Create account at [Groq Console](https://console.groq.com/)
2. Navigate to API Keys
3. Create new key

**Free tier:** 14,400 requests/day, 300+ tokens/second

### Mistral AI

1. Create account at [Mistral Console](https://console.mistral.ai/)
2. Phone verification required
3. Generate API key

**Free tier:** 1 billion tokens/month

### DeepSeek

1. Create account at [DeepSeek Platform](https://platform.deepseek.com/)
2. Generate API key

**Advantages:** Cost-effective, good reasoning

### Replicate (for FLUX.2 Images)

1. Create account at [Replicate](https://replicate.com/)
2. Go to Account → API tokens
3. Create new token

**Pricing:** Pay-per-use, affordable for images

---

## Provider Configuration

### Provider Priority

Configure which providers are tried first in your `.env`:

```env
LLM_PROVIDER_PRIORITY=gemini,groq,mistral,deepseek
IMAGE_PROVIDER_PRIORITY=gemini,flux,stability
VIDEO_PROVIDER_PRIORITY=veo3,kling,nanobanana
```

### Tier-Based Access

The system automatically selects providers based on subscription tier:

| Tier | LLM Providers | Image Providers | Video Providers |
|------|---------------|-----------------|-----------------|
| Free | Groq → Mistral → DeepSeek | FLUX | None |
| SME | Gemini → Groq → Mistral | Gemini → FLUX | Veo Fast |
| Business | Gemini Pro → Gemini → Groq | Imagen 4 → FLUX | Veo 3 → Kling |
| Enterprise | All providers | All providers | All providers |

### Fallback Behavior

When a provider fails, the system automatically tries the next:

```
Primary Provider → Secondary Provider → Tertiary Provider → Mock Response
```

---

## Testing the Setup

### 1. Test Authentication

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Expected response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### 2. Test Provider Status

```bash
curl http://localhost:8000/api/v1/providers/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected response:
```json
{
  "llm": {
    "gemini": true,
    "gemini_pro": true,
    "groq": false
  },
  "image": {
    "gemini": true
  },
  "video": {
    "veo3": true
  }
}
```

### 3. Test LLM Generation

```bash
curl -X POST http://localhost:8000/api/v1/canvas/enhance \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "A coffee shop"}'
```

### 4. Test Subscription Info

```bash
curl http://localhost:8000/api/v1/subscription/tier \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Troubleshooting

### Backend Won't Start

**Error: `ModuleNotFoundError`**
```bash
# Ensure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

**Error: `No module named 'app'`**
```bash
# Run from sme-toolkit-backend directory
cd sme-toolkit-backend
python -m uvicorn app.main:app --port 8000
```

### Provider Not Working

**Error: `Provider not available`**
1. Check API key is set in `.env`
2. Verify API key is valid (not expired/revoked)
3. Check provider status endpoint

**Error: `Rate limit exceeded`**
1. Check your provider's usage dashboard
2. Wait for rate limit reset (usually daily)
3. Add fallback providers

### Frontend Connection Issues

**Error: `CORS error`**

Ensure the backend CORS settings include your frontend URL. Check `app/main.py`:

```python
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    # Add your frontend URL
]
```

**Error: `Network Error`**

1. Verify backend is running on port 8000
2. Check `VITE_API_BASE_URL` in `.env.local`
3. Try accessing http://localhost:8000/docs directly

### Database Issues

**Error: `Database locked`**

SQLite can only handle one writer at a time. For production, use PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/sme_toolkit
```

**Reset database:**
```bash
rm sme_toolkit.db  # Remove SQLite file
python -m uvicorn app.main:app --port 8000  # Will recreate
```

### Common Fixes

1. **Clear Python cache:**
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} +
   ```

2. **Update dependencies:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Regenerate JWT secret:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

---

## Next Steps

1. **Configure additional providers** - Add API keys for fallback providers
2. **Set up Redis** - For production caching and rate limiting
3. **Configure PostgreSQL** - For production database
4. **Set up monitoring** - Add logging and error tracking
5. **Deploy to production** - Use Docker or cloud services

---

## Support

- **Documentation:** [Backend Docs](sme-toolkit-backend/docs/)
- **API Reference:** http://localhost:8000/docs (when running)
- **Provider Docs:** [Multi-Provider AI](sme-toolkit-backend/docs/MULTI_PROVIDER_AI.md)
