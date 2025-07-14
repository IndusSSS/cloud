# SmartSecurity.Solutions Cloud Micro-service

A FastAPI-based micro-service for IoT device management and data ingestion in the SmartSecurity.Solutions platform.

## Features

- **User Authentication**: JWT-based authentication with Argon2 password hashing
- **Device Management**: CRUD operations for IoT devices
- **Data Ingestion**: REST API for receiving sensor data from devices
- **Real-time Processing**: Background worker for MQTT message processing
- **Scalable Architecture**: Async database operations with PostgreSQL
- **Security First**: Secure by design with proper authentication and authorization

## Quick Start

### Prerequisites

- Python 3.12+
- Poetry (dependency management)
- PostgreSQL
- Redis (optional, for caching)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd cloud
```

2. Install dependencies:
```bash
make install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the application:
```bash
make dev
```

The API will be available at `http://localhost:8000/api/v1/docs`

## API Documentation

### Authentication

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user info

### Device Management

- `GET /api/v1/devices` - List devices
- `POST /api/v1/devices` - Create device
- `GET /api/v1/devices/{id}` - Get device details
- `PUT /api/v1/devices/{id}` - Update device

### Data Ingestion

- `POST /api/v1/ingest` - Ingest sensor data
- `GET /api/v1/sensors/{device_id}` - Get device sensor readings

### User Management

- `GET /api/v1/users` - List users (admin only)
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user (admin only)

## Development

### Running Tests

```bash
make test
```

### Code Quality

```bash
make lint    # Run linting
make format  # Format code
```

### Docker

```bash
make docker-build  # Build image
make docker-run    # Run with docker-compose
```

## Architecture

The application follows a modular architecture:

- **`app/core/`** - Configuration and core settings
- **`app/models/`** - SQLModel database models
- **`app/api/`** - FastAPI endpoints and dependencies
- **`app/services/`** - Business logic services
- **`app/utils/`** - Utility functions and helpers
- **`app/worker.py`** - Background task processing

## Security

- JWT tokens for API authentication
- Argon2 password hashing
- Role-based access control
- Input validation and sanitization
- Secure database connections

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is proprietary software owned by SmartSecurity.Solutions.