# Makefile
.PHONY: help install test lint format clean run dev docker-build docker-run

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	poetry install

test: ## Run tests
	pytest -v

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=html

lint: ## Run linting
	ruff check .
	mypy app/

format: ## Format code
	black .
	ruff check --fix .

clean: ## Clean up generated files
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

run: ## Run the application
	uvicorn app.main:app --host 0.0.0.0 --port 8000

dev: ## Run in development mode
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

docker-build: ## Build Docker image
	docker build -t smartsecurity-cloud .

docker-run: ## Run with Docker Compose
	docker-compose up -d

docker-stop: ## Stop Docker containers
	docker-compose down

setup: install ## Setup development environment
	pre-commit install