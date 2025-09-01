.PHONY: help install test run clean docker-up docker-down migrate seed

help: ## Show this help message
	@echo "E-commerce API - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term-missing

test-watch: ## Run tests in watch mode
	pytest-watch

run: ## Run the application locally
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Run the application in production mode
	uvicorn app.main:app --host 0.0.0.0 --port 8000

clean: ## Clean up Python cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

docker-up: ## Start Docker services
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-build: ## Build Docker images
	docker-compose build

migrate: ## Run database migrations
	alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create msg="description")
	alembic revision --autogenerate -m "$(msg)"

migrate-rollback: ## Rollback last migration
	alembic downgrade -1

seed: ## Seed database with sample data
	python scripts/seed_data.py

setup: ## Complete setup (install, migrate, seed)
	$(MAKE) install
	$(MAKE) migrate
	$(MAKE) seed

docker-setup: ## Complete Docker setup
	$(MAKE) docker-up
	sleep 10
	$(MAKE) migrate
	$(MAKE) seed

format: ## Format code with black
	black app/ tests/

lint: ## Run linting checks
	flake8 app/ tests/
	black --check app/ tests/

check: ## Run all checks (lint, test)
	$(MAKE) lint
	$(MAKE) test

dev: ## Start development environment
	$(MAKE) docker-up
	sleep 10
	$(MAKE) migrate
	$(MAKE) seed
	$(MAKE) run
