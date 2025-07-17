# SmartSecurity Cloud

Enterprise-grade IoT security management platform built on the MESSS framework.

## 🚀 30-Second Elevator Pitch

SmartSecurity Cloud is a comprehensive IoT security platform that provides real-time device monitoring, threat detection, and automated incident response. Built with security-first principles using the MESSS framework (Modular, Efficient, Secure, Scalable, Stable), it offers enterprise-grade protection for IoT ecosystems with advanced authentication, device fingerprinting, and AI-powered threat detection.

**Key Features:**
- 🔐 **Advanced Security**: JWT authentication, Argon2 password hashing, rate limiting
- 📱 **Device Management**: Real-time IoT device monitoring and control
- 🛡️ **Threat Detection**: AI-powered anomaly detection and behavioral analysis
- 📊 **Analytics**: Comprehensive security analytics and reporting
- 🏢 **Enterprise Ready**: Multi-tenant architecture with RBAC

## ⚡ Quick Start

```bash
# Clone and setup (≤3 lines)
git clone https://github.com/your-org/smartsecurity-cloud.git && cd smartsecurity-cloud
poetry install && poetry shell
docker compose up -d
```

**Access the platform:**
- 🌐 **API Documentation**: http://localhost:8000/docs
- 👥 **Admin Panel**: http://localhost:3000
- 🏠 **Customer Portal**: http://localhost:3001
- 💚 **Health Check**: http://localhost:8000/health

## 🏗️ Architecture

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
```

## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure stateless authentication
- **Argon2 Hashing**: Industry-standard password security
- **Rate Limiting**: Protection against brute force attacks
- **Device Fingerprinting**: Anomaly detection for suspicious logins
- **RBAC**: Role-based access control

### Threat Protection
- **Input Validation**: XSS and injection attack prevention
- **Session Management**: Secure session lifecycle
- **Audit Logging**: Comprehensive security event tracking
- **HTTPS Only**: Encrypted communications
- **Security Headers**: Modern web security standards

## 🛠️ Development

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- Poetry (Python dependency management)
- Node.js 18+ (for frontend development)

### Development Setup
```bash
# Install dependencies
poetry install
poetry shell

# Start services
docker compose up -d

# Run database migrations
poetry run alembic upgrade head

# Start development server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run security tests
poetry run python test_security_runner.py

# Run with coverage
poetry run pytest --cov=app
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

## 📚 Documentation

- [🏗️ Architecture](./docs/ARCHITECTURE.md) - System design and data flow
- [🔧 Development Setup](./docs/DEV_SETUP.md) - Complete setup guide
- [🎨 Style Guide](./docs/STYLE_GUIDE.md) - Coding conventions
- [🔒 Security](./docs/SECURITY.md) - Security implementation
- [📋 MESS Guidelines](./docs/MESS_GUIDELINES.md) - Development framework
- [🤝 Contributing](./docs/CONTRIBUTING.md) - How to contribute
- [🗺️ Roadmap](./docs/ROADMAP.md) - Development phases
- [📝 Changelog](./docs/CHANGELOG.md) - Version history

## 🚀 Deployment

### Production Deployment
```bash
# Build and deploy
docker compose -f docker-compose.prod.yml up -d

# Setup SSL certificates
./setup_ssl_letsencrypt.sh

# Configure environment
cp .env.example .env.prod
# Edit .env.prod with production values
```

### Environment Variables
```bash
# Required
SECRET_KEY=your-256-bit-secret-key
JWT_SECRET_KEY=your-256-bit-jwt-secret
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379

# Optional
ENCRYPTION_KEY=your-encryption-key
API_KEY=your-api-key
```

## 🔧 Configuration

### Security Settings
```python
# Security configuration
SECURITY_SETTINGS = {
    "password_min_length": 12,
    "password_expiry_days": 90,
    "max_login_attempts": 5,
    "session_timeout_minutes": 30,
    "rate_limit_window": 900,  # 15 minutes
}
```

### Rate Limiting
- **Login Attempts**: 5 per 15 minutes per IP
- **API Requests**: 100 per minute per user
- **Password Reset**: 3 per hour per email
- **Registration**: 10 per hour per IP

## 📊 Monitoring

### Health Checks
- **API Health**: `/health` endpoint
- **Database**: Connection pool monitoring
- **Redis**: Cache hit/miss ratio
- **MQTT**: Broker connection status

### Metrics
- **Response Times**: P50, P95, P99 latencies
- **Error Rates**: 4xx and 5xx error percentages
- **Security Events**: Failed logins, rate limit hits
- **Business Metrics**: User activity, device connections

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./docs/CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the [MESS Guidelines](./docs/MESS_GUIDELINES.md)
4. Write tests for new functionality
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](./docs/) directory
- **Issues**: [GitHub Issues](https://github.com/your-org/smartsecurity-cloud/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/smartsecurity-cloud/discussions)
- **Security**: [Security Policy](SECURITY.md)

## 🏆 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for high-performance APIs
- Powered by [Vue.js](https://vuejs.org/) for reactive frontend
- Secured with [Argon2](https://argon2.online/) for password hashing
- Monitored with [Prometheus](https://prometheus.io/) and [Grafana](https://grafana.com/)

---

**SmartSecurity Cloud** - Enterprise IoT Security, Simplified.