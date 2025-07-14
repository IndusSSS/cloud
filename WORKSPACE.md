# SmartSecurity.Solutions Cloud - Workspace Context

## Project Overview

**SmartSecurity.Solutions Cloud** is a comprehensive IoT device management and data ingestion platform designed for security and monitoring applications. This microservice-based architecture provides real-time data processing, device management, and secure API access for IoT security devices.

## Business Context

### Target Market
- **Security Companies**: Commercial and residential security service providers
- **Facility Managers**: Building and infrastructure monitoring
- **IoT Device Manufacturers**: Security camera, sensor, and monitoring device companies
- **System Integrators**: Companies that deploy and manage security systems

### Core Value Proposition
- **Real-time Monitoring**: Live data streaming from IoT security devices
- **Scalable Architecture**: Multi-tenant cloud platform supporting thousands of devices
- **Secure by Design**: Enterprise-grade security with JWT authentication and role-based access
- **Easy Integration**: RESTful APIs and WebSocket support for real-time updates
- **Comprehensive Analytics**: Data ingestion, storage, and retrieval for security insights

## Technical Architecture

### System Components

#### 1. **API Gateway** (`app/main.py`)
- FastAPI-based REST API server
- WebSocket support for real-time data streaming
- Automatic OpenAPI documentation generation
- Health check endpoints for monitoring

#### 2. **Authentication & Authorization** (`app/api/v1/endpoints/auth.py`)
- JWT-based authentication system
- Argon2 password hashing for security
- Role-based access control (User/Admin/System Admin)
- Multi-tenant user management

#### 3. **Device Management** (`app/api/v1/endpoints/devices.py`)
- CRUD operations for IoT devices
- Device status monitoring and configuration
- Tenant-aware device isolation
- Device specifications and metadata storage

#### 4. **Data Ingestion** (`app/api/v1/endpoints/ingest.py`)
- REST API for sensor data ingestion
- MQTT message processing via background worker
- Data validation and sanitization
- Support for various sensor types and formats

#### 5. **Real-time Processing** (`app/worker.py`)
- Background MQTT message consumer
- Redis pub/sub for real-time data distribution
- WebSocket broadcasting to connected clients
- Data aggregation and analytics

#### 6. **Multi-tenancy** (`app/models/tenant.py`)
- Tenant isolation and management
- Subscription plan support (Free/Pro/Enterprise)
- Resource allocation per tenant
- Billing and usage tracking foundation

### Data Models

#### Core Entities
- **Users**: Authentication, roles, and profiles
- **Tenants**: Multi-tenant isolation and billing
- **Devices**: IoT device registry and configuration
- **Sensors**: Sensor data storage and retrieval
- **Audit Logs**: Security event tracking and compliance

#### Relationships
```
Tenant (1) ←→ (N) Users
Tenant (1) ←→ (N) Devices  
Device (1) ←→ (N) Sensors
User (1) ←→ (N) AuditLogs
```

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python 3.12+)
- **Database**: PostgreSQL with async support
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Authentication**: JWT with Argon2 hashing
- **Message Queue**: Redis for pub/sub
- **MQTT**: Eclipse Mosquitto broker

#### Frontend
- **Framework**: Vue.js 3 with Composition API
- **Styling**: Tailwind CSS
- **Charts**: ApexCharts for data visualization
- **Build Tool**: Vite
- **Deployment**: Nginx for static serving

#### DevOps
- **Containerization**: Docker & Docker Compose
- **Dependency Management**: Poetry
- **Code Quality**: Black, Ruff, MyPy
- **Testing**: Pytest with async support
- **CI/CD**: Pre-commit hooks

## API Design

### REST Endpoints

#### Authentication
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Current user info

#### Device Management
- `GET /api/v1/devices` - List devices (tenant-scoped)
- `POST /api/v1/devices` - Create new device
- `GET /api/v1/devices/{id}` - Get device details
- `PUT /api/v1/devices/{id}` - Update device
- `DELETE /api/v1/devices/{id}` - Delete device

#### Data Ingestion
- `POST /api/v1/ingest/ingest` - Ingest sensor data
- `GET /api/v1/ingest/sensors/{device_id}` - Get sensor readings
- `POST /api/v1/ingest/root/v1/health` - Health beacon endpoint

#### User Management
- `GET /api/v1/users` - List users (admin only)
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user (admin only)
- `POST /api/v1/users` - Create user (admin only)

#### Tenant Management
- `GET /api/v1/tenants` - List tenants (system admin only)
- `POST /api/v1/tenants` - Create tenant
- `GET /api/v1/tenants/{id}` - Get tenant details
- `PUT /api/v1/tenants/{id}` - Update tenant
- `DELETE /api/v1/tenants/{id}` - Delete tenant

#### Audit & Monitoring
- `GET /api/v1/audit` - List audit logs (admin only)
- `GET /api/v1/audit/{id}` - Get audit log details

### WebSocket Endpoints
- `WS /ws/{tenant_id}` - Real-time data streaming
- `WS /api/v1/ws/live/{device_id}` - Device-specific live data

## Security Architecture

### Authentication Flow
1. **Login**: Username/password → JWT token
2. **Authorization**: JWT token → User context
3. **Access Control**: Role-based permissions
4. **Audit**: All actions logged for compliance

### Security Features
- **Password Security**: Argon2 hashing with salt
- **Token Security**: JWT with configurable expiration
- **Data Isolation**: Tenant-based data separation
- **Input Validation**: Pydantic models for all inputs
- **SQL Injection Protection**: Parameterized queries
- **CORS Configuration**: Controlled cross-origin access

### Compliance Considerations
- **Audit Logging**: Complete action tracking
- **Data Retention**: Configurable data lifecycle
- **Access Controls**: Principle of least privilege
- **Encryption**: TLS for data in transit
- **Privacy**: GDPR-ready data handling

## Deployment Architecture

### Development Environment
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Server    │    │   Background    │
│   (Vue.js)      │◄──►│   (FastAPI)     │◄──►│   Worker        │
│   Port: 3000    │    │   Port: 8000    │    │   (MQTT)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │   MQTT Broker   │
│   Database      │    │   (Pub/Sub)     │    │   (Mosquitto)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Production Considerations
- **Load Balancing**: Nginx reverse proxy
- **Database**: PostgreSQL with connection pooling
- **Caching**: Redis for session and data caching
- **Monitoring**: Health checks and metrics
- **Scaling**: Horizontal scaling with container orchestration
- **Backup**: Automated database backups
- **SSL/TLS**: HTTPS termination and certificate management

## Development Workflow

### Local Development
1. **Setup**: `make setup` - Install dependencies and pre-commit hooks
2. **Database**: Docker Compose for local PostgreSQL and Redis
3. **Development**: `make dev` - Hot-reload FastAPI server
4. **Testing**: `make test` - Run test suite
5. **Quality**: `make lint` and `make format` - Code quality checks

### Code Organization
```
app/
├── api/           # API endpoints and routing
├── core/          # Configuration and core settings
├── db/            # Database session management
├── models/        # SQLModel database models
├── services/      # Business logic services
├── utils/         # Utility functions
└── worker.py      # Background task processing
```

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **MQTT Tests**: Message processing validation
- **Security Tests**: Authentication and authorization
- **Performance Tests**: Load testing for scalability

## Future Roadmap

### Phase 2 Features
- **Advanced Analytics**: Machine learning for anomaly detection
- **Device Firmware Management**: OTA updates and version control
- **Alert System**: Real-time notifications and escalation
- **Dashboard Customization**: User-configurable dashboards
- **API Rate Limiting**: Usage-based throttling

### Phase 3 Features
- **Multi-region Deployment**: Global data center distribution
- **Advanced Security**: Hardware security modules (HSM)
- **Compliance Certifications**: SOC 2, ISO 27001
- **Mobile Applications**: iOS and Android clients
- **Third-party Integrations**: Webhook support and API marketplace

## Business Metrics

### Key Performance Indicators
- **Device Uptime**: 99.9% availability target
- **Data Ingestion**: Support for 10,000+ devices per tenant
- **API Response Time**: <100ms for 95th percentile
- **User Adoption**: Target 1,000+ active tenants
- **Revenue Growth**: 20% month-over-month expansion

### Success Criteria
- **Technical**: Scalable, secure, and maintainable codebase
- **Business**: Reduced time-to-market for security integrations
- **User**: Intuitive interface with comprehensive device management
- **Operational**: Automated deployment and monitoring capabilities

---

*This workspace document serves as the single source of truth for understanding the SmartSecurity.Solutions Cloud project scope, architecture, and development context.* 