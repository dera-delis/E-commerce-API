import pytest
import threading
import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db
from app.models import User, Product, Category, UserRole, Order, OrderItem, Cart
from app.auth import get_password_hash
from tests.conftest import override_get_db


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def setup_method(self):
        """Setup test database and override dependencies"""
        app.dependency_overrides[get_db] = override_get_db
    
    def teardown_method(self):
        """Clean up dependencies"""
        app.dependency_overrides.clear()
    
    def test_invalid_token_format(self, client: TestClient):
        """Test API behavior with invalid token format"""
        headers = {"Authorization": "Bearer invalid_token_format"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
    
    def test_expired_token(self, client: TestClient):
        """Test API behavior with expired token"""
        # This would require a token that's actually expired
        # For now, just test that invalid tokens are rejected
        headers = {"Authorization": "Bearer expired_token_here"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
    
    def test_malformed_json(self, client: TestClient):
        """Test API behavior with malformed JSON"""
        headers = {"Content-Type": "application/json"}
        response = client.post(
            "/api/v1/auth/signup",
            content="invalid json content",
            headers=headers
        )
        assert response.status_code == 422
    
    def test_very_long_inputs(self, client: TestClient):
        """Test API behavior with very long input strings"""
        long_string = "x" * 10000  # Very long string
        
        response = client.post("/api/v1/auth/signup", json={
            "username": long_string,
            "email": f"{long_string}@example.com",
            "password": "password123"
        })
        
        # Should either accept or reject gracefully, not crash
        assert response.status_code in [201, 422]
    
    def test_special_characters_in_inputs(self, client: TestClient):
        """Test API behavior with special characters"""
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        response = client.post("/api/v1/auth/signup", json={
            "username": f"user{special_chars}",
            "email": f"user{special_chars}@example.com",
            "password": "password123"
        })
        
        # Should handle special characters gracefully
        assert response.status_code in [201, 422]
    
    def test_unicode_inputs(self, client: TestClient):
        """Test API behavior with unicode characters"""
        unicode_string = "café résumé naïve"
        
        response = client.post("/api/v1/auth/signup", json={
            "username": f"user{unicode_string}",
            "email": f"user{unicode_string}@example.com",
            "password": "password123"
        })
        
        # Should handle unicode gracefully
        assert response.status_code in [201, 422]
    
    def test_negative_values(self, client: TestClient, test_admin_token: str, test_category: Category):
        """Test API behavior with negative values"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        
        # Test negative price
        response = client.post("/api/v1/products/", json={
            "name": "Test Product",
            "description": "Test Description",
            "price": -10.0,
            "stock": 100,
            "category_id": test_category.id
        }, headers=headers)
        
        # Should reject negative price
        assert response.status_code == 422
    
    def test_zero_values(self, client: TestClient, test_admin_token: str, test_category: Category):
        """Test API behavior with zero values"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        
        # Test zero price
        response = client.post("/api/v1/products/", json={
            "name": "Test Product",
            "description": "Test Description",
            "price": 0.0,
            "stock": 100,
            "category_id": test_category.id
        }, headers=headers)
        
        # Should accept zero price
        assert response.status_code == 201
    
    def test_extremely_large_numbers(self, client: TestClient, test_admin_token: str, test_category: Category):
        """Test API behavior with extremely large numbers"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        
        # Test very large price
        response = client.post("/api/v1/products/", json={
            "name": "Test Product",
            "description": "Test Description",
            "price": 1e20,  # Very large number
            "stock": 100,
            "category_id": test_category.id
        }, headers=headers)
        
        # Should either accept or reject gracefully
        assert response.status_code in [201, 422]
    
    def test_empty_strings(self, client: TestClient, test_admin_token: str, test_category: Category):
        """Test API behavior with empty strings"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        
        # Test empty name
        response = client.post("/api/v1/products/", json={
            "name": "",
            "description": "Test Description",
            "price": 10.0,
            "stock": 100,
            "category_id": test_category.id
        }, headers=headers)
        
        # Should reject empty name
        assert response.status_code == 422
    
    def test_whitespace_only_strings(self, client: TestClient, test_admin_token: str, test_category: Category):
        """Test API behavior with whitespace-only strings"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        
        # Test whitespace-only name
        response = client.post("/api/v1/products/", json={
            "name": "   ",
            "description": "Test Description",
            "price": 10.0,
            "stock": 100,
            "category_id": test_category.id
        }, headers=headers)
        
        # Should reject whitespace-only strings
        assert response.status_code == 422
    
    def test_sql_injection_attempts(self, client: TestClient):
        """Test API behavior with potential SQL injection attempts"""
        sql_injection = "'; DROP TABLE users; --"
        
        response = client.get(f"/api/v1/products/?search={sql_injection}")
        
        # Should handle gracefully, not crash
        assert response.status_code == 200
    
    def test_xss_attempts(self, client: TestClient, test_admin_token: str, test_category: Category):
        """Test API behavior with potential XSS attempts"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        xss_script = "<script>alert('xss')</script>"
        
        response = client.post("/api/v1/products/", json={
            "name": xss_script,
            "description": xss_script,
            "price": 10.0,
            "stock": 100,
            "category_id": test_category.id
        }, headers=headers)
        
        # Should accept the content (sanitization would be handled by frontend)
        assert response.status_code == 201
    
    def test_concurrent_user_creation(self, client: TestClient):
        """Test concurrent user creation with same username"""
        results = []
        
        def create_user():
            try:
                response = client.post("/api/v1/auth/signup", json={
                    "username": "concurrent_user",
                    "email": f"user{time.time()}@example.com",
                    "password": "password123"
                })
                results.append(response.status_code)
            except Exception:
                # Handle any exceptions gracefully
                results.append(500)
        
        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_user)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # At least one should succeed, others might fail due to duplicate username
        assert any(status == 201 for status in results), "At least one user creation should succeed"
    
    def test_database_constraint_violations(self, client: TestClient, test_admin_token: str, test_category: Category):
        """Test API behavior with database constraint violations"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        
        # Test duplicate product name
        product_data = {
            "name": "Duplicate Product",
            "description": "Test Description",
            "price": 10.0,
            "stock": 100,
            "category_id": test_category.id
        }
        
        # Create first product
        client.post("/api/v1/products/", json=product_data, headers=headers)
        
        # Try to create duplicate
        response = client.post("/api/v1/products/", json=product_data, headers=headers)
        
        # Should reject duplicate name
        assert response.status_code == 400
    
    def test_missing_required_fields(self, client: TestClient, test_admin_token: str, test_category: Category):
        """Test API behavior with missing required fields"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        
        # Missing name field
        response = client.post("/api/v1/products/", json={
            "description": "Test Description",
            "price": 10.0,
            "stock": 100,
            "category_id": test_category.id
        }, headers=headers)
        
        # Should reject missing required field
        assert response.status_code == 422
    
    def test_invalid_enum_values(self, client: TestClient, test_admin_token: str):
        """Test API behavior with invalid enum values"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        
        # Try to create user with invalid role
        response = client.post("/api/v1/auth/signup", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "role": "invalid_role"
        })
        
        # Should reject invalid enum value
        assert response.status_code == 422
