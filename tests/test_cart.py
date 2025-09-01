import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import Cart, Product
from tests.conftest import override_get_db

class TestCart:
    """Test cart endpoints"""
    
    def test_add_to_cart_success(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test adding item to cart successfully"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        cart_data = {
            "product_id": test_product.id,
            "quantity": 2
        }
        response = client.post("/cart/add", json=cart_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["product_id"] == test_product.id
        assert data["quantity"] == 2

    def test_add_to_cart_duplicate_product(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test adding duplicate product to cart"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        cart_data = {
            "product_id": test_product.id,
            "quantity": 1
        }
        
        # Add first time
        client.post("/cart/add", json=cart_data, headers=headers)
        
        # Add second time (should update quantity)
        response = client.post("/cart/add", json=cart_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED

    def test_add_to_cart_product_not_found(self, client: TestClient, test_user_token: str, db: Session):
        """Test adding non-existent product to cart"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        cart_data = {
            "product_id": 99999,
            "quantity": 1
        }
        response = client.post("/cart/add", json=cart_data, headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_to_cart_insufficient_stock(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test adding item with insufficient stock"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        cart_data = {
            "product_id": test_product.id,
            "quantity": test_product.stock + 1  # More than available stock
        }
        response = client.post("/cart/add", json=cart_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_cart_items(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test getting cart items"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # First add an item
        cart_data = {"product_id": test_product.id, "quantity": 1}
        client.post("/cart/add", json=cart_data, headers=headers)
        
        # Then get cart items
        response = client.get("/cart/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_update_cart_item_quantity(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test updating cart item quantity"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # First add an item
        cart_data = {"product_id": test_product.id, "quantity": 1}
        client.post("/cart/add", json=cart_data, headers=headers)
        
        # Then update quantity
        update_data = {"quantity": 3}
        response = client.put(f"/cart/{test_product.id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["quantity"] == 3

    def test_update_cart_item_insufficient_stock(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test updating cart item with insufficient stock"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # First add an item
        cart_data = {"product_id": test_product.id, "quantity": 1}
        client.post("/cart/add", json=cart_data, headers=headers)
        
        # Then try to update to more than available stock
        update_data = {"quantity": test_product.stock + 1}
        response = client.put(f"/cart/{test_product.id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_cart_item_not_found(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test updating non-existent cart item"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        update_data = {"quantity": 2}
        response = client.put(f"/cart/{test_product.id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_remove_from_cart(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test removing item from cart"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # First add an item
        cart_data = {"product_id": test_product.id, "quantity": 1}
        client.post("/cart/add", json=cart_data, headers=headers)
        
        # Then remove it
        response = client.delete(f"/cart/{test_product.id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_remove_from_cart_not_found(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test removing non-existent cart item"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.delete(f"/cart/{test_product.id}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_clear_cart(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test clearing entire cart"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # First add an item
        cart_data = {"product_id": test_product.id, "quantity": 1}
        client.post("/cart/add", json=cart_data, headers=headers)
        
        # Then clear cart
        response = client.delete("/cart/", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_cart_unauthorized(self, client: TestClient):
        """Test cart access without authentication"""
        response = client.get("/cart/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
