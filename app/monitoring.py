import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import psutil
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect and store application metrics"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        self.start_time = datetime.now()
        self.endpoints_hit = {}
        self.status_codes = {}
    
    def record_request(self, endpoint: str, status_code: int, response_time: float):
        """Record a request metric"""
        self.request_count += 1
        self.response_times.append(response_time)
        
        # Track endpoint usage
        if endpoint not in self.endpoints_hit:
            self.endpoints_hit[endpoint] = 0
        self.endpoints_hit[endpoint] += 1
        
        # Track status codes
        if status_code not in self.status_codes:
            self.status_codes[status_code] = 0
        self.status_codes[status_code] += 1
        
        # Keep only last 1000 response times for memory management
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def record_error(self):
        """Record an error"""
        self.error_count += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        uptime = datetime.now() - self.start_time
        
        # Calculate response time statistics
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            min_response_time = min(self.response_times)
            max_response_time = max(self.response_times)
        else:
            avg_response_time = min_response_time = max_response_time = 0
        
        # Get system metrics
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            cpu_percent = memory = disk = None
        
        return {
            "application": {
                "uptime_seconds": uptime.total_seconds(),
                "uptime_formatted": str(uptime).split('.')[0],
                "total_requests": self.request_count,
                "error_count": self.error_count,
                "error_rate": (self.error_count / self.request_count * 100) if self.request_count > 0 else 0,
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "min_response_time_ms": round(min_response_time * 1000, 2),
                "max_response_time_ms": round(max_response_time * 1000, 2),
                "start_time": self.start_time.isoformat(),
                "endpoints_hit": self.endpoints_hit,
                "status_codes": self.status_codes
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent if memory else None,
                "memory_used_gb": round(memory.used / (1024**3), 2) if memory else None,
                "memory_total_gb": round(memory.total / (1024**3), 2) if memory else None,
                "disk_percent": disk.percent if disk else None,
                "disk_free_gb": round(disk.free / (1024**3), 2) if disk else None,
                "disk_total_gb": round(disk.total / (1024**3), 2) if disk else None
            }
        }

# Global metrics collector
metrics_collector = MetricsCollector()

def log_request_middleware(request: Request, call_next):
    """Middleware to log requests and collect metrics"""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path} from {request.client.host}")
    
    try:
        response = await call_next(request)
        response_time = time.time() - start_time
        
        # Record metrics
        metrics_collector.record_request(
            endpoint=request.url.path,
            status_code=response.status_code,
            response_time=response_time
        )
        
        # Log response
        logger.info(f"Response: {request.method} {request.url.path} -> {response.status_code} ({response_time:.3f}s)")
        
        # Add response time header
        response.headers["X-Response-Time"] = str(response_time)
        
        return response
        
    except Exception as e:
        response_time = time.time() - start_time
        metrics_collector.record_error()
        logger.error(f"Error processing {request.method} {request.url.path}: {e}")
        
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
            headers={"X-Response-Time": str(response_time)}
        )

def get_health_status() -> Dict[str, Any]:
    """Get detailed health status"""
    try:
        # Check system resources
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Define health thresholds
        memory_threshold = 90  # 90% memory usage
        disk_threshold = 90    # 90% disk usage
        
        memory_healthy = memory.percent < memory_threshold
        disk_healthy = disk.percent < disk_threshold
        
        overall_healthy = memory_healthy and disk_healthy
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "memory": {
                    "status": "healthy" if memory_healthy else "unhealthy",
                    "usage_percent": memory.percent,
                    "threshold": memory_threshold
                },
                "disk": {
                    "status": "healthy" if disk_healthy else "unhealthy",
                    "usage_percent": disk.percent,
                    "threshold": disk_threshold
                },
                "application": {
                    "status": "healthy",
                    "uptime_seconds": (datetime.now() - metrics_collector.start_time).total_seconds()
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error checking health status: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

def log_slow_queries(query_time: float, query: str, params: Optional[Dict] = None):
    """Log slow database queries"""
    if query_time > 1.0:  # Log queries taking more than 1 second
        logger.warning(f"Slow query detected: {query_time:.3f}s - {query}")
        if params:
            logger.warning(f"Query parameters: {params}")

def log_performance_metrics(operation: str, duration: float, details: Optional[Dict] = None):
    """Log performance metrics for operations"""
    if duration > 0.5:  # Log operations taking more than 500ms
        logger.info(f"Performance: {operation} took {duration:.3f}s")
        if details:
            logger.info(f"Details: {details}")

# Export the metrics collector for use in other modules
__all__ = ['metrics_collector', 'log_request_middleware', 'get_health_status', 'log_slow_queries', 'log_performance_metrics']
