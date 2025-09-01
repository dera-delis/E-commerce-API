from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from .. import crud, schemas, models
from ..dependencies import get_current_admin_user_dependency, get_current_user_dependency, verify_category_exists
from ..database import get_db

router = APIRouter()


@router.get("/", response_model=List[schemas.Product])
def get_products(
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of products to return"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
    search: Optional[str] = Query(None, description="Search in product name and description"),
    db: Session = Depends(get_db)
):
    """Get products with filtering, search, and pagination"""
    filters = []
    
    if category_id:
        filters.append(models.Product.category_id == category_id)
    
    if min_price is not None:
        filters.append(models.Product.price >= min_price)
    
    if max_price is not None:
        filters.append(models.Product.price <= max_price)
    
    if in_stock is not None:
        if in_stock:
            filters.append(models.Product.stock > 0)
        else:
            filters.append(models.Product.stock == 0)
    
    # Build search query
    if search:
        search_filter = or_(
            models.Product.name.ilike(f"%{search}%"),
            models.Product.description.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    # Apply filters
    query = db.query(models.Product)
    if filters:
        query = query.filter(and_(*filters))
    
    # Apply pagination
    products = query.offset(skip).limit(limit).all()
    
    return products


@router.get("/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.post("/", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin_user_dependency())
):
    """Create a new product (admin only)"""
    # Verify category exists
    verify_category_exists(product.category_id, db)
    
    # Check for duplicate product name
    existing_product = crud.get_product_by_name(db, product.name)
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists"
        )
    
    return crud.create_product(db, product)


@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product_update: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin_user_dependency())
):
    """Update a product (admin only)"""
    existing_product = crud.get_product(db, product_id)
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product_update.category_id:
        verify_category_exists(product_update.category_id, db)
    
    # Check for duplicate name if name is being updated
    if product_update.name and product_update.name != existing_product.name:
        duplicate_product = crud.get_product_by_name(db, product_update.name)
        if duplicate_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this name already exists"
            )
    
    return crud.update_product(db, product_id, product_update)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin_user_dependency())
):
    """Delete a product (admin only)"""
    existing_product = crud.get_product(db, product_id)
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    crud.delete_product(db, product_id)


@router.get("/categories/{category_id}/products", response_model=List[schemas.Product])
def get_products_by_category(
    category_id: int,
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of products to return"),
    db: Session = Depends(get_db)
):
    """Get products by category with pagination"""
    # Verify category exists
    verify_category_exists(category_id, db)
    
    products = crud.get_products_by_category(db, category_id, skip=skip, limit=limit)
    return products
