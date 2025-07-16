# SmartSecurity.Solutions Cloud Micro-service

A FastAPI-based micro-service for IoT device management and data ingestion in the SmartSecurity.Solutions platform.

## Features

- **User Authentication**: JWT-based authentication with Argon2 password hashing
- **Device Management**: CRUD operations for IoT devices
- **Data Ingestion**: REST API for receiving sensor data from devices
- **Real-time Processing**: Background worker for MQTT message processing
- **Scalable Architecture**: Async database operations with PostgreSQL
- **Security First**: Secure by design with proper authentication and authorization
- **HTTPS-Only Access**: Enforced HTTPS with SSL/TLS encryption and security headers
- **Multi-tenant Architecture**: Tenant isolation and role-based access control
- **Admin Console**: Comprehensive admin interface for system management

## Quick Start

### Prerequisites

- Python 3.12+
- Poetry (dependency management)
- PostgreSQL
- Redis (optional, for caching)
- Docker and Docker Compose (for HTTPS setup)
- OpenSSL (for certificate generation)

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

#### Development Mode (HTTP)
```bash
make dev
```
The API will be available at `http://localhost:8000/api/v1/docs`

#### Production Mode (HTTPS-Only)
```bash
# Generate SSL certificates and start with Docker
make setup-https
```
- **Customer Portal**: https://cloud.smartsecurity.solutions
- **Admin Console**: https://admin.smartsecurity.solutions

## HTTPS-Only Setup

The platform now enforces HTTPS-only access for enhanced security. See [HTTPS_SETUP.md](HTTPS_SETUP.md) for detailed configuration instructions.

### Quick HTTPS Setup
```bash
# Generate SSL certificates
make ssl-certs

# Add to hosts file:
# 127.0.0.1 cloud.smartsecurity.solutions
# 127.0.0.1 admin.smartsecurity.solutions

# Start with Docker
docker-compose up -d
```

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

### Admin Endpoints

- `GET /api/v1/admin/users` - System-wide user management
- `GET /api/v1/admin/devices` - System-wide device management
- `GET /api/v1/admin/tenants` - Tenant management
- `GET /api/v1/admin/audit` - Audit log access
- `POST /api/v1/admin/ota/firmware/rollout` - OTA firmware management

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
make docker-stop   # Stop containers
```

## Architecture

The application follows a modular architecture:

- **`app/core/`** - Configuration and core settings
- **`app/models/`** - SQLModel database models
- **`app/api/`** - FastAPI endpoints and dependencies
- **`app/services/`** - Business logic services
- **`app/utils/`** - Utility functions and helpers
- **`app/worker.py`** - Background task processing
- **`nginx/`** - Nginx configuration for HTTPS and reverse proxy
- **`ssl/`** - SSL certificates and private keys

## Security

- JWT tokens for API authentication
- Argon2 password hashing
- Role-based access control (RBAC)
- Input validation and sanitization
- Secure database connections
- HTTPS-only access enforcement
- Comprehensive security headers
- SSL/TLS encryption
- Multi-tenant isolation
- Audit logging for all admin actions

## Frontend Applications

### Customer Portal (`frontend_cloud/`)
- Device management interface
- Real-time sensor data visualization
- User profile management
- Support and documentation

### Admin Console (`frontend_admin/`)
- System-wide user management
- Device administration
- Tenant management
- System health monitoring
- Audit log viewer
- Feature flag management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is proprietary software owned by SmartSecurity.Solutions.