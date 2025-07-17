# Architecture

High-level system architecture and data flow for the SmartSecurity Cloud platform built on the MESSS framework.

## System Overview

The SmartSecurity Cloud platform is a modular, microservices-based IoT security management system designed for enterprise-grade device monitoring and threat detection.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Admin Panel   │    │   Customer      │
│   (Vue.js)      │    │   (Vue.js)      │    │   Portal        │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      Nginx Proxy          │
                    │   (SSL Termination)       │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    FastAPI Backend        │
                    │   (MESSS Framework)       │
                    └─────────────┬─────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
┌─────────▼─────────┐  ┌─────────▼─────────┐  ┌─────────▼─────────┐
│   PostgreSQL      │  │     Redis         │  │    Mosquitto      │
│   (Primary DB)    │  │   (Cache/Sessions)│  │   (MQTT Broker)   │
└───────────────────┘  └───────────────────┘  └───────────────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    IoT Devices            │
                    │   (Sensors, Cameras)      │
                    └───────────────────────────┘
```

## Core Components

### 1. Frontend Layer
- **Customer Portal**: Vue.js SPA for device management and monitoring
- **Admin Panel**: Vue.js SPA for system administration and analytics
- **Responsive Design**: Tailwind CSS for modern, mobile-friendly UI

### 2. API Gateway
- **Nginx**: SSL termination, load balancing, and request routing
- **Rate Limiting**: Built-in protection against abuse
- **CORS**: Cross-origin resource sharing configuration

### 3. Backend Services (MESSS Framework)
- **FastAPI**: High-performance async API framework
- **Authentication**: JWT-based with Argon2 password hashing
- **Authorization**: Role-based access control (RBAC)
- **Rate Limiting**: Redis-based request throttling
- **Session Management**: Secure session tracking with device fingerprinting
- **Audit Logging**: Comprehensive security event tracking

### 4. Data Layer
- **PostgreSQL**: Primary database for user data, devices, and analytics
- **Redis**: Caching, session storage, and rate limiting
- **SQLModel**: Modern ORM with Pydantic integration

### 5. IoT Integration
- **Mosquitto**: MQTT broker for real-time device communication
- **Device Management**: Secure device registration and monitoring
- **Data Ingestion**: Real-time sensor data processing

## Data Flow

### Authentication Flow
1. User submits credentials via frontend
2. FastAPI validates credentials against PostgreSQL
3. Rate limiting checked via Redis
4. JWT tokens generated and returned
5. Session created and stored in Redis
6. Security event logged for audit trail

### Device Data Flow
1. IoT device publishes data to Mosquitto MQTT broker
2. FastAPI MQTT client receives and validates data
3. Data processed and stored in PostgreSQL
4. Real-time updates pushed to connected frontend clients
5. Analytics updated for dashboard display

### Admin Operations Flow
1. Admin authenticates with elevated privileges
2. RBAC system validates permissions
3. Operations performed with full audit logging
4. Changes propagated to affected systems
5. Notifications sent to relevant users

## Security Architecture

### Multi-Layer Security
- **Network**: SSL/TLS encryption for all communications
- **Application**: Input validation, SQL injection prevention
- **Authentication**: Argon2 password hashing, JWT tokens
- **Authorization**: Role-based access control
- **Audit**: Comprehensive logging of all security events

### Threat Protection
- **Rate Limiting**: Prevents brute force attacks
- **Input Sanitization**: XSS and injection attack prevention
- **Device Fingerprinting**: Anomaly detection for suspicious logins
- **Session Management**: Secure session lifecycle management

## Scalability Design

### Horizontal Scaling
- **Stateless API**: FastAPI instances can be scaled horizontally
- **Database**: PostgreSQL with connection pooling
- **Cache**: Redis cluster for high availability
- **Load Balancer**: Nginx for request distribution

### Performance Optimization
- **Async Operations**: Non-blocking I/O throughout the stack
- **Caching**: Redis for frequently accessed data
- **Database Indexing**: Optimized queries for large datasets
- **CDN**: Static asset delivery optimization

## Deployment Architecture

### Containerization
- **Docker**: All services containerized for consistency
- **Docker Compose**: Local development and testing
- **Production**: Kubernetes-ready configuration

### Environment Management
- **Development**: Local Docker Compose setup
- **Staging**: Production-like environment for testing
- **Production**: VPS deployment with SSL certificates

## Monitoring and Observability

### Health Checks
- **API Health**: `/health` endpoint for service status
- **Database**: Connection pool monitoring
- **Redis**: Cache hit/miss ratio tracking
- **MQTT**: Broker connection status

### Logging
- **Structured Logging**: JSON format for easy parsing
- **Security Events**: Comprehensive audit trail
- **Performance Metrics**: Response time and throughput
- **Error Tracking**: Detailed error reporting and alerting

## Future Architecture Considerations

### Microservices Evolution
- **Service Decomposition**: Breaking monolith into focused services
- **API Gateway**: Enhanced routing and transformation
- **Service Mesh**: Inter-service communication management
- **Event Sourcing**: Event-driven architecture for scalability

### Cloud Native Features
- **Auto-scaling**: Dynamic resource allocation
- **Service Discovery**: Dynamic service registration
- **Configuration Management**: Centralized configuration
- **Secrets Management**: Secure credential handling 