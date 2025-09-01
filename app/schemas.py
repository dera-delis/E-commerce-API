from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from .models import UserRole, OrderStatus


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.CUSTOMER  # Default to customer


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str
    password: str
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Category schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: Optional[str] = None


class Category(CategoryBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Product schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category_id: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Sample Product",
                "description": "A sample product description",
                "price": 99.99,
                "stock": 100,
                "category_id": 1
            }
        }
    )


class ProductCreate(ProductBase):
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Product name cannot be empty or whitespace-only')
        if len(v.strip()) < 1:
            raise ValueError('Product name must be at least 1 character long')
        return v.strip()
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Price cannot be negative')
        if v > 1e6:  # Max price of 1 million
            raise ValueError('Price is too high')
        return v
    
    @field_validator('stock')
    @classmethod
    def validate_stock(cls, v):
        if v < 0:
            raise ValueError('Stock cannot be negative')
        if v > 1e6:  # Max stock of 1 million
            raise ValueError('Stock is too high')
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None


class Product(ProductBase):
    id: int
    created_at: datetime
    category: Category
    
    model_config = ConfigDict(from_attributes=True)


# Cart schemas
class CartItemBase(BaseModel):
    product_id: int
    quantity: int


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int


class CartItem(CartItemBase):
    id: int
    user_id: int
    product: Product
    
    model_config = ConfigDict(from_attributes=True)


# Order schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    order_id: int
    product: Product
    
    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    total_price: float
    status: OrderStatus = OrderStatus.PENDING


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None


class Order(OrderBase):
    id: int
    user_id: int
    created_at: datetime
    order_items: List[OrderItem]
    
    model_config = ConfigDict(from_attributes=True)


# Checkout schema
class CheckoutRequest(BaseModel):
    pass  # No additional data needed, uses current cart
