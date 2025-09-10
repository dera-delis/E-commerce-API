# 🛍️ E-commerce API

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![Tests](https://github.com/dera-delis/E-commerce-API/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/dera-delis/E-commerce-API/actions)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

A production-ready, high-performance E-commerce API backend built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT authentication, and comprehensive testing. Features role-based access control, real-time monitoring, and Docker deployment.

> **🎯 Ready to explore?** Try the API locally or check the [**Live Demo**](#-live-demo) section below!

## Features

- **Authentication & Authorization**: JWT-based authentication with role-based access control (admin/customer)
- **User Management**: User registration, login, and profile management

### 🔐 Role-Based Access Control (RBAC)

| Role | Permissions |
|------|-------------|
| **Customer** | • Add items to cart<br>• Update cart quantities<br>• Remove items from cart<br>• Clear entire cart<br>• Checkout cart to create orders<br>• View own orders only<br>• View products and categories |
| **Admin** | • All customer permissions<br>• Create, update, delete products<br>• Create, update, delete categories<br>• View all orders from all users<br>• Update order status<br>• Manage user accounts |
- **Product Management**: CRUD operations for products with category support
- **Category Management**: Product categorization system
- **Shopping Cart**: Add, update, remove, and clear cart items
- **Order Management**: Checkout process, order tracking, and status updates
- **Stock Management**: Automatic stock reduction on checkout
- **API Documentation**: Auto-generated OpenAPI docs with Swagger UI
- **API Versioning**: RESTful API with `/api/v1/` versioning for backward compatibility
- **Performance Monitoring**: Real-time metrics, rate limiting, and GZip compression
- **Security**: Input validation, SQL injection protection, and comprehensive error handling

## 🚀 Live Demo

> **⚠️ Note:** The live demo may occasionally be unavailable due to free tier limitations. For the best experience, please run the API locally using the instructions below.

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Try_Here-blue?style=for-the-badge&logo=fastapi)](https://ecommerce-api-op5q.onrender.com/docs)

[![API Documentation](https://img.shields.io/badge/📚_API_Docs-Swagger_UI-green?style=for-the-badge&logo=swagger)](https://ecommerce-api-op5q.onrender.com/docs)

[![Alternative Docs](https://img.shields.io/badge/📖_ReDoc-View_Docs-orange?style=for-the-badge&logo=readthedocs)](https://ecommerce-api-op5q.onrender.com/redoc)

[![Health Check](https://img.shields.io/badge/💚_Health_Check-API_Status-brightgreen?style=for-the-badge&logo=healthchecks.io)](https://ecommerce-api-op5q.onrender.com/health)

**Quick Links:**
- 🔗 [API Base URL](https://ecommerce-api-op5q.onrender.com) *(may be sleeping)*
- 📚 [Interactive Documentation](https://ecommerce-api-op5q.onrender.com/docs) *(may be sleeping)*
- 📖 [Alternative Documentation](https://ecommerce-api-op5q.onrender.com/redoc) *(may be sleeping)*
- 💚 [Health Status](https://ecommerce-api-op5q.onrender.com/health) *(may be sleeping)*

### 🏃‍♂️ **Quick Local Test** (Recommended)

If the live demo is unavailable, you can test the API locally in under 2 minutes:

```bash
# Clone and start the API
git clone https://github.com/dera-delis/E-commerce-API.git
cd E-commerce-API
docker-compose up -d

# Test the API
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Open in browser
```

### 🧪 **Quick API Test** (Working Examples)

Test the API immediately with these working curl commands:

```bash
# 1. Health Check
curl http://localhost:8000/health

# 2. Get all products (no auth required)
curl http://localhost:8000/api/v1/products/

# 3. Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "password123"
  }'

# 4. Login and get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"

# 5. Add item to cart (replace YOUR_TOKEN with actual token)
curl -X POST "http://localhost:8000/api/v1/cart/add" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

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
├── .github/             # GitHub Actions CI/CD
│   └── workflows/
│       └── ci.yml       # Automated testing pipeline
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker services
├── Dockerfile.prod      # Production container
├── database_schema.dbml # Database schema diagram (dbdiagram.io)
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

*Comprehensive database design with optimized relationships and performance indexes. The schema includes 6 core tables with proper foreign key constraints and composite indexes for optimal query performance.*

**Schema Features:**
- 🏗️ **6 Core Tables**: Users, Categories, Products, Orders, Order Items, Cart
- 🔗 **Optimized Relationships**: Proper foreign key constraints and cascading
- ⚡ **Performance Indexes**: Composite indexes for common query patterns
- 🔒 **Data Integrity**: Enums for status fields and proper constraints
- 📊 **Scalable Design**: Supports high-volume e-commerce operations

> **💡 Interactive Schema**: View the live database schema at [dbdiagram.io](https://dbdiagram.io) using the `database_schema.dbml` file in the repository.

### API Testing Workflow
![User Signup](screenshots/api-testing/user-signup.png)
![Adding Product to Cart](screenshots/api-testing/adding-product-to-cart.png)
![Checkout Order](screenshots/api-testing/checkout-order.png)

### Test Suite Execution
![Test Suite](screenshots/pytest.png)

**Test Results:**
- ✅ **81/81 tests passed** (100% success rate)
- 🚀 **Comprehensive coverage** including authentication, cart operations, orders, and edge cases
- 🔒 **Security testing** with SQL injection and XSS protection validation
- ⚡ **Performance testing** with rate limiting and concurrent request handling
- 🛡️ **Edge case testing** with malformed inputs and boundary conditions

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

5. **Seed the database with sample data** *(Optional but recommended)*
   ```bash
   docker-compose exec api python scripts/seed_data.py
   ```
   This creates sample data including:
   - **Admin user**: `admin@example.com` / `admin123`
   - **Test customer**: `customer@example.com` / `customer123`
   - **Sample categories**: Electronics, Clothing, Books, Home & Garden
   - **Sample products**: Various items across all categories

6. **Access the API**
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

5. **Seed the database with sample data** *(Optional but recommended)*
   ```bash
   python scripts/seed_data.py
   ```
   This creates sample users, categories, and products for easy testing.

6. **Start the application**
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
- `GET /api/v1/categories/{category_id}` - Get category by ID (public)
- `POST /api/v1/categories/` - Create category (admin only)
- `PUT /api/v1/categories/{category_id}` - Update category (admin only)
- `DELETE /api/v1/categories/{category_id}` - Delete category (admin only)

### Products
- `GET /api/v1/products/` - List all products (public)
- `GET /api/v1/products/{product_id}` - Get product by ID (public)
- `GET /api/v1/products/categories/{category_id}/products` - Get products by category (public)
- `POST /api/v1/products/` - Create product (admin only)
- `PUT /api/v1/products/{product_id}` - Update product (admin only)
- `DELETE /api/v1/products/{product_id}` - Delete product (admin only)

### Cart
- `GET /api/v1/cart/` - Get cart items (authenticated)
- `POST /api/v1/cart/add` - Add item to cart (authenticated)
- `PUT /api/v1/cart/{product_id}` - Update cart item quantity (authenticated)
- `DELETE /api/v1/cart/{product_id}` - Remove item from cart (authenticated)
- `DELETE /api/v1/cart/` - Clear cart (authenticated)

### Orders
- `GET /api/v1/orders/` - Get orders (customers see their own, admins see all)
- `GET /api/v1/orders/all` - Get all orders (admin only)
- `GET /api/v1/orders/{order_id}` - Get order by ID (owner or admin)
- `POST /api/v1/orders/checkout` - Checkout cart (customers only)
- `PUT /api/v1/orders/{order_id}/status` - Update order status (admin only)

## Usage Examples

### 1. User Registration and Login

> **💡 Try it live!** Use the [Interactive Documentation](https://ecommerce-api-op5q.onrender.com/docs) to test these endpoints directly in your browser.

```bash
# Register a new user (Local Development)
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'

# Register a new user (Live Demo)
curl -X POST "https://ecommerce-api-op5q.onrender.com/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'

# Login (Local Development)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=securepassword123"

# Login (Live Demo)
curl -X POST "https://ecommerce-api-op5q.onrender.com/api/v1/auth/login" \
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
