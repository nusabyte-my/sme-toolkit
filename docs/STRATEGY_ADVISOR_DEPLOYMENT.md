# Strategy Advisor System Deployment Guide

## Overview

This guide covers deploying the Multi-Agent Strategy Advisor System to production environments.

## Pre-Deployment Checklist

### 1. Code Quality

- [ ] All tests passing
- [ ] Code coverage > 80%
- [ ] No critical bugs
- [ ] Documentation complete
- [ ] Security review complete

### 2. Configuration

- [ ] Environment variables configured
- [ ] Database credentials set
- [ ] API keys configured
- [ ] CORS settings configured
- [ ] Rate limiting configured

### 3. Infrastructure

- [ ] Server resources allocated
- [ ] Database server ready
- [ ] Cache server ready
- [ ] Load balancer configured
- [ ] SSL certificates obtained
- [ ] Domain configured
- [ ] CDN configured (optional)

### 4. Monitoring

- [ ] Logging configured
- [ ] Metrics collection enabled
- [ ] Alerting configured
- [ ] Health check endpoints ready
- [ ] Error tracking setup

## Deployment Options

### Option 1: Docker Deployment (Recommended)

#### Backend Deployment

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -s /sbin/nologin appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  backend:
    build: ./sme-toolkit-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:${DB_PASSWORD}@db:5432/sme_toolkit
      - REDIS_URL=redis://redis:6379/0
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: .
    ports:
      - "80:80"
    environment:
      - VITE_API_BASE_URL=http://backend:8000/api/v1
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=sme_toolkit
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

**Deploy with Docker:**

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Option 2: Cloud Deployment

#### AWS Deployment

**EC2 Setup:**

```bash
# Launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-01234567890abcdef0 \
  --user-data file://user-data.sh

# SSH into instance
ssh -i your-key-pair.pem ec2-user@<instance-ip>

# Clone repository
git clone https://github.com/your-org/sme-toolkit.git
cd sme-toolkit

# Install dependencies
cd sme-toolkit-backend
pip install -r requirements.txt

cd ..
npm install

# Configure environment
cp .env.production .env
# Edit .env with production values

# Start services
# Backend
cd sme-toolkit-backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Frontend
cd ..
npm run build
# Serve with nginx or similar
```

**RDS Setup:**

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier sme-toolkit-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password your-password \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-01234567890abcdef0

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://admin:your-password@sme-toolkit-db.xxxx.us-east-1.rds.amazonaws.com:5432/sme_toolkit
```

**ElastiCache Setup:**

```bash
# Create ElastiCache Redis cluster
aws elasticache create-replication-group \
  --replication-group-id sme-toolkit-cache \
  --cache-node-type cache.m3.medium \
  --engine redis \
  --num-cache-nodes 1 \
  --security-group-ids sg-01234567890abcdef0

# Update REDIS_URL in .env
REDIS_URL=redis://sme-toolkit-cache.xxxx.cache.amazonaws.com:6379/0
```

#### Google Cloud Deployment

**Compute Engine Setup:**

```bash
# Create VM instance
gcloud compute instances create sme-toolkit-backend \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB

# SSH into instance
gcloud compute ssh sme-toolkit-backend --zone=us-central1-a

# Clone and setup
git clone https://github.com/your-org/sme-toolkit.git
cd sme-toolkit

# Install dependencies
cd sme-toolkit-backend
pip install -r requirements.txt

cd ..
npm install

# Configure environment
cp .env.production .env
# Edit with production values

# Start services
# Backend
cd sme-toolkit-backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Frontend
cd ..
npm run build
# Serve with nginx
```

**Cloud SQL Setup:**

```bash
# Create Cloud SQL instance
gcloud sql instances create sme-toolkit-db \
  --tier=db-n1-standard-1 \
  --cpu=2 \
  --memory=8GB \
  --database-version=POSTGRES_13 \
  --region=us-central1

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@/cloudsql/instance-connection-name/database
```

#### Azure Deployment

**Virtual Machine Setup:**

```bash
# Create VM
az vm create \
  --resource-group sme-toolkit-rg \
  --name sme-toolkit-backend \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username azureuser \
  --generate-ssh-keys

# SSH into instance
ssh azureuser@<vm-ip>

# Clone and setup
git clone https://github.com/your-org/sme-toolkit.git
cd sme-toolkit

# Install dependencies
cd sme-toolkit-backend
pip install -r requirements.txt

cd ..
npm install

# Configure environment
cp .env.production .env
# Edit with production values

# Start services
# Backend
cd sme-toolkit-backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Frontend
cd ..
npm run build
# Serve with nginx
```

**Database Setup:**

```bash
# Create PostgreSQL server
az postgres server create \
  --resource-group sme-toolkit-rg \
  --name sme-toolkit-db \
  --sku B_Gen5_2 \
  --storage-size 20GB \
  --admin-user admin

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://admin:password@sme-toolkit-db.postgres.database.azure.com:5432/sme_toolkit
```

### Option 3: Kubernetes Deployment

**Deployment Manifest:**

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sme-toolkit-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sme-toolkit-backend
  template:
    metadata:
      labels:
        app: sme-toolkit-backend
    spec:
      containers:
      - name: backend
        image: your-registry/sme-toolkit-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: redis-config
              key: url
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-credentials
              key: api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: sme-toolkit-backend-service
spec:
  selector:
    app: sme-toolkit-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: LoadBalancer
---
# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sme-toolkit-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: sme-toolkit-frontend
  template:
    metadata:
      labels:
        app: sme-toolkit-frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/sme-toolkit-frontend:latest
        ports:
        - containerPort: 80
        env:
        - name: VITE_API_BASE_URL
          value: "http://sme-toolkit-backend-service/api/v1"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: sme-toolkit-frontend-service
spec:
  selector:
    app: sme-toolkit-frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: LoadBalancer
```

**Deploy to Kubernetes:**

```bash
# Apply configurations
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# Check deployment status
kubectl get deployments
kubectl get pods

# View logs
kubectl logs -f deployment/sme-toolkit-backend
kubectl logs -f deployment/sme-toolkit-frontend

# Scale deployment
kubectl scale deployment sme-toolkit-backend --replicas=5
```

## Post-Deployment Steps

### 1. Health Checks

```bash
# Backend health
curl https://your-domain.com/health

# Frontend health
curl https://your-domain.com/

# Database health
curl https://your-domain.com/health/db

# Cache health
curl https://your-domain.com/health/cache
```

### 2. Database Migrations

```bash
# Run migrations
cd sme-toolkit-backend
alembic upgrade head

# Verify migrations
alembic current
```

### 3. Cache Warm-up

```bash
# Warm up cache with common queries
curl -X POST https://your-domain.com/api/v1/scoring/current \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"business_profile_id": "sample-profile"}'
```

### 4. Monitor Initial Traffic

```bash
# Check logs
tail -f sme_toolkit.log

# Monitor metrics
# Use your monitoring dashboard
# Check error rates
# Check response times
```

## Scaling

### Horizontal Scaling

**Auto-scaling Configuration:**

```yaml
# Kubernetes Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: sme-toolkit-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: sme-toolkit-backend
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
```

### Vertical Scaling

**Resource Limits:**

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "1000m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

## Monitoring

### Application Monitoring

**Prometheus Metrics:**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'sme-toolkit'
    static_configs:
      - targets: ['sme-toolkit-backend:8000']
    metrics_path: '/metrics'
```

**Grafana Dashboards:**

- API Response Times
- Database Query Performance
- Cache Hit Rates
- Agent Execution Times
- Error Rates
- User Engagement

### Log Aggregation

**ELK Stack:**

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/sme_toolkit/*.log
  fields:
    app: sme-toolkit
    env: production

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

## Security

### SSL/TLS Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall Rules

```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8000/tcp # Backend API (internal)
ufw deny incoming
```

### Rate Limiting

```python
# In FastAPI middleware
from slowapi import FastAPI
from slowapi.middleware import Middleware
from slowapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add rate limiting middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Backup Strategy

### Database Backups

```bash
# Automated daily backups
0 2 * * * pg_dump -U user -h dbhost -d sme_toolkit > /backups/sme_toolkit_$(date +\%Y\%m\%d).sql

# Retain backups for 30 days
find /backups -name "sme_toolkit_*.sql" -mtime +30 -delete
```

### Application Backups

```bash
# Backup configuration files
tar -czf /backups/config_$(date +\%Y\%m\%d).tar.gz .env

# Backup uploaded files
tar -czf /backups/uploads_$(date +\%Y\%m\%d).tar.gz uploads/
```

## Rollback Procedure

### 1. Database Rollback

```bash
# Stop application
docker-compose down

# Restore database
psql -U user -h dbhost -d sme_toolkit < /backups/sme_toolkit_2024-01-01.sql

# Restart application
docker-compose up -d
```

### 2. Application Rollback

```bash
# Revert to previous version
git checkout <previous-commit-tag>

# Rebuild and deploy
docker-compose up -d --build
```

## Maintenance

### Scheduled Maintenance

```bash
# Enable maintenance mode
curl -X POST https://your-domain.com/api/v1/maintenance/enable \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Perform maintenance tasks
# - Database optimization
# - Cache clearing
# - Log rotation

# Disable maintenance mode
curl -X POST https://your-domain.com/api/v1/maintenance/disable \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Zero-Downtime Deployment

```bash
# Blue-green deployment
# Deploy new version to green environment
kubectl apply -f deployment-green.yaml

# Wait for health checks
kubectl wait --for=condition=ready pod -l app=sme-toolkit-green

# Switch traffic to green
kubectl patch service sme-toolkit-service -p '{"spec":{"selector":{"app":"sme-toolkit-green"}}'

# Monitor for issues
# If issues, switch back to blue
kubectl patch service sme-toolkit-service -p '{"spec":{"selector":{"app":"sme-toolkit-blue"}}'
```

## Performance Tuning

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_business_profile_id ON company_goals(business_profile_id);
CREATE INDEX idx_score_type_date ON score_records(score_type, calculated_at);

-- Analyze query performance
EXPLAIN ANALYZE company_goals;
```

### Cache Optimization

```python
# Adjust TTL based on usage
CACHE_TTL = {
    'scores': 300,      # 5 minutes
    'profiles': 600,    # 10 minutes
    'analysis': 900,    # 15 minutes
    'goals': 120        # 2 minutes
}
```

## Troubleshooting

See [STRATEGY_ADVISOR_TROUBLESHOOTING.md](STRATEGY_ADVISOR_TROUBLESHOOTING.md) for common issues and solutions.

## Support

For deployment issues:
- Email: ops@sme-toolkit.com
- Documentation: https://docs.sme-toolkit.com
- Status Page: https://status.sme-toolkit.com
