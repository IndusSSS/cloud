@echo off
echo ========================================
echo SmartSecurity.Solutions Cloud Setup
echo ========================================

echo.
echo [1/5] Installing Python dependencies...
pip install fastapi uvicorn sqlmodel sqlalchemy[asyncio] asyncpg redis aiomqtt slowapi prometheus-fastapi-instrumentator pyotp passlib[argon2] python-jose[cryptography] python-multipart pydantic pydantic-settings

echo.
echo [2/5] Installing development dependencies...
pip install pytest pytest-asyncio httpx ruff mypy black

echo.
echo [3/5] Creating .env file...
if not exist .env (
    echo Creating .env file with default settings...
    (
        echo # Database Configuration
        echo DATABASE_URL=postgresql+asyncpg://cloud:cloudpass@localhost/cloud_db
        echo DATABASE_ECHO=false
        echo.
        echo # Security Configuration
        echo SECRET_KEY=your-secret-key-change-in-production
        echo ALGORITHM=HS256
        echo ACCESS_TOKEN_EXPIRE_MINUTES=30
        echo.
        echo # Redis Configuration
        echo REDIS_URL=redis://localhost:6379/0
        echo.
        echo # MQTT Configuration
        echo MQTT_BROKER=localhost
        echo MQTT_PORT=1883
        echo.
        echo # API Configuration
        echo API_PREFIX=/api/v1
        echo DEBUG=true
        echo HOST=0.0.0.0
        echo PORT=8000
    ) > .env
    echo .env file created successfully!
) else (
    echo .env file already exists, skipping...
)

echo.
echo [4/5] Testing application startup...
python -c "from app.main import app; print('✓ Application imports successfully')"

echo.
echo [5/5] Setup complete!
echo.
echo Next steps:
echo 1. Start Docker services: docker-compose up -d
echo 2. Run the application: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
echo 3. Open browser: http://localhost:8000/api/v1/docs
echo 4. Frontend: http://localhost:8080
echo.
echo Available commands:
echo - test: python -m pytest
echo - lint: python -m ruff check .
echo - format: python -m black .
echo.
pause 