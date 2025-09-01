from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, auth
from ..database import get_db

router = APIRouter(tags=["cart"])


@router.get("/", response_model=List[schemas.CartItem])
def get_cart_items(
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's cart items"""
    return crud.get_cart_items(db, user_id=current_user.id)


@router.post("/add", response_model=schemas.CartItem, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    cart_item: schemas.CartItemCreate,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Add product to cart"""
    # Verify product exists
    product = crud.get_product(db, cart_item.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check stock availability
    if product.stock < cart_item.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {product.stock}"
        )
    
    result = crud.add_to_cart(db, user_id=current_user.id, cart_item=cart_item)
    return result


@router.put("/{product_id}", response_model=schemas.CartItem)
def update_cart_item(
    product_id: int,
    cart_update: schemas.CartItemUpdate,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    # Verify product exists
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check stock availability
    if product.stock < cart_update.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {product.stock}"
        )
    
    updated_item = crud.update_cart_item(db, user_id=current_user.id, product_id=product_id, quantity=cart_update.quantity)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    return updated_item


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(
    product_id: int,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Remove product from cart"""
    success = crud.remove_from_cart(db, user_id=current_user.id, product_id=product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all items from cart"""
    crud.clear_cart(db, user_id=current_user.id)
