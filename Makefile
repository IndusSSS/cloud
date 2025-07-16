# Makefile
.PHONY: help install test lint format clean run dev docker-build docker-run ssl-certs

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

ssl-certs: ## Generate SSL certificates for HTTPS-only access
	@echo "Generating SSL certificates for HTTPS-only access..."
	@mkdir -p ssl/certs ssl/private
	@echo "Generating certificate for cloud.smartsecurity.solutions..."
	@openssl genrsa -out ssl/private/cloud.smartsecurity.solutions.key 2048
	@openssl req -new -key ssl/private/cloud.smartsecurity.solutions.key -out ssl/cloud.smartsecurity.solutions.csr -subj "/C=US/ST=State/L=City/O=SmartSecurity/OU=IT/CN=cloud.smartsecurity.solutions"
	@openssl x509 -req -in ssl/cloud.smartsecurity.solutions.csr -signkey ssl/private/cloud.smartsecurity.solutions.key -out ssl/certs/cloud.smartsecurity.solutions.crt -days 365
	@rm ssl/cloud.smartsecurity.solutions.csr
	@echo "Generating certificate for admin.smartsecurity.solutions..."
	@openssl genrsa -out ssl/private/admin.smartsecurity.solutions.key 2048
	@openssl req -new -key ssl/private/admin.smartsecurity.solutions.key -out ssl/admin.smartsecurity.solutions.csr -subj "/C=US/ST=State/L=City/O=SmartSecurity/OU=IT/CN=admin.smartsecurity.solutions"
	@openssl x509 -req -in ssl/admin.smartsecurity.solutions.csr -signkey ssl/private/admin.smartsecurity.solutions.key -out ssl/certs/admin.smartsecurity.solutions.crt -days 365
	@rm ssl/admin.smartsecurity.solutions.csr
	@echo "SSL certificates generated successfully!"
	@echo "Next steps:"
	@echo "1. Add to /etc/hosts (Linux/Mac) or C:\Windows\System32\drivers\etc\hosts (Windows):"
	@echo "   127.0.0.1 cloud.smartsecurity.solutions"
	@echo "   127.0.0.1 admin.smartsecurity.solutions"
	@echo "2. Run: make docker-run"
	@echo "3. Access via HTTPS:"
	@echo "   - Cloud: https://cloud.smartsecurity.solutions"
	@echo "   - Admin: https://admin.smartsecurity.solutions"

setup: install ## Setup development environment
	pre-commit install

setup-https: ssl-certs docker-run ## Setup HTTPS-only environment with certificates and Docker
	@echo "HTTPS-only environment setup complete!"