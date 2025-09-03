from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
import logging
from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Database engine with connection pooling and performance optimizations
try:
    engine = create_engine(
        settings.database_url,
        pool_size=20,  # Number of connections to maintain
        max_overflow=30,  # Additional connections when pool is full
        pool_pre_ping=True,  # Validate connections before use
        pool_recycle=3600,  # Recycle connections every hour
        pool_timeout=30,  # Timeout for getting connection from pool
        echo=settings.debug,  # SQL logging in debug mode
        # Add connection retry logic
        connect_args={
            "connect_timeout": 10,
            "application_name": "ecommerce_api"
        }
    )
    
    # Test the connection
    with engine.connect() as conn:
        conn.execute("SELECT 1")
        logger.info("Database connection established successfully")
        
except SQLAlchemyError as e:
    logger.error(f"Database connection failed: {e}")
    # Create a minimal engine for startup (will fail on actual DB operations)
    engine = None
except Exception as e:
    logger.error(f"Unexpected error during database setup: {e}")
    engine = None

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None

Base = declarative_base()


def get_db():
    """Database dependency"""
    if not SessionLocal:
        # Return a mock session that will fail gracefully
        class MockSession:
            def __init__(self):
                pass
            
            def close(self):
                pass
                
            def __enter__(self):
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
        
        # Raise a proper HTTP exception instead of crashing
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503, 
            detail="Database service unavailable. Please try again later."
        )
    
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def check_db_connection():
    """Check if database is accessible"""
    try:
        if engine:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        return False
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
