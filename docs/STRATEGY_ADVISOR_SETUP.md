# Strategy Advisor System Setup Guide

## Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 20 GB
- OS: Linux, macOS, or Windows 10+

**Recommended Requirements:**
- CPU: 4+ cores
- RAM: 8+ GB
- Storage: 50+ GB SSD
- OS: Linux (Ubuntu 20.04+)

### Software Requirements

**Backend:**
- Python 3.9+
- pip or poetry
- SQLite 3.35+ (development)
- PostgreSQL 13+ (production)

**Frontend:**
- Node.js 18+
- npm or yarn
- Modern web browser (Chrome, Firefox, Safari, Edge)

**External Services:**
- Google Gemini AI API key
- (Optional) Redis server for caching
- (Optional) PostgreSQL database for production

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-org/sme-toolkit.git
cd sme-toolkit
```

### 2. Backend Setup

#### Install Dependencies

```bash
cd sme-toolkit-backend
pip install -r requirements.txt
```

Or using poetry:

```bash
cd sme-toolkit-backend
poetry install
```

#### Environment Configuration

Create a `.env` file in the backend directory:

```bash
cd sme-toolkit-backend
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1

# Database Configuration
DATABASE_URL=sqlite:///./sme_toolkit.db
# For production:
# DATABASE_URL=postgresql://user:password@localhost:5432/sme_toolkit

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-pro

# Cache Configuration
CACHE_TYPE=memory
# For production:
# CACHE_TYPE=redis
# REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=sme_toolkit.log
```

#### Initialize Database

```bash
# For SQLite (development)
python -m app.database

# For PostgreSQL (production)
# Create database first
createdb sme_toolkit
# Then run migrations
alembic upgrade head
```

#### Verify Installation

```bash
# Run health check
python -c "from app.main import app; print('Backend ready')"

# Or start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

#### Install Dependencies

```bash
cd ..
npm install
```

Or using yarn:

```bash
cd ..
yarn install
```

#### Environment Configuration

Create a `.env.local` file in the root directory:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_API_TIMEOUT=30000

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_SCORING=true
VITE_ENABLE_ORCHESTRATION=true

# Development
VITE_DEV_MODE=true
```

#### Verify Installation

```bash
# Start development server
npm run dev

# Or build for production
npm run build
```

### 4. Development Setup

#### Start Backend

```bash
cd sme-toolkit-backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

#### Start Frontend

```bash
npm run dev
```

Frontend will be available at: http://localhost:5173

#### Access Application

Open your browser and navigate to: http://localhost:5173

## Configuration

### Backend Configuration

#### Database Settings

**SQLite (Development):**
```env
DATABASE_URL=sqlite:///./sme_toolkit.db
```

**PostgreSQL (Production):**
```env
DATABASE_URL=postgresql://user:password@host:5432/database
```

#### Cache Settings

**In-Memory (Development):**
```env
CACHE_TYPE=memory
CACHE_TTL=300
```

**Redis (Production):**
```env
CACHE_TYPE=redis
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300
```

#### AI Service Settings

```env
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-1.5-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2048
```

#### Security Settings

```env
SECRET_KEY=your_secret_key_minimum_32_characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Frontend Configuration

#### API Configuration

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_API_TIMEOUT=30000
```

#### Feature Flags

```env
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_SCORING=true
VITE_ENABLE_ORCHESTRATION=true
VITE_ENABLE_GOALS=true
VITE_ENABLE_GROWTH=true
VITE_ENABLE_COSTING=true
VITE_ENABLE_SUGGESTIONS=true
```

## Verification

### Backend Health Check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "database": "connected",
    "cache": "available",
    "ai_service": "connected"
  }
}
```

### Frontend Health Check

Open browser console and check for errors:

```javascript
// Should see:
// ✓ Frontend initialized
// ✓ API connection established
// ✓ Services loaded
```

### API Documentation

Access API documentation at: http://localhost:8000/docs

## Troubleshooting

### Common Issues

#### Backend Won't Start

**Problem:** Backend fails to start

**Solutions:**
1. Check Python version: `python --version` (should be 3.9+)
2. Check dependencies: `pip list`
3. Check port availability: `netstat -an | grep 8000`
4. Check logs: `tail -f sme_toolkit.log`

#### Database Connection Error

**Problem:** Cannot connect to database

**Solutions:**
1. Verify DATABASE_URL in `.env`
2. Check database server is running
3. Verify credentials
4. Check firewall settings

#### AI Service Error

**Problem:** Cannot connect to Gemini AI

**Solutions:**
1. Verify GEMINI_API_KEY in `.env`
2. Check API key is valid
3. Check network connectivity
4. Verify API quota

#### Frontend Build Error

**Problem:** Frontend build fails

**Solutions:**
1. Clear node_modules: `rm -rf node_modules`
2. Reinstall dependencies: `npm install`
3. Check Node version: `node --version` (should be 18+)
4. Check TypeScript errors: `npm run type-check`

#### CORS Error

**Problem:** Frontend cannot connect to backend

**Solutions:**
1. Check CORS settings in backend
2. Verify API_BASE_URL in frontend
3. Check backend is running
4. Disable browser security for testing

## Development Workflow

### 1. Make Changes

Edit code in your preferred IDE

### 2. Test Changes

```bash
# Backend tests
cd sme-toolkit-backend
pytest tests/

# Frontend tests
npm test
```

### 3. Commit Changes

```bash
git add .
git commit -m "Description of changes"
```

### 4. Push Changes

```bash
git push origin main
```

## Production Deployment

See [STRATEGY_ADVISOR_DEPLOYMENT.md](STRATEGY_ADVISOR_DEPLOYMENT.md) for production deployment instructions.

## Additional Resources

- [Architecture Documentation](STRATEGY_ADVISOR_ARCHITECTURE.md)
- [API Documentation](STRATEGY_ADVISOR_API.md)
- [Troubleshooting Guide](STRATEGY_ADVISOR_TROUBLESHOOTING.md)

## Support

For setup issues, contact:
- Email: support@sme-toolkit.com
- Documentation: https://docs.sme-toolkit.com
- Issues: https://github.com/your-org/sme-toolkit/issues
