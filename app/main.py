from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from .routers import auth, categories, products, cart, orders
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A comprehensive E-commerce API with JWT authentication, role-based access control, and PostgreSQL backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.debug
)

# Add middleware for performance and security
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Performance middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses > 1KB

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"]
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests
    if process_time > 1.0:  # Log requests taking more than 1 second
        logger.warning(f"Slow request: {request.method} {request.url.path} took {process_time:.2f}s")
    
    return response

# Rate limiting (simple in-memory implementation) - REDUCED for testing
from collections import defaultdict
import asyncio
from datetime import datetime, timedelta

# Simple rate limiting storage
rate_limit_storage = defaultdict(list)

def is_rate_limited(ip: str, limit: int = 10000, window: int = 60) -> bool:
    """Simple rate limiting: max requests per window seconds - REDUCED for testing"""
    now = datetime.now()
    # Clean old entries
    rate_limit_storage[ip] = [
        timestamp for timestamp in rate_limit_storage[ip] 
        if now - timestamp < timedelta(seconds=window)
    ]
    
    if len(rate_limit_storage[ip]) >= limit:
        return True
    
    rate_limit_storage[ip].append(now)
    return False

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    
    if is_rate_limited(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."}
        )
    
    response = await call_next(request)
    return response

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(cart.router, prefix="/cart", tags=["Cart"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to E-commerce API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint"""
    return {
        "total_requests": len([ts for timestamps in rate_limit_storage.values() for ts in timestamps]),
        "active_ips": len(rate_limit_storage),
        "uptime": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
