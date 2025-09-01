from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from . import models, schemas
from .auth import get_password_hash


# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


# Category CRUD operations
def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[models.Category]:
    return db.query(models.Category).offset(skip).limit(limit).all()


def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, category_update: schemas.CategoryUpdate) -> Optional[models.Category]:
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    
    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    db_category = get_category(db, category_id)
    if not db_category:
        return False
    
    db.delete(db_category)
    db.commit()
    return True


# Product CRUD operations
def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_products(db: Session, skip: int = 0, limit: int = 100, category_id: Optional[int] = None) -> List[models.Product]:
    query = db.query(models.Product)
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    return query.offset(skip).limit(limit).all()


def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product_update: schemas.ProductUpdate) -> Optional[models.Product]:
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    db_product = get_product(db, product_id)
    if not db_product:
        return False
    
    db.delete(db_product)
    db.commit()
    return True


def get_product_by_name(db: Session, name: str) -> Optional[models.Product]:
    """Get product by name"""
    return db.query(models.Product).filter(models.Product.name == name).first()


def get_products_by_category(db: Session, category_id: int, skip: int = 0, limit: int = 100) -> List[models.Product]:
    """Get products by category with pagination"""
    return db.query(models.Product).filter(
        models.Product.category_id == category_id
    ).offset(skip).limit(limit).all()


def get_products_with_filters(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    search: Optional[str] = None
) -> List[models.Product]:
    """Get products with advanced filtering and search"""
    query = db.query(models.Product)
    
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    
    if in_stock is not None:
        if in_stock:
            query = query.filter(models.Product.stock > 0)
        else:
            query = query.filter(models.Product.stock == 0)
    
    if search:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                models.Product.name.ilike(f"%{search}%"),
                models.Product.description.ilike(f"%{search}%")
            )
        )
    
    return query.offset(skip).limit(limit).all()


def get_products_count(db: Session) -> int:
    """Get total count of products"""
    return db.query(models.Product).count()


def get_products_count_by_category(db: Session, category_id: int) -> int:
    """Get count of products in a category"""
    return db.query(models.Product).filter(
        models.Product.category_id == category_id
    ).count()


# Cart CRUD operations
def get_cart_items(db: Session, user_id: int) -> List[models.Cart]:
    return db.query(models.Cart).filter(models.Cart.user_id == user_id).all()


def get_cart_item(db: Session, user_id: int, product_id: int) -> Optional[models.Cart]:
    return db.query(models.Cart).filter(
        and_(models.Cart.user_id == user_id, models.Cart.product_id == product_id)
    ).first()


def add_to_cart(db: Session, user_id: int, cart_item: schemas.CartItemCreate) -> models.Cart:
    # Check if item already exists in cart
    existing_item = get_cart_item(db, user_id, cart_item.product_id)
    if existing_item:
        existing_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    
    db_cart_item = models.Cart(
        user_id=user_id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity
    )
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return db_cart_item


def update_cart_item(db: Session, user_id: int, product_id: int, quantity: int) -> Optional[models.Cart]:
    cart_item = get_cart_item(db, user_id, product_id)
    if not cart_item:
        return None
    
    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item


def remove_from_cart(db: Session, user_id: int, product_id: int) -> bool:
    cart_item = get_cart_item(db, user_id, product_id)
    if not cart_item:
        return False
    
    db.delete(cart_item)
    db.commit()
    return True


def clear_cart(db: Session, user_id: int) -> bool:
    cart_items = get_cart_items(db, user_id)
    for item in cart_items:
        db.delete(item)
    db.commit()
    return True


# Order CRUD operations
def get_order(db: Session, order_id: int) -> Optional[models.Order]:
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def get_user_orders(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Order]:
    return db.query(models.Order).filter(models.Order.user_id == user_id).offset(skip).limit(limit).all()


def get_all_orders(db: Session, skip: int = 0, limit: int = 100) -> List[models.Order]:
    return db.query(models.Order).offset(skip).limit(limit).all()


def create_order(db: Session, user_id: int, total_price: float) -> models.Order:
    db_order = models.Order(user_id=user_id, total_price=total_price)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def update_order_status(db: Session, order_id: int, status: models.OrderStatus) -> Optional[models.Order]:
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    return db_order


def create_order_item(db: Session, order_id: int, product_id: int, quantity: int, price: float) -> models.OrderItem:
    db_order_item = models.OrderItem(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        price=price
    )
    db.add(db_order_item)
    db.commit()
    db.refresh(db_order_item)
    return db_order_item

