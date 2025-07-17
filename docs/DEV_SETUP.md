# Development Setup

Quick start guide for setting up the SmartSecurity Cloud development environment.

## Prerequisites

- **Docker & Docker Compose**: Latest version
- **Python 3.12+**: For local development
- **Poetry**: Python dependency management
- **Git**: Version control

## Quick Start (≤3 lines)

```bash
git clone https://github.com/your-org/smartsecurity-cloud.git && cd smartsecurity-cloud
poetry install && poetry shell
docker compose up -d
```

## Detailed Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/smartsecurity-cloud.git
cd smartsecurity-cloud
```

### 2. Install Dependencies
```bash
# Install Python dependencies
poetry install

# Activate virtual environment
poetry shell

# Install pre-commit hooks (optional)
pre-commit install
```

### 3. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/smartsecurity
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# MQTT
MQTT_BROKER_URL=mqtt://localhost:1883
MQTT_USERNAME=admin
MQTT_PASSWORD=password

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. Start Services
```bash
# Start all services (database, Redis, MQTT)
docker compose up -d

# Verify services are running
docker compose ps
```

### 5. Database Setup
```bash
# Run database migrations
poetry run alembic upgrade head

# Seed initial data
poetry run python -m app.seed_data
```

### 6. Start Development Server
```bash
# Start FastAPI backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start frontend (optional)
cd frontend && npm install && npm run dev
```

## Service URLs

Once running, access the services at:

- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:3000
- **Customer Portal**: http://localhost:3001
- **Health Check**: http://localhost:8000/health

## Development Workflow

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_auth.py

# Run with coverage
poetry run pytest --cov=app

# Run security tests
poetry run python test_security_runner.py
```

### Code Quality
```bash
# Format code
poetry run black app/ tests/

# Lint code
poetry run ruff check app/ tests/

# Type checking
poetry run mypy app/
```

### Database Operations
```bash
# Create new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1

# Reset database
poetry run alembic downgrade base
poetry run alembic upgrade head
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

#### Docker Issues
```bash
# Reset Docker containers
docker compose down -v
docker compose up -d

# Rebuild containers
docker compose build --no-cache
```

#### Database Connection Issues
```bash
# Check database status
docker compose logs postgres

# Reset database
docker compose down -v
docker compose up -d postgres
poetry run alembic upgrade head
```

#### Redis Connection Issues
```bash
# Check Redis status
docker compose logs redis

# Test Redis connection
poetry run python -c "import redis; r = redis.Redis(); r.ping()"
```

### Environment-Specific Setup

#### macOS
```bash
# Install dependencies via Homebrew
brew install python@3.12 docker docker-compose

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

#### Ubuntu/Debian
```bash
# Install system dependencies
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip docker.io docker-compose

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

#### Windows
```bash
# Install via Chocolatey
choco install python docker-desktop

# Install Poetry
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

## IDE Setup

### VS Code Configuration
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

### PyCharm Configuration
1. Open project in PyCharm
2. Go to Settings → Project → Python Interpreter
3. Add new interpreter: Poetry Environment
4. Select the project's `pyproject.toml`

## Production Setup

For production deployment, see [DEPLOYMENT.md](./DEPLOYMENT.md).

## Contributing

Before contributing, please read [CONTRIBUTING.md](./CONTRIBUTING.md) and [MESS_GUIDELINES.md](./MESS_GUIDELINES.md). 