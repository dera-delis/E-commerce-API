# 🛍️ E-commerce API

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![Tests](https://img.shields.io/badge/Tests-80%2F80%20passed-brightgreen.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

A production-ready, high-performance E-commerce API backend built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT authentication, and comprehensive testing. Features role-based access control, real-time monitoring, and Docker deployment.

## Features

- **Authentication & Authorization**: JWT-based authentication with role-based access control (admin/customer)
- **User Management**: User registration, login, and profile management
- **Product Management**: CRUD operations for products with category support
- **Category Management**: Product categorization system
- **Shopping Cart**: Add, update, remove, and clear cart items
- **Order Management**: Checkout process, order tracking, and status updates
- **Stock Management**: Automatic stock reduction on checkout
- **API Documentation**: Auto-generated OpenAPI docs with Swagger UI
- **Performance Monitoring**: Real-time metrics, rate limiting, and GZip compression
- **Security**: Input validation, SQL injection protection, and comprehensive error handling

## 🚀 Live Demo

- **API Base URL**: https://ecommerce-api-op5q.onrender.com  
- **Swagger Docs**: https://ecommerce-api-op5q.onrender.com/docs  
- **ReDoc**: https://ecommerce-api-op5q.onrender.com/redoc
- **Health Check**: https://ecommerce-api-op5q.onrender.com/health

*Deployment scripts and production configuration included in the repository.*

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
│   ├── monitoring.py    # Performance monitoring
│   └── routers/         # API route handlers
│       ├── auth.py      # Authentication endpoints
│       ├── categories.py # Category management
│       ├── products.py  # Product management
│       ├── cart.py      # Shopping cart operations
│       └── orders.py    # Order management
├── tests/               # Test suite
├── screenshots/         # Visual documentation
│   ├── swagger-ui.png   # API documentation interface
│   ├── redoc.png        # Alternative API documentation
│   ├── docker-containers.png # Container deployment
│   ├── database-schema.png   # Database structure
│   └── api-testing/     # API testing workflow
│       ├── user-signup.png      # User registration
│       ├── adding-product-to-cart.png # Cart operations
│       └── checkout-order.png   # Order completion
├── scripts/             # Utility scripts
│   ├── init_db.py       # Database initialization
│   ├── seed_data.py     # Sample data seeding
│   └── startup.py       # Application startup
├── alembic/             # Database migrations
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker services
├── Dockerfile.prod      # Production container
├── env.example          # Environment variables template
├── pytest.ini          # Test configuration
├── Makefile            # Development commands
└── README.md           # This file
```

## 📸 Screenshots

### API Documentation (Swagger UI)
![API Documentation](screenshots/swagger-ui.png)

### API Documentation (ReDoc)
![ReDoc Documentation](screenshots/redoc.png)

### Docker Containers Running
![Docker Containers](screenshots/docker-containers.png)

### Database Schema
![Database Schema](screenshots/database-schema.png)

### API Testing Workflow
![User Signup](screenshots/api-testing/user-signup.png)
![Adding Product to Cart](screenshots/api-testing/adding-product-to-cart.png)
![Checkout Order](screenshots/api-testing/checkout-order.png)

### Test Suite Execution
![Test Suite](screenshots/pytest.png)

*Note: Screenshots demonstrate the complete API workflow from user registration to order completion.*

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
   cp env.example .env
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
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info

### Categories
- `GET /categories/` - List all categories (public)
- `GET /categories/{category_id}` - Get category by ID (public)
- `POST /categories/` - Create category (admin only)
- `PUT /categories/{category_id}` - Update category (admin only)
- `DELETE /categories/{category_id}` - Delete category (admin only)

### Products
- `GET /products/` - List all products (public)
- `GET /products/{product_id}` - Get product by ID (public)
- `GET /products/categories/{category_id}/products` - Get products by category (public)
- `POST /products/` - Create product (admin only)
- `PUT /products/{product_id}` - Update product (admin only)
- `DELETE /products/{product_id}` - Delete product (admin only)

### Cart
- `GET /cart/` - Get cart items (authenticated)
- `POST /cart/add` - Add item to cart (authenticated)
- `PUT /cart/{product_id}` - Update cart item quantity (authenticated)
- `DELETE /cart/{product_id}` - Remove item from cart (authenticated)
- `DELETE /cart/` - Clear cart (authenticated)

### Orders
- `GET /orders/` - Get orders (customers see their own, admins see all)
- `GET /orders/all` - Get all orders (admin only)
- `GET /orders/{order_id}` - Get order by ID (owner or admin)
- `POST /orders/checkout` - Checkout cart (customers only)
- `PUT /orders/{order_id}/status` - Update order status (admin only)

## Usage Examples

### 1. User Registration and Login

```bash
# Register a new user (Local)
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'

# Register a new user (Live Demo)
curl -X POST "https://ecommerce-api-op5q.onrender.com/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'

# Login (Local)
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=securepassword123"

# Login (Live Demo)
curl -X POST "https://ecommerce-api-op5q.onrender.com/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=securepassword123"
```

### 2. Product Management (Admin)

```bash
# Create a category
curl -X POST "http://localhost:8000/categories/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electronics",
    "description": "Electronic devices and accessories"
  }'

# Create a product
curl -X POST "http://localhost:8000/products/" \
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
curl -X POST "http://localhost:8000/cart/add" \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'

# View cart
curl -X GET "http://localhost:8000/cart/" \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```

### 4. Checkout Process

```bash
# Checkout cart
curl -X POST "http://localhost:8000/orders/checkout" \
  -H "Authorization: Bearer YOUR_USER_TOKEN"

# View orders
curl -X GET "http://localhost:8000/orders/" \
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

## 💼 Portfolio Project

This project is part of my **Backend Portfolio** showcasing production-ready API development skills.

- [GitHub Profile](https://github.com/dera-delis)  
- [LinkedIn](https://www.linkedin.com/in/dera-delis)  
- [Portfolio Website](https://dera-delis.dev) *(Coming Soon)*

### 🎯 What This Project Demonstrates

- **Full-Stack Backend Development** with modern Python frameworks
- **Database Design & Optimization** with PostgreSQL and SQLAlchemy
- **API Security & Authentication** with JWT and role-based access control
- **Testing & Quality Assurance** with comprehensive test coverage
- **DevOps & Deployment** with Docker and production configurations
- **Performance Optimization** with monitoring and caching strategies
- **Documentation & Best Practices** with professional project structure

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on GitHub or contact the development team.
