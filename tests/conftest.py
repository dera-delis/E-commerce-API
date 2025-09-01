import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.models import User, Product, Category, UserRole, Base
from app.auth import get_password_hash
from app.schemas import UserCreate
from app import crud

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def db():
    """Database session fixture"""
    # Create tables for each test
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after each test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Test client fixture"""
    # Override the database dependency to use the same session
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    # No finally block here, as db fixture handles drop_all

@pytest.fixture
def test_user(db):
    """Create a test user"""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    user = crud.create_user(db, user_data)
    return user

@pytest.fixture
def test_admin_user(db):
    """Create a test admin user"""
    user_data = UserCreate(
        username="admin",
        email="admin@example.com",
        password="admin123",
        role=UserRole.ADMIN
    )
    user = crud.create_user(db, user_data)
    return user

@pytest.fixture
def test_category(db):
    """Create a test category"""
    category = Category(
        name="Electronics",
        description="Electronic devices and accessories"
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@pytest.fixture
def test_product(db, test_category):
    """Create a test product"""
    product = Product(
        name="Test Laptop",
        description="A test laptop for testing",
        price=999.99,
        stock=10,
        category_id=test_category.id
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@pytest.fixture
def test_user_token(client, test_user):
    """Get authentication token for test user"""
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    return response.json()["access_token"]

@pytest.fixture
def test_admin_token(client, test_admin_user):
    """Get authentication token for test admin"""
    response = client.post("/auth/login", data={
        "username": "admin",
        "password": "admin123"
    })
    return response.json()["access_token"]

