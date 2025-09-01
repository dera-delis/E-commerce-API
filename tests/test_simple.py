import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect
from app.main import app
from app.database import get_db
from tests.conftest import override_get_db


def test_basic_setup():
    """Test basic application setup"""
    assert app is not None
    assert app.title == "E-commerce API"


def test_database_creation():
    """Test database creation"""
    from app.database import engine
    inspector = inspect(engine)
    assert inspector is not None


def test_app_creation():
    """Test FastAPI app creation"""
    assert hasattr(app, 'routes')
    assert len(app.routes) > 0


def test_health_endpoint(client: TestClient):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
