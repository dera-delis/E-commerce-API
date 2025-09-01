#!/bin/bash

# Production Deployment Script for E-commerce API
set -e

echo "🚀 Starting production deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env.prod exists
if [ ! -f .env.prod ]; then
    echo "❌ .env.prod file not found. Please create it with production values."
    exit 1
fi

# Load production environment variables
export $(cat .env.prod | grep -v '^#' | xargs)

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p nginx/logs nginx/ssl

# Generate self-signed SSL certificate for testing (replace with real certs in production)
if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
    echo "🔐 Generating self-signed SSL certificate..."
    openssl req -x509 -newkey rsa:4096 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker compose -f docker-compose.prod.yml down --volumes

# Build and start production services
echo "🔨 Building and starting production services..."
docker compose -f docker-compose.prod.yml up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
if ! docker compose -f docker-compose.prod.yml ps | grep -q "healthy"; then
    echo "❌ Services are not healthy. Check logs with: docker compose -f docker-compose.prod.yml logs"
    exit 1
fi

# Run database migrations
echo "🗄️ Running database migrations..."
docker compose -f docker-compose.prod.yml exec api alembic upgrade head

# Seed initial data
echo "🌱 Seeding initial data..."
docker compose -f docker-compose.prod.yml exec api python scripts/seed_data.py

# Test the API
echo "🧪 Testing the API..."
sleep 10
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is responding correctly"
else
    echo "❌ API is not responding. Check logs with: docker compose -f docker-compose.prod.yml logs api"
    exit 1
fi

echo "🎉 Production deployment completed successfully!"
echo ""
echo "📊 Service Status:"
docker compose -f docker-compose.prod.yml ps
echo ""
echo "🌐 API is available at:"
echo "   - HTTP:  http://localhost (redirects to HTTPS)"
echo "   - HTTPS: https://localhost"
echo "   - Direct: http://localhost:8000"
echo ""
echo "📚 API Documentation:"
echo "   - Swagger UI: https://localhost/docs"
echo "   - ReDoc: https://localhost/redoc"
echo ""
echo "📝 Useful commands:"
echo "   - View logs: docker compose -f docker-compose.prod.yml logs -f"
echo "   - Stop services: docker compose -f docker-compose.prod.yml down"
echo "   - Restart services: docker compose -f docker-compose.prod.yml restart"
echo "   - Update services: docker compose -f docker-compose.prod.yml up -d --build"
