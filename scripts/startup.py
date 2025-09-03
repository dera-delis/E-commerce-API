#!/usr/bin/env python3
"""
Startup script for E-commerce API
This script runs during app startup to ensure database is ready
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

def run_startup_checks():
    """Run startup checks and database initialization"""
    try:
        print("🚀 Running startup checks...")
        
        # Check if we're in production (Render)
        if os.getenv('RENDER'):
            print("🌐 Running in Render environment")
            
            # Import and run migrations
            try:
                from alembic.config import Config
                from alembic import command
                
                print("📊 Running database migrations...")
                alembic_cfg = Config("alembic.ini")
                command.upgrade(alembic_cfg, "head")
                print("✅ Database migrations completed")
                
            except Exception as e:
                print(f"⚠️ Migration warning: {e}")
                print("🔄 Continuing startup...")
        
        print("✅ Startup checks completed")
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        # Don't crash the app, just log the error

if __name__ == "__main__":
    run_startup_checks()
