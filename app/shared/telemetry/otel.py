from prometheus_client import Counter, Histogram, Gauge

# 1. HTTP Request Latency Histogram
HTTP_REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP Request Latency in seconds",
    ["method", "path"]
)

# 2. Database Query Latency
DB_QUERY_LATENCY = Histogram(
    "db_query_latency_seconds",
    "Database Query Latency in seconds",
    ["operation"]
)

# 3. Cache Hits and Misses Counter
CACHE_OPERATIONS = Counter(
    "cache_operations_total",
    "Cache operations total counts",
    ["action", "status"]  # e.g., action="get", status="hit"/"miss"
)

# 4. Active WebSockets Gauge
ACTIVE_WEBSOCKETS = Gauge(
    "active_websockets_count",
    "Number of currently active WebSocket channels"
)

# 5. Celery Queue Depth
CELERY_QUEUE_DEPTH = Gauge(
    "celery_queue_depth",
    "Total pending background tasks in Celery queue depth"
)

# 6. Background Task Duration
BACKGROUND_TASK_DURATION = Histogram(
    "background_task_duration_seconds",
    "Background tasks execution durations in seconds",
    ["task_name"]
)

# 7. Authentication Counter
AUTH_EVENTS = Counter(
    "auth_events_total",
    "Authentication events metrics",
    ["action", "status"]  # e.g., action="login", status="success"/"fail"
)

def instrument_app(app) -> None:
    """Instrument the FastAPI app with OpenTelemetry tracers."""
    # Placeholder for future OTEL setup configuration
    pass
