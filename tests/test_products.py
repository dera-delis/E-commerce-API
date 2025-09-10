import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import Product, Category
from tests.conftest import override_get_db

class TestProducts:
    """Test product endpoints"""
    
    def test_get_products_public(self, client: TestClient, db: Session):
        """Test public access to products list"""
        response = client.get("/api/v1/products/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_get_product_by_id_public(self, client: TestClient, db: Session, test_product: Product):
        """Test public access to individual product"""
        response = client.get(f"/products/{test_product.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == test_product.name
        assert data["price"] == test_product.price

    def test_get_product_not_found(self, client: TestClient, db: Session):
        """Test getting non-existent product"""
        response = client.get("/products/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_product_admin_success(self, client: TestClient, test_admin_token: str, test_category: Category):
        """Test admin creating product successfully"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        product_data = {
            "name": "New Product",
            "description": "A new product",
            "price": 199.99,
            "stock": 50,
            "category_id": test_category.id
        }
        response = client.post("/api/v1/products/", json=product_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == product_data["name"]
        assert data["price"] == product_data["price"]

    def test_create_product_customer_forbidden(self, client: TestClient, test_user_token: str, test_category: Category):
        """Test customer cannot create product"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        product_data = {
            "name": "Customer Product",
            "description": "A product by customer",
            "price": 99.99,
            "stock": 10,
            "category_id": test_category.id
        }
        response = client.post("/api/v1/products/", json=product_data, headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_product_no_auth(self, client: TestClient, test_category: Category):
        """Test creating product without authentication"""
        product_data = {
            "name": "Unauthorized Product",
            "description": "A product without auth",
            "price": 149.99,
            "stock": 25,
            "category_id": test_category.id
        }
        response = client.post("/api/v1/products/", json=product_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_product_invalid_category(self, client: TestClient, test_admin_token: str):
        """Test creating product with invalid category"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        product_data = {
            "name": "Invalid Category Product",
            "description": "A product with invalid category",
            "price": 299.99,
            "stock": 15,
            "category_id": 99999  # Non-existent category
        }
        response = client.post("/api/v1/products/", json=product_data, headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_product_duplicate_name(self, client: TestClient, test_admin_token: str, test_product: Product, test_category: Category):
        """Test creating product with duplicate name"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        product_data = {
            "name": test_product.name,  # Same name as existing product
            "description": "A duplicate product",
            "price": 399.99,
            "stock": 20,
            "category_id": test_category.id
        }
        response = client.post("/api/v1/products/", json=product_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_product_admin_success(self, client: TestClient, test_admin_token: str, test_product: Product):
        """Test admin updating product successfully"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        update_data = {
            "name": "Updated Product",
            "price": 299.99
        }
        response = client.put(f"/products/{test_product.id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["price"] == update_data["price"]

    def test_update_product_customer_forbidden(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test customer cannot update product"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        update_data = {"name": "Customer Update"}
        response = client.put(f"/products/{test_product.id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_product_not_found(self, client: TestClient, test_admin_token: str):
        """Test updating non-existent product"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        update_data = {"name": "Non-existent Update"}
        response = client.put("/products/999", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_product_admin_success(self, client: TestClient, test_admin_token: str, test_product: Product):
        """Test admin deleting product successfully"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        response = client.delete(f"/products/{test_product.id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_product_customer_forbidden(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test customer cannot delete product"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.delete(f"/products/{test_product.id}", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_product_not_found(self, client: TestClient, test_admin_token: str):
        """Test deleting non-existent product"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        response = client.delete("/products/999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_products_by_category(self, client: TestClient, db: Session, test_category: Category):
        """Test getting products by category"""
        response = client.get(f"/products/categories/{test_category.id}/products")
        assert response.status_code == status.HTTP_200_OK
        products = response.json()
        assert isinstance(products, list)
