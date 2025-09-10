import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User
from tests.conftest import override_get_db

class TestAuth:
    """Test authentication endpoints"""
    
    def test_signup_success(self, client: TestClient, db: Session):
        """Test successful user signup"""
        response = client.post("/api/v1/auth/signup", json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        })
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "hashed_password" not in data

    def test_signup_duplicate_username(self, client: TestClient, db: Session):
        """Test signup with duplicate username"""
        # First signup
        client.post("/api/v1/auth/signup", json={
            "username": "duplicate",
            "email": "first@example.com",
            "password": "password123"
        })
        
        # Second signup with same username
        response = client.post("/api/v1/auth/signup", json={
            "username": "duplicate",
            "email": "second@example.com",
            "password": "password123"
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_signup_duplicate_email(self, client: TestClient, db: Session):
        """Test signup with duplicate email"""
        # First signup
        client.post("/api/v1/auth/signup", json={
            "username": "first",
            "email": "duplicate@example.com",
            "password": "password123"
        })
        
        # Second signup with same email
        response = client.post("/api/v1/auth/signup", json={
            "username": "second",
            "email": "duplicate@example.com",
            "password": "password123"
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success(self, client: TestClient, db: Session):
        """Test successful login"""
        # First create a user
        client.post("/api/v1/auth/signup", json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "password123"
        })
        
        # Then login
        response = client.post("/api/v1/auth/login", data={
            "username": "loginuser",
            "password": "password123"
        })
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_username(self, client: TestClient, db: Session):
        """Test login with invalid username"""
        response = client.post("/api/v1/auth/login", data={
            "username": "nonexistent",
            "password": "password123"
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_invalid_password(self, client: TestClient, db: Session):
        """Test login with invalid password"""
        # First create a user
        client.post("/api/v1/auth/signup", json={
            "username": "passworduser",
            "email": "password@example.com",
            "password": "password123"
        })
        
        # Then login with wrong password
        response = client.post("/api/v1/auth/login", data={
            "username": "passworduser",
            "password": "wrongpassword"
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_success(self, client: TestClient, test_user_token: str):
        """Test getting current user with valid token"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_no_token(self, client: TestClient):
        """Test getting current user without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN
