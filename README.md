# E-commerce API

A comprehensive E-commerce API backend built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT authentication, and pytest testing.

## Features

- **Authentication & Authorization**: JWT-based authentication with role-based access control (admin/customer)
- **User Management**: User registration, login, and profile management
- **Product Management**: CRUD operations for products with category support
- **Category Management**: Product categorization system
- **Shopping Cart**: Add, update, remove, and clear cart items
- **Order Management**: Checkout process, order tracking, and status updates
- **Stock Management**: Automatic stock reduction on checkout
- **API Documentation**: Auto-generated OpenAPI docs with Swagger UI

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt
- **Testing**: pytest with async support
- **Containerization**: Docker & Docker Compose

## Project Structure

```
ecommerce-api/
├── app/
│   ├── main.py          # FastAPI app entry point
│   ├── config.py        # Configuration and settings
│   ├── database.py      # Database connection and session
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── auth.py          # JWT authentication logic
│   ├── crud.py          # Database operations
│   ├── dependencies.py  # Reusable dependencies
│   └── routers/         # API route handlers
│       ├── auth.py      # Authentication endpoints
│       ├── categories.py # Category management
│       ├── products.py  # Product management
│       ├── cart.py      # Shopping cart operations
│       └── orders.py    # Order management
├── tests/               # Test suite
├── alembic/             # Database migrations
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker services
├── Dockerfile          # API container
└── README.md           # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL (if running locally)

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecommerce-api
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Option 2: Local Development

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database**
   ```bash
   # Create database
   createdb ecommerce
   
   # Update .env with your database URL
   DATABASE_URL=postgresql://username:password@localhost:5432/ecommerce
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info

### Categories
- `GET /api/v1/categories/` - List all categories (public)
- `GET /api/v1/categories/{id}` - Get category by ID (public)
- `POST /api/v1/categories/` - Create category (admin only)
- `PUT /api/v1/categories/{id}` - Update category (admin only)
- `DELETE /api/v1/categories/{id}` - Delete category (admin only)

### Products
- `GET /api/v1/products/` - List all products (public)
- `GET /api/v1/products/{id}` - Get product by ID (public)
- `POST /api/v1/products/` - Create product (admin only)
- `PUT /api/v1/products/{id}` - Update product (admin only)
- `DELETE /api/v1/products/{id}` - Delete product (admin only)

### Cart
- `GET /api/v1/cart/` - Get cart items (authenticated)
- `POST /api/v1/cart/add` - Add item to cart (authenticated)
- `PUT /api/v1/cart/{product_id}` - Update cart item quantity (authenticated)
- `DELETE /api/v1/cart/{product_id}` - Remove item from cart (authenticated)
- `DELETE /api/v1/cart/` - Clear cart (authenticated)

### Orders
- `GET /api/v1/orders/` - Get orders (customers see their own, admins see all)
- `GET /api/v1/orders/{id}` - Get order by ID (owner or admin)
- `POST /api/v1/orders/checkout` - Checkout cart (customers only)
- `PUT /api/v1/orders/{id}/status` - Update order status (admin only)

## Usage Examples

### 1. User Registration and Login

```bash
# Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=securepassword123"
```

### 2. Product Management (Admin)

```bash
# Create a category
curl -X POST "http://localhost:8000/api/v1/categories/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electronics",
    "description": "Electronic devices and accessories"
  }'

# Create a product
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smartphone",
    "description": "Latest smartphone model",
    "price": 699.99,
    "stock": 50,
    "category_id": 1
  }'
```

### 3. Shopping Cart Operations

```bash
# Add item to cart
curl -X POST "http://localhost:8000/api/v1/cart/add" \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'

# View cart
curl -X GET "http://localhost:8000/api/v1/cart/" \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```

### 4. Checkout Process

```bash
# Checkout cart
curl -X POST "http://localhost:8000/api/v1/orders/checkout" \
  -H "Authorization: Bearer YOUR_USER_TOKEN"

# View orders
curl -X GET "http://localhost:8000/api/v1/orders/" \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```

## Testing

Run the test suite with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

## Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migrations
```bash
alembic downgrade -1
```

## Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/ecommerce

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# App
APP_NAME=E-commerce API
DEBUG=true
```

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **Role-based Access Control**: Admin and customer roles
- **Input Validation**: Pydantic schemas for request validation
- **CORS Protection**: Configurable cross-origin resource sharing
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries

## Performance Features

- **Async Support**: FastAPI async/await for better performance
- **Database Indexing**: Proper database indexes on frequently queried fields
- **Connection Pooling**: SQLAlchemy connection pooling
- **Efficient Queries**: Optimized database queries with relationships

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on GitHub or contact the development team.
