# Production Deployment Guide

This guide covers deploying the E-commerce API to production with Docker, Nginx, and monitoring.

## Prerequisites

- Docker and Docker Compose installed
- OpenSSL for SSL certificate generation
- Domain name (for production SSL certificates)
- Server with at least 2GB RAM and 20GB disk space

## Quick Start

### 1. Environment Setup

Create a production environment file:

```bash
cp .env.example .env.prod
```

Edit `.env.prod` with your production values:

```env
# Database Configuration
DATABASE_URL=postgresql://ecommerce_user:your_secure_password@localhost:5433/ecommerce
POSTGRES_PASSWORD=your_secure_password

# Redis Configuration
REDIS_URL=redis://:your_redis_password@localhost:6379/0
REDIS_PASSWORD=your_redis_password

# JWT Configuration
SECRET_KEY=your_super_secret_key_here_make_it_long_and_random_at_least_32_characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Application Configuration
APP_NAME=E-commerce API
DEBUG=false
```

### 2. SSL Certificates

For production, use Let's Encrypt or your preferred CA. For testing, the deployment script generates self-signed certificates.

### 3. Deploy

```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

## Manual Deployment

### 1. Start Services

```bash
# Create necessary directories
mkdir -p nginx/logs nginx/ssl

# Generate SSL certificates (for testing)
openssl req -x509 -newkey rsa:4096 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Start production services
docker compose -f docker-compose.prod.yml up -d --build
```

### 2. Database Setup

```bash
# Run migrations
docker compose -f docker-compose.prod.yml exec api alembic upgrade head

# Seed data
docker compose -f docker-compose.prod.yml exec api python scripts/seed_data.py
```

### 3. Verify Deployment

```bash
# Check service status
docker compose -f docker-compose.prod.yml ps

# Test API
curl -k https://localhost/health
```

## Production Considerations

### Security

1. **Environment Variables**: Never commit `.env.prod` to version control
2. **SSL Certificates**: Use proper CA-signed certificates in production
3. **Firewall**: Configure firewall to only allow necessary ports
4. **Secrets Management**: Use a secrets management service for production

### Performance

1. **Load Balancing**: Add more API instances behind Nginx
2. **Caching**: Redis is included for session and data caching
3. **Database**: Consider read replicas for high-traffic scenarios
4. **Monitoring**: Use the built-in metrics endpoint for monitoring

### Monitoring

The API includes several monitoring endpoints:

- `/health` - Basic health check
- `/metrics` - Detailed application metrics
- Response headers include timing information

### Scaling

To scale the API:

1. **Horizontal Scaling**: Add more API containers
2. **Database Scaling**: Use connection pooling and read replicas
3. **Caching**: Implement Redis caching for frequently accessed data
4. **CDN**: Use a CDN for static assets

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure ports 80, 443, 8000, 5433, 6379 are available
2. **SSL Issues**: Check certificate paths and permissions
3. **Database Connection**: Verify database credentials and network connectivity
4. **Memory Issues**: Monitor container resource usage

### Logs

```bash
# View all logs
docker compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml logs -f postgres
```

### Health Checks

```bash
# Check service health
docker compose -f docker-compose.prod.yml ps

# Test API endpoints
curl -k https://localhost/health
curl -k https://localhost/metrics
```

## Maintenance

### Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and restart services
docker compose -f docker-compose.prod.yml up -d --build

# Run migrations if needed
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

### Backups

```bash
# Database backup
docker compose -f docker-compose.prod.yml exec postgres pg_dump -U ecommerce_user ecommerce > backup.sql

# Restore database
docker compose -f docker-compose.prod.yml exec -T postgres psql -U ecommerce_user ecommerce < backup.sql
```

### Monitoring

Set up external monitoring for:

- API response times
- Error rates
- System resource usage
- Database performance
- SSL certificate expiration

## Security Checklist

- [ ] Strong passwords for all services
- [ ] SSL certificates properly configured
- [ ] Firewall rules configured
- [ ] Regular security updates
- [ ] Secrets management implemented
- [ ] Access logging enabled
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] Input validation implemented
- [ ] SQL injection protection
- [ ] XSS protection headers

## Performance Checklist

- [ ] Database indexes created
- [ ] Connection pooling configured
- [ ] Caching implemented
- [ ] Gzip compression enabled
- [ ] Static file serving optimized
- [ ] Load balancing configured
- [ ] Monitoring and alerting set up
- [ ] Performance testing completed

## Support

For deployment issues:

1. Check the logs: `docker compose -f docker-compose.prod.yml logs`
2. Verify environment variables
3. Check service health: `docker compose -f docker-compose.prod.yml ps`
4. Test individual services
5. Review this deployment guide
