import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import Order, OrderItem, Cart, Product
from tests.conftest import override_get_db

class TestOrders:
    """Test order endpoints"""
    
    def test_checkout_success(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test successful checkout"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # First add item to cart
        cart_data = {"product_id": test_product.id, "quantity": 2}
        client.post("/api/v1/cart/add", json=cart_data, headers=headers)
        
        # Then checkout
        response = client.post("/api/v1/orders/checkout", headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["status"] == "pending"
        assert data["total_price"] == test_product.price * 2

    def test_checkout_empty_cart(self, client: TestClient, test_user_token: str, db: Session):
        """Test checkout with empty cart"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.post("/api/v1/orders/checkout", headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_checkout_admin_forbidden(self, client: TestClient, test_admin_token: str, test_product: Product):
        """Test admin cannot checkout (should be customer only)"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        
        # Add item to cart
        cart_data = {"product_id": test_product.id, "quantity": 1}
        client.post("/api/v1/cart/add", json=cart_data, headers=headers)
        
        # Try to checkout
        response = client.post("/api/v1/orders/checkout", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_checkout_insufficient_stock(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test checkout with insufficient stock"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Try to add more than available stock
        cart_data = {"product_id": test_product.id, "quantity": test_product.stock + 1}
        response = client.post("/api/v1/cart/add", json=cart_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Then try to checkout (should fail due to empty cart)
        response = client.post("/api/v1/orders/checkout", headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_checkout_stock_reduction(self, client: TestClient, test_user_token: str, test_product: Product, db: Session):
        """Test that checkout reduces product stock"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        initial_stock = test_product.stock
        
        # Add item to cart
        cart_data = {"product_id": test_product.id, "quantity": 2}
        client.post("/api/v1/cart/add", json=cart_data, headers=headers)
        
        # Checkout
        response = client.post("/api/v1/orders/checkout", headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify stock is reduced
        db.refresh(test_product)
        assert test_product.stock == initial_stock - 2

    def test_checkout_cart_cleared(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test that checkout clears the cart"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Add item to cart
        cart_data = {"product_id": test_product.id, "quantity": 1}
        client.post("/api/v1/cart/add", json=cart_data, headers=headers)
        
        # Verify cart has item
        cart_response = client.get("/api/v1/cart/", headers=headers)
        assert len(cart_response.json()) > 0
        
        # Checkout
        response = client.post("/api/v1/orders/checkout", headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify cart is cleared
        cart_response = client.get("/api/v1/cart/", headers=headers)
        assert len(cart_response.json()) == 0

    def test_get_user_orders(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test customer getting their own orders"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # First create an order
        cart_data = {"product_id": test_product.id, "quantity": 1}
        client.post("/api/v1/cart/add", json=cart_data, headers=headers)
        client.post("/api/v1/orders/checkout", headers=headers)
        
        # Then get orders
        response = client.get("/api/v1/orders/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_all_orders_admin(self, client: TestClient, test_admin_token: str, test_user_token: str, test_product: Product):
        """Test admin getting all orders"""
        # Create an order as user
        user_headers = {"Authorization": f"Bearer {test_user_token}"}
        cart_data = {"product_id": test_product.id, "quantity": 1}
        client.post("/api/v1/cart/add", json=cart_data, headers=user_headers)
        client.post("/api/v1/orders/checkout", headers=user_headers)
        
        # Admin gets all orders
        admin_headers = {"Authorization": f"Bearer {test_admin_token}"}
        response = client.get("/api/v1/orders/all", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_order_by_id_owner(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test customer getting their own order by ID"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Create an order
        cart_data = {"product_id": test_product.id, "quantity": 1}
        client.post("/api/v1/cart/add", json=cart_data, headers=headers)
        checkout_response = client.post("/api/v1/orders/checkout", headers=headers)
        order_id = checkout_response.json()["id"]
        
        # Get order by ID
        response = client.get(f"/orders/{order_id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == order_id

    def test_get_order_by_id_admin(self, client: TestClient, test_admin_token: str, test_user_token: str, test_product: Product):
        """Test admin getting any order by ID"""
        # Create an order as user
        user_headers = {"Authorization": f"Bearer {test_user_token}"}
        cart_data = {"product_id": test_product.id, "quantity": 1}
        client.post("/api/v1/cart/add", json=cart_data, headers=user_headers)
        checkout_response = client.post("/api/v1/orders/checkout", headers=user_headers)
        order_id = checkout_response.json()["id"]
        
        # Admin gets the order
        admin_headers = {"Authorization": f"Bearer {test_admin_token}"}
        response = client.get(f"/orders/{order_id}", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == order_id

    def test_get_order_by_id_unauthorized(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test customer cannot get another user's order"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Create an order
        cart_data = {"product_id": test_product.id, "quantity": 1}
        client.post("/api/v1/cart/add", json=cart_data, headers=headers)
        checkout_response = client.post("/api/v1/orders/checkout", headers=headers)
        order_id = checkout_response.json()["id"]
        
        # Try to get order without token
        response = client.get(f"/orders/{order_id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_order_status_admin(self, client: TestClient, test_admin_token: str, test_user_token: str, test_product: Product):
        """Test admin updating order status"""
        # Create an order as user
        user_headers = {"Authorization": f"Bearer {test_user_token}"}
        cart_data = {"product_id": test_product.id, "quantity": 1}
        client.post("/api/v1/cart/add", json=cart_data, headers=user_headers)
        checkout_response = client.post("/api/v1/orders/checkout", headers=user_headers)
        order_id = checkout_response.json()["id"]
        
        # Admin updates status
        admin_headers = {"Authorization": f"Bearer {test_admin_token}"}
        update_data = {"status": "shipped"}
        response = client.put(f"/orders/{order_id}/status", json=update_data, headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "shipped"

    def test_update_order_status_customer_forbidden(self, client: TestClient, test_user_token: str, test_product: Product):
        """Test customer cannot update order status"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Create an order
        cart_data = {"product_id": test_product.id, "quantity": 1}
        client.post("/api/v1/cart/add", json=cart_data, headers=headers)
        checkout_response = client.post("/api/v1/orders/checkout", headers=headers)
        order_id = checkout_response.json()["id"]
        
        # Try to update status
        update_data = {"status": "shipped"}
        response = client.put(f"/orders/{order_id}/status", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_order_status_not_found(self, client: TestClient, test_admin_token: str):
        """Test updating non-existent order status"""
        headers = {"Authorization": f"Bearer {test_admin_token}"}
        update_data = {"status": "shipped"}
        response = client.put("/api/v1/orders/999/status", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_orders_unauthorized(self, client: TestClient):
        """Test orders access without authentication"""
        response = client.get("/api/v1/orders/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
