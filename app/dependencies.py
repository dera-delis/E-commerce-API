from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import auth, models
from .database import get_db


def get_current_user_dependency():
    """Dependency to get current authenticated user"""
    return auth.get_current_user


def get_current_admin_user_dependency():
    """Dependency to get current admin user"""
    return auth.get_current_admin_user


def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID - used for order ownership verification"""
    from . import crud
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def verify_order_ownership(
    order_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Verify that the current user owns the order or is admin"""
    from . import crud
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if current_user.role != models.UserRole.ADMIN and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this order"
        )
    
    return order


def verify_product_exists(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Verify that a product exists"""
    from . import crud
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


def verify_category_exists(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Verify that a category exists"""
    from . import crud
    category = crud.get_category(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category
