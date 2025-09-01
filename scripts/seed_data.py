#!/usr/bin/env python3
"""
Database seeding script for the E-commerce API
Creates sample categories, products, and admin user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import SessionLocal, engine
from app.models import Base, User, Category, Product, UserRole

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def seed_database():
    """Seed the database with sample data"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(User).first():
            print("Database already contains data. Skipping seeding.")
            return
        
        print("Seeding database with sample data...")
        
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@ecommerce.com",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Created admin user: {admin_user.username}")
        
        # Create sample categories
        categories_data = [
            {"name": "Electronics", "description": "Electronic devices and accessories"},
            {"name": "Clothing", "description": "Fashion and apparel"},
            {"name": "Books", "description": "Books and publications"},
            {"name": "Home & Garden", "description": "Home improvement and gardening"},
            {"name": "Sports", "description": "Sports equipment and accessories"}
        ]
        
        categories = []
        for cat_data in categories_data:
            category = Category(**cat_data)
            db.add(category)
            db.commit()
            db.refresh(category)
            categories.append(category)
            print(f"Created category: {category.name}")
        
        # Create sample products
        products_data = [
            {
                "name": "Smartphone X",
                "description": "Latest smartphone with advanced features",
                "price": 699.99,
                "stock": 50,
                "category_id": categories[0].id  # Electronics
            },
            {
                "name": "Laptop Pro",
                "description": "High-performance laptop for professionals",
                "price": 1299.99,
                "stock": 25,
                "category_id": categories[0].id  # Electronics
            },
            {
                "name": "Cotton T-Shirt",
                "description": "Comfortable cotton t-shirt",
                "price": 19.99,
                "stock": 100,
                "category_id": categories[1].id  # Clothing
            },
            {
                "name": "Python Programming Book",
                "description": "Comprehensive guide to Python programming",
                "price": 39.99,
                "stock": 75,
                "category_id": categories[2].id  # Books
            },
            {
                "name": "Garden Tool Set",
                "description": "Complete set of essential garden tools",
                "price": 89.99,
                "stock": 30,
                "category_id": categories[3].id  # Home & Garden
            },
            {
                "name": "Yoga Mat",
                "description": "Premium yoga mat for home workouts",
                "price": 29.99,
                "stock": 60,
                "category_id": categories[4].id  # Sports
            }
        ]
        
        for prod_data in products_data:
            product = Product(**prod_data)
            db.add(product)
            db.commit()
            db.refresh(product)
            print(f"Created product: {product.name} - ${product.price}")
        
        print("\nDatabase seeding completed successfully!")
        print(f"Admin credentials: username=admin, password=admin123")
        print(f"Created {len(categories)} categories and {len(products_data)} products")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
