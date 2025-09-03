#!/usr/bin/env python3
"""
Database initialization script for E-commerce API
Run this script to create tables and add initial data
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from alembic.config import Config
from alembic import command
from app.database import engine, Base
from app.models import User, Category, Product
from app.crud import create_user, create_category, create_product
from app.auth import get_password_hash
from sqlalchemy.orm import Session

def init_database():
    """Initialize the database with tables and initial data"""
    try:
        print("🚀 Initializing database...")
        
        # Run Alembic migrations
        print("📊 Running database migrations...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrations completed")
        
        # Create initial data
        print("🌱 Creating initial data...")
        create_initial_data()
        print("✅ Initial data created")
        
        print("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

def create_initial_data():
    """Create initial categories and admin user"""
    db = Session(engine)
    
    try:
        # Create admin user
        admin_user = create_user(
            db=db,
            username="admin",
            email="admin@ecommerce.com",
            password="admin123",
            role="ADMIN"
        )
        print(f"👤 Admin user created: {admin_user.username}")
        
        # Create sample categories
        categories = [
            {"name": "Electronics", "description": "Electronic devices and gadgets"},
            {"name": "Clothing", "description": "Fashion and apparel"},
            {"name": "Books", "description": "Books and literature"},
            {"name": "Home & Garden", "description": "Home improvement and gardening"}
        ]
        
        for cat_data in categories:
            category = create_category(db=db, **cat_data)
            print(f"📁 Category created: {category.name}")
        
        # Create sample products
        products = [
            {
                "name": "Smartphone X",
                "description": "Latest smartphone with advanced features",
                "price": 599.99,
                "stock": 50,
                "category_id": 1
            },
            {
                "name": "T-Shirt Classic",
                "description": "Comfortable cotton t-shirt",
                "price": 19.99,
                "stock": 100,
                "category_id": 2
            }
        ]
        
        for prod_data in products:
            product = create_product(db=db, **prod_data)
            print(f"📦 Product created: {product.name}")
            
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
