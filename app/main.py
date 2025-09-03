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

@app.on_event("startup")
async def startup_event():
    """Handle startup events"""
    try:
        print("🚀 Running startup initialization...")
        
        # Check environment variables
        import os
        print(f"🌐 Environment check:")
        print(f"   RENDER: {os.getenv('RENDER')}")
        print(f"   DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')[:50]}...")
        print(f"   DEBUG: {os.getenv('DEBUG')}")
        
        # Try to run migrations
        try:
            import subprocess
            import sys
            
            print("📊 Attempting database migrations...")
            result = subprocess.run([
                sys.executable, "-m", "alembic", "upgrade", "head"
            ], capture_output=True, text=True, cwd="/opt/render/project/src")
            
            print(f"Migration stdout: {result.stdout}")
            print(f"Migration stderr: {result.stderr}")
            print(f"Migration return code: {result.returncode}")
            
            if result.returncode == 0:
                print("✅ Database migrations completed during startup")
            else:
                print(f"⚠️ Migration failed with return code {result.returncode}")
                
        except Exception as e:
            print(f"⚠️ Migration startup error: {e}")
            import traceback
            traceback.print_exc()
        
        # Check database connection
        from .database import check_db_connection
        
        if check_db_connection():
            logger.info("✅ Database connection established")
        else:
            logger.warning("⚠️ Database connection failed - app will start but DB operations will fail")
            
        logger.info("🚀 E-commerce API started successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()
        # Don't crash the app, just log the error

# Add middleware for performance and security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Performance middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses > 1KB

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"] if settings.debug else [
        "localhost", 
        "127.0.0.1",
        ".onrender.com",  # Allow Render domains
        ".render.com",    # Allow Render domains
        "ecommerce-api-op5q.onrender.com"  # Your specific domain
    ]
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
app.include_router(auth.router, prefix="/auth")
app.include_router(products.router, prefix="/products")
app.include_router(categories.router, prefix="/categories")
app.include_router(cart.router, prefix="/cart")
app.include_router(orders.router, prefix="/orders")


@app.get("/test")
async def test_endpoint():
    """Simple test endpoint for debugging"""
    return {
        "status": "ok",
        "message": "Test endpoint working",
        "timestamp": time.time()
    }


@app.get("/debug")
async def debug_endpoint(request: Request):
    """Debug endpoint to see request details"""
    return {
        "status": "debug",
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "client_host": request.client.host if request.client else "unknown",
        "timestamp": time.time()
    }


@app.get("/db-check")
async def database_check():
    """Check database connection and tables"""
    try:
        from .database import check_db_connection, engine
        from sqlalchemy import text
        
        # Check connection
        db_connected = check_db_connection()
        
        # Check if tables exist
        tables = []
        if db_connected and engine:
            try:
                with engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                    """))
                    tables = [row[0] for row in result]
            except Exception as e:
                tables = f"Error getting tables: {e}"
        
        return {
            "status": "database_check",
            "database_connected": db_connected,
            "tables": tables,
            "timestamp": time.time()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }


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
    try:
        from .database import check_db_connection
        
        db_status = check_db_connection()
        
        return {
            "status": "healthy" if db_status else "degraded",
            "database": "connected" if db_status else "disconnected",
            "timestamp": time.time(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time(),
            "version": "1.0.0"
        }


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
