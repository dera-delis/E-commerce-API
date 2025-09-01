from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, auth
from ..database import get_db

router = APIRouter()


@router.get("/", response_model=List[schemas.Category])
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all categories (public endpoint)"""
    return crud.get_categories(db, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=schemas.Category)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category by ID (public endpoint)"""
    category = crud.get_category(db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.post("/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_admin_user)
):
    """Create a new category (admin only)"""
    # Check if category name already exists
    existing_category = crud.get_categories(db)
    for existing in existing_category:
        if existing.name.lower() == category.name.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists"
            )
    
    return crud.create_category(db=db, category=category)


@router.put("/{category_id}", response_model=schemas.Category)
def update_category(
    category_id: int,
    category_update: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_admin_user)
):
    """Update a category (admin only)"""
    updated_category = crud.update_category(db, category_id=category_id, category_update=category_update)
    if not updated_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return updated_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_admin_user)
):
    """Delete a category (admin only)"""
    # Check if category has products
    products = crud.get_products(db, category_id=category_id)
    if products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with existing products"
        )
    
    success = crud.delete_category(db, category_id=category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
