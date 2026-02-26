"""Prometheus metrics integration."""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Request metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

# Analysis metrics
analysis_count = Counter('analysis_total', 'Total analyses', ['verdict'])
analysis_duration = Histogram('analysis_duration_seconds', 'Analysis duration')
cache_hits = Counter('cache_hits_total', 'Cache hits')
cache_misses = Counter('cache_misses_total', 'Cache misses')

# Model metrics
model_predictions = Counter('model_predictions_total', 'Model predictions', ['version', 'prediction'])
model_confidence = Histogram('model_confidence', 'Model confidence scores', ['version'])

# System metrics
active_users = Gauge('active_users', 'Currently active users')
queue_size = Gauge('celery_queue_size', 'Celery queue size', ['queue'])

def metrics_endpoint():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

class MetricsMiddleware:
    """Middleware to track request metrics."""
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        start = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                duration = time.time() - start
                request_duration.labels(
                    method=scope["method"],
                    endpoint=scope["path"]
                ).observe(duration)
                request_count.labels(
                    method=scope["method"],
                    endpoint=scope["path"],
                    status=message["status"]
                ).inc()
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
