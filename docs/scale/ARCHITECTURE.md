# SME Toolkit - Scale Architecture Plan

**Generated:** 2026-05-24
**Purpose:** Convert MVP to production-scale system

---

## Executive Summary

This document outlines the comprehensive scaling strategy for SME Toolkit, transforming it from a monolithic MVP to a production-ready, scalable platform.

### Current State vs Scale Target

| Component | MVP Status | Scale Target |
|-----------|------------|--------------|
| Database | SQLite/PostgreSQL single | PostgreSQL cluster with read replicas |
| Backend | FastAPI monolith | Modular services with API gateway |
| Frontend | React SPA | CDN-distributed, code-split |
| AI Providers | In-process routing | External microservice with circuit breakers |
| Caching | None | Redis cluster |
| Queue | None | Celery + Redis |
| Monitoring | Basic logging | Prometheus + Grafana + Loki |
| Deployment | Docker Compose | Kubernetes (K8s) |

---

## 1. Database Layer Scaling

### 1.1 PostgreSQL Migration & Optimization

**File:** `migrations/production/001_postgres_optimization.sql`

Key optimizations:
- Enable pg_trgm for trigram similarity search
- Enable pg_stat_statements for query monitoring
- Enable btree_gin for composite indexes
- Table partitioning for high-volume tables (token_transactions, user_activity_logs)
- Monthly partitions for data archiving

### 1.2 Connection Pooling

**File:** `sme-toolkit-backend/app/database_pool.py`

Configuration:
- pool_size: 20 persistent connections
- max_overflow: 10 additional during peak
- pool_timeout: 30 seconds
- pool_recycle: 3600 seconds (1 hour)
- pool_pre_ping: True for health checks

Read replica routing with round-robin selection.

### 1.3 Critical Indexes

**File:** `migrations/production/002_performance_indexes.sql`

High-priority indexes:
- token_transactions: user_id + created_at DESC
- user_activity_logs: user_id + action + created_at
- leads: business_profile_id + status + score
- Full-text search with GIN trigram indexes

---

## 2. Caching Layer (Redis)

### 2.1 Redis Configuration

**File:** `sme-toolkit-backend/app/cache/redis_client.py`

Features:
- Async Redis client with connection pooling
- Max 50 connections
- Socket keepalive enabled
- Retry on timeout

### 2.2 Caching Strategies by Data Type

| Data Type | TTL | Strategy |
|-----------|-----|----------|
| user_profile | 30 min | write-through |
| user_subscription | 5 min | write-through |
| token_balance | 1 min | cache-aside |
| provider_status | 30 sec | cache-aside |
| business_scores | 1 hour | refresh-ahead |
| analytics_dashboard | 15 min | cache-aside |
| available_models | 2 hours | cache-aside |

---

## 3. Message Queue System

### 3.1 Celery Configuration

**File:** `sme-toolkit-backend/app/queue/celery_app.py`

Queue definitions:
- `default` - General tasks
- `ai_llm` - Text generation
- `ai_image` - Image generation
- `ai_video` - Video generation
- `analytics` - Analytics processing
- `notifications` - Email/push notifications
- `scheduled` - Cron jobs

### 3.2 Scheduled Tasks

| Task | Schedule | Purpose |
|------|----------|---------|
| reset_daily_quotas | Midnight UTC | Reset daily usage limits |
| cleanup_sessions | 3 AM UTC | Remove expired sessions |
| calculate_daily_metrics | 1 AM UTC | Aggregate analytics |
| check_provider_health | Every 5 min | AI provider health check |
| sync_marketplace_data | Every 30 min | Sync Shopee/Lazada data |

---

## 4. API Gateway & Middleware

### 4.1 Advanced Rate Limiting

**File:** `sme-toolkit-backend/app/middleware/rate_limiter.py`

Features:
- Sliding window algorithm via Redis sorted sets
- Tier-based limits (anonymous: 10, free: 60, sme: 300, business: 1000, enterprise: 5000)
- Rate limit headers in responses
- Per-endpoint customization

### 4.2 Circuit Breaker Pattern

**File:** `sme-toolkit-backend/app/middleware/circuit_breaker.py`

Configuration:
- failure_threshold: 5 failures
- recovery_timeout: 60 seconds
- half_open_max_calls: 3 test calls

States: CLOSED -> OPEN -> HALF_OPEN -> CLOSED

---

## 5. Observability Stack

### 5.1 Structured Logging

**File:** `sme-toolkit-backend/app/monitoring/logging_config.py`

Features:
- JSON structured logs
- Request ID tracking
- User context in logs
- Audit logging for compliance
- Error file logging

### 5.2 Prometheus Metrics

**File:** `sme-toolkit-backend/app/monitoring/metrics.py`

Key metrics:
- `sme_toolkit_requests_total` - Request counter
- `sme_toolkit_request_latency_seconds` - Latency histogram
- `sme_toolkit_ai_requests_total` - AI provider requests
- `sme_toolkit_ai_latency_seconds` - AI latency
- `sme_toolkit_token_balance` - User token gauge
- `sme_toolkit_active_users` - Active users gauge
- `sme_toolkit_db_connections` - DB pool stats
- `sme_toolkit_queue_tasks` - Queue task counts

---

## 6. Security Hardening

### 6.1 Secrets Management

**File:** `sme-toolkit-backend/app/security/secrets.py`

Features:
- Centralized secrets with caching
- Rotation callback registration
- Environment variable fallback

### 6.2 API Key Encryption

**File:** `sme-toolkit-backend/app/security/encryption.py`

Features:
- Fernet symmetric encryption
- PBKDF2 key derivation
- Automatic encrypt/decrypt on SQLAlchemy models

---

## 7. Kubernetes Deployment

### 7.1 Namespace & Secrets

**File:** `k8s/namespace.yaml`, `k8s/secrets.yaml`

### 7.2 Backend Deployment

**File:** `k8s/backend-deployment.yaml`

Configuration:
- 3 replicas
- Rolling update strategy (maxSurge: 1, maxUnavailable: 0)
- Resource limits: 2 CPU, 2Gi memory
- Liveness/readiness probes
- Prometheus annotations

### 7.3 Supporting Services

- Redis: 3 replicas, persistent volume
- PostgreSQL: StatefulSet with PVC
- Celery workers: Separate deployments per queue

---

## 8. CI/CD Pipeline

### 8.1 GitHub Actions

**File:** `.github/workflows/deploy.yml`

Stages:
1. Test (unit tests, integration tests)
2. Build (Docker images)
3. Security scan (Trivy, Snyk)
4. Deploy to staging
5. Integration tests on staging
6. Deploy to production (manual approval)

### 8.2 Docker Configuration

**File:** `Dockerfile.prod`

Multi-stage build:
- Builder stage with all dependencies
- Production stage with minimal footprint
- Non-root user execution
- Health check endpoint

---

## Implementation Priority

### Phase 1 (Week 1-2)
- [ ] PostgreSQL connection pooling
- [ ] Redis caching layer
- [ ] Structured logging

### Phase 2 (Week 3-4)
- [ ] Celery queue system
- [ ] Circuit breakers
- [ ] Rate limiting enhancement

### Phase 3 (Week 5-6)
- [ ] Kubernetes manifests
- [ ] CI/CD pipeline
- [ ] Prometheus metrics

### Phase 4 (Week 7-8)
- [ ] Load testing
- [ ] Performance tuning
- [ ] Security hardening

---

## Monitoring Dashboards

### Grafana Dashboards

1. **System Overview**
   - Request rate, latency percentiles
   - Error rate by endpoint
   - Active users by tier

2. **AI Providers**
   - Provider latency comparison
   - Success/failure rates
   - Token consumption

3. **Database**
   - Connection pool status
   - Query latency
   - Replication lag

4. **Queue Health**
   - Tasks pending per queue
   - Worker utilization
   - Failed task rate

---

## Cost Estimation (Monthly)

### Production Infrastructure

| Component | Configuration | Est. Cost |
|-----------|--------------|-----------|
| API Servers | 3x 2vCPU, 4GB | $150 |
| Database | PostgreSQL HA | $200 |
| Redis | 3x cluster | $100 |
| Celery Workers | 5x workers | $100 |
| Load Balancer | Managed | $50 |
| Monitoring | Prometheus/Grafana | $50 |
| **Total** | | **$650/month** |

### Scaling Thresholds

- 1,000 daily users: Base infrastructure
- 5,000 daily users: +2 API servers, read replica
- 10,000+ daily users: Kubernetes autoscaling, CDN

---

## Next Steps

1. Review and approve architecture plan
2. Set up staging environment
3. Implement Phase 1 components
4. Conduct load testing
5. Deploy to production with gradual rollout
