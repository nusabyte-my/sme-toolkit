"""
Prometheus metrics configuration for observability
"""

from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import (
    request_size,
    response_size,
    latency,
    requests,
)
import os

ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"

REQUEST_COUNT = Counter(
    "sme_toolkit_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code", "tier"]
)

REQUEST_LATENCY = Histogram(
    "sme_toolkit_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
)

AI_PROVIDER_REQUESTS = Counter(
    "sme_toolkit_ai_provider_requests_total",
    "Total AI provider requests",
    ["provider", "modality", "tier", "status"]
)

AI_PROVIDER_LATENCY = Histogram(
    "sme_toolkit_ai_provider_latency_seconds",
    "AI provider request latency",
    ["provider", "modality"],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 60.0, 120.0, 300.0]
)

AI_PROVIDER_FALLBACKS = Counter(
    "sme_toolkit_ai_provider_fallbacks_total",
    "AI provider fallback events",
    ["from_provider", "to_provider", "modality"]
)

TOKEN_OPERATIONS = Counter(
    "sme_toolkit_token_operations_total",
    "Token operations",
    ["operation_type", "tier"]
)

TOKEN_BALANCE = Gauge(
    "sme_toolkit_token_balance",
    "User token balance",
    ["user_id", "tier"]
)

ACTIVE_USERS = Gauge(
    "sme_toolkit_active_users_total",
    "Active users by tier",
    ["tier"]
)

DATABASE_CONNECTIONS = Gauge(
    "sme_toolkit_db_connections",
    "Database connection pool stats",
    ["pool_status"]
)

DATABASE_QUERY_LATENCY = Histogram(
    "sme_toolkit_db_query_latency_seconds",
    "Database query latency",
    ["query_type"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

CACHE_OPERATIONS = Counter(
    "sme_toolkit_cache_operations_total",
    "Cache operations",
    ["operation", "result"]
)

CACHE_LATENCY = Histogram(
    "sme_toolkit_cache_latency_seconds",
    "Cache operation latency",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1]
)

QUEUE_TASKS = Gauge(
    "sme_toolkit_queue_tasks",
    "Queue task counts",
    ["queue", "status"]
)

QUEUE_LATENCY = Histogram(
    "sme_toolkit_queue_task_latency_seconds",
    "Queue task execution latency",
    ["queue"],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0]
)

CIRCUIT_BREAKER_STATE = Gauge(
    "sme_toolkit_circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=open, 2=half_open)",
    ["name"]
)

LEAD_OPERATIONS = Counter(
    "sme_toolkit_lead_operations_total",
    "Lead operations",
    ["operation", "status"]
)

MARKETPLACE_SYNC = Counter(
    "sme_toolkit_marketplace_sync_total",
    "Marketplace sync operations",
    ["platform", "status"]
)

APP_INFO = Info(
    "sme_toolkit_app",
    "Application information"
)
APP_INFO.info({
    "version": os.getenv("APP_VERSION", "1.0.0"),
    "environment": os.getenv("ENVIRONMENT", "development"),
})


def setup_metrics(app):
    if not ENABLE_METRICS:
        return
    
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=False,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/health", "/metrics", "/favicon.ico"],
        inprogress_name="sme_toolkit_requests_inprogress",
        inprogress_labels=True,
    )
    
    instrumentator.add(
        latency(
            buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
    )
    
    instrumentator.add(
        request_size(
            buckets=[100, 500, 1000, 5000, 10000, 50000, 100000]
        )
    )
    
    instrumentator.add(
        response_size(
            buckets=[100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]
        )
    )
    
    instrumentator.instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


def track_ai_request(provider: str, modality: str, tier: str, status: str):
    AI_PROVIDER_REQUESTS.labels(
        provider=provider,
        modality=modality,
        tier=tier,
        status=status
    ).inc()


def track_ai_latency(provider: str, modality: str, latency_seconds: float):
    AI_PROVIDER_LATENCY.labels(
        provider=provider,
        modality=modality
    ).observe(latency_seconds)


def track_fallback(from_provider: str, to_provider: str, modality: str):
    AI_PROVIDER_FALLBACKS.labels(
        from_provider=from_provider,
        to_provider=to_provider,
        modality=modality
    ).inc()


def track_token_operation(operation_type: str, tier: str):
    TOKEN_OPERATIONS.labels(
        operation_type=operation_type,
        tier=tier
    ).inc()


def track_cache_operation(operation: str, hit: bool):
    CACHE_OPERATIONS.labels(
        operation=operation,
        result="hit" if hit else "miss"
    ).inc()


def track_db_query(query_type: str, latency_seconds: float):
    DATABASE_QUERY_LATENCY.labels(query_type=query_type).observe(latency_seconds)


def update_db_pool_stats(active: int, idle: int, overflow: int):
    DATABASE_CONNECTIONS.labels(pool_status="active").set(active)
    DATABASE_CONNECTIONS.labels(pool_status="idle").set(idle)
    DATABASE_CONNECTIONS.labels(pool_status="overflow").set(overflow)


def update_circuit_breaker_state(name: str, state: int):
    CIRCUIT_BREAKER_STATE.labels(name=name).set(state)


def update_queue_stats(queue: str, pending: int, active: int, failed: int):
    QUEUE_TASKS.labels(queue=queue, status="pending").set(pending)
    QUEUE_TASKS.labels(queue=queue, status="active").set(active)
    QUEUE_TASKS.labels(queue=queue, status="failed").set(failed)


def update_active_users(tier_counts: dict):
    for tier, count in tier_counts.items():
        ACTIVE_USERS.labels(tier=tier).set(count)
