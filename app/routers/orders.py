from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, auth, models
from ..database import get_db

router = APIRouter()


@router.get("/", response_model=List[schemas.Order])
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get orders - customers see their own, admins see all"""
    if current_user.role == models.UserRole.ADMIN:
        return crud.get_all_orders(db, skip=skip, limit=limit)
    else:
        return crud.get_user_orders(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/all", response_model=List[schemas.Order])
def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: schemas.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all orders (admin only)"""
    return crud.get_all_orders(db, skip=skip, limit=limit)


@router.get("/{order_id}", response_model=schemas.Order)
def get_order(
    order_id: int,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific order - customers can only see their own, admins can see all"""
    order = crud.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if user has access to this order
    if current_user.role != models.UserRole.ADMIN and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this order"
        )
    
    return order


@router.put("/{order_id}/status", response_model=schemas.Order)
def update_order_status(
    order_id: int,
    status_update: schemas.OrderUpdate,
    current_user: schemas.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update order status (admin only)"""
    if not status_update.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status is required"
        )
    
    updated_order = crud.update_order_status(db, order_id=order_id, status=status_update.status)
    if not updated_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return updated_order


@router.post("/checkout", response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
def checkout(
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Checkout - create order from cart (customers only)"""
    if current_user.role == models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins cannot checkout"
        )
    
    # Get cart items
    cart_items = crud.get_cart_items(db, user_id=current_user.id)
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    # Calculate total price and verify stock
    total_price = 0
    for cart_item in cart_items:
        product = crud.get_product(db, cart_item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {cart_item.product_id} not found"
            )
        
        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}. Available: {product.stock}"
            )
        
        total_price += product.price * cart_item.quantity
    
    # Create order
    order = crud.create_order(db, user_id=current_user.id, total_price=total_price)
    
    # Create order items and update stock
    for cart_item in cart_items:
        product = crud.get_product(db, cart_item.product_id)
        
        # Create order item
        crud.create_order_item(
            db, 
            order_id=order.id, 
            product_id=cart_item.product_id, 
            quantity=cart_item.quantity, 
            price=product.price
        )
        
        # Update product stock
        product.stock -= cart_item.quantity
        db.commit()
    
    # Clear cart
    crud.clear_cart(db, user_id=current_user.id)
    
    # Refresh order to get order items
    db.refresh(order)
    
    return order
