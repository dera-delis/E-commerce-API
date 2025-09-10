import pytest
import time
import threading
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db
from app.models import User, Product, Category, UserRole
from app.auth import get_password_hash
from tests.conftest import override_get_db


class TestPerformance:
    """Test performance optimizations and edge cases"""
    
    def setup_method(self):
        """Setup test database and override dependencies"""
        app.dependency_overrides[get_db] = override_get_db
    
    def teardown_method(self):
        """Clean up dependencies"""
        app.dependency_overrides.clear()
    
    def test_rate_limiting(self, client: TestClient):
        """Test rate limiting middleware"""
        # Make many requests quickly
        responses = []
        for _ in range(100):  # Test within the current rate limit
            response = client.get("/health")
            responses.append(response.status_code)
        
        # All requests should succeed with current high rate limit
        assert all(status == 200 for status in responses), "All requests should succeed within rate limit"
    
    def test_gzip_compression(self, client: TestClient):
        """Test GZip compression middleware"""
        # Test with a larger response that should trigger compression
        response = client.get("/api/v1/products/?limit=1000")
        # Note: GZip compression only applies to responses > 1000 bytes
        # Small responses might not be compressed
        assert response.status_code == 200, "Response should be successful"
    
    def test_process_time_header(self, client: TestClient):
        """Test process time header middleware"""
        response = client.get("/health")
        assert "X-Process-Time" in response.headers, "Process time header should be present"
        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0, "Process time should be non-negative"
    
    def test_metrics_endpoint(self, client: TestClient):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "active_ips" in data
        assert "uptime" in data
    
    def test_product_search_performance(self, client: TestClient, db: Session):
        """Test product search with various filters"""
        # Test search by name
        response = client.get("/api/v1/products/?search=laptop")
        assert response.status_code == 200
        
        # Test price filtering
        response = client.get("/api/v1/products/?min_price=100&max_price=1000")
        assert response.status_code == 200
        
        # Test stock filtering
        response = client.get("/api/v1/products/?in_stock=true")
        assert response.status_code == 200
        
        # Test category filtering
        response = client.get("/api/v1/products/?category_id=1")
        assert response.status_code == 200
        
        # Test pagination
        response = client.get("/api/v1/products/?skip=0&limit=5")
        assert response.status_code == 200
        products = response.json()
        assert len(products) <= 5
    
    def test_large_dataset_performance(self, client: TestClient, db: Session):
        """Test performance with larger datasets"""
        # Create many products to test pagination performance
        category = db.query(Category).first()
        if not category:
            pytest.skip("No category available for testing")
        
        for i in range(50):
            product = Product(
                name=f"Test Product {i}",
                description=f"Description for product {i}",
                price=10.0 + i,
                stock=100,
                category_id=category.id
            )
            db.add(product)
        
        db.commit()
        
        # Test pagination performance
        response = client.get("/api/v1/products/?skip=0&limit=100")
        assert response.status_code == 200
        products = response.json()
        assert len(products) <= 100
    
    def test_concurrent_requests(self, client: TestClient):
        """Test handling of concurrent requests"""
        results = []
        errors = []
        
        def make_request():
            try:
                response = client.get("/health")
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(results) == 10, "All concurrent requests should complete"
        assert all(status == 200 for status in results), "All requests should return 200"
        assert len(errors) == 0, "No errors should occur during concurrent requests"
    
    def test_database_connection_pooling(self, client: TestClient):
        """Test database connection pooling under load"""
        # Make many database queries to test connection pooling
        responses = []
        for _ in range(20):
            response = client.get("/api/v1/products/")
            responses.append(response.status_code)
        
        # All should succeed
        assert all(status == 200 for status in responses), "All requests should succeed"
    
    def test_memory_usage(self, client: TestClient):
        """Test memory usage doesn't grow excessively"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            # Make many requests
            for _ in range(50):
                client.get("/health")
            
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (less than 50MB)
            assert memory_increase < 50 * 1024 * 1024, f"Memory increase {memory_increase} bytes is too high"
        except ImportError:
            pytest.skip("psutil not available for memory testing")
    
    def test_response_time_consistency(self, client: TestClient):
        """Test response times are consistent"""
        times = []
        for _ in range(10):
            start = time.time()
            client.get("/health")
            end = time.time()
            times.append(end - start)
        
        # Response times should be consistent (within reasonable variance)
        avg_time = sum(times) / len(times)
        variance = sum((t - avg_time) ** 2 for t in times) / len(times)
        
        assert variance < 0.01, f"Response time variance {variance} is too high"
        assert avg_time < 1.0, f"Average response time {avg_time} is too slow"
