# Security

Threat model, secret-handling rules, and security implementation guidelines for the SmartSecurity Cloud platform.

## Threat Model

### Attack Vectors

#### 1. Authentication Attacks
- **Brute Force**: Automated password guessing
- **Credential Stuffing**: Using leaked credentials
- **Session Hijacking**: Stealing valid session tokens
- **Account Enumeration**: Discovering valid usernames

#### 2. Authorization Attacks
- **Privilege Escalation**: Gaining unauthorized access
- **Horizontal Privilege Escalation**: Accessing other users' data
- **Vertical Privilege Escalation**: Gaining admin privileges

#### 3. Data Attacks
- **SQL Injection**: Malicious database queries
- **XSS (Cross-Site Scripting)**: Client-side code injection
- **CSRF (Cross-Site Request Forgery)**: Unauthorized actions
- **Data Exfiltration**: Unauthorized data access

#### 4. Infrastructure Attacks
- **DDoS**: Denial of service attacks
- **Man-in-the-Middle**: Intercepting communications
- **Supply Chain**: Compromised dependencies
- **Social Engineering**: Human manipulation

### Risk Assessment

#### High Risk
- **Authentication Bypass**: Complete system compromise
- **Data Breach**: Sensitive information exposure
- **Admin Access**: Full system control
- **Financial Impact**: Direct monetary loss

#### Medium Risk
- **User Data Access**: Privacy violation
- **Service Disruption**: Availability impact
- **Reputation Damage**: Trust erosion
- **Compliance Violation**: Regulatory issues

#### Low Risk
- **Information Disclosure**: Non-sensitive data
- **Performance Impact**: Service degradation
- **Log Pollution**: Monitoring interference

## Security Implementation

### Authentication Security

#### Password Security
```python
# Argon2 password hashing with secure parameters
pwd_context = CryptContext(
    schemes=["argon2"],
    default="argon2",
    argon2__memory_cost=65536,  # 64MB
    argon2__time_cost=3,        # 3 iterations
    argon2__parallelism=4       # 4 parallel threads
)

def hash_password(password: str) -> str:
    """Hash password using Argon2 with secure parameters."""
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against Argon2 hash."""
    return pwd_context.verify(password, hashed)
```

#### Password Policy
- **Minimum Length**: 12 characters
- **Complexity**: Uppercase, lowercase, numbers, symbols
- **History**: Prevent reuse of last 5 passwords
- **Expiration**: 90 days maximum
- **Breach Detection**: Check against known compromised passwords

#### Multi-Factor Authentication
```python
# TOTP-based MFA implementation
def generate_mfa_secret() -> str:
    """Generate secure MFA secret."""
    return pyotp.random_base32()

def verify_mfa_code(secret: str, code: str) -> bool:
    """Verify TOTP code."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)
```

### JWT Security

#### Token Configuration
```python
# JWT token security settings
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # 256-bit minimum

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create secure JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": "SmartSecurity Cloud",
        "aud": "SmartSecurity Users",
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt
```

#### Token Validation
```python
def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token with comprehensive checks."""
    try:
        payload = jwt.decode(
            token, 
            JWT_SECRET_KEY, 
            algorithms=[JWT_ALGORITHM],
            issuer="SmartSecurity Cloud",
            audience="SmartSecurity Users"
        )
        
        # Additional security checks
        if payload.get("type") not in ["access", "refresh"]:
            return None
            
        if payload.get("exp") < datetime.utcnow().timestamp():
            return None
            
        return payload
    except jwt.PyJWTError:
        return None
```

### Rate Limiting

#### Implementation
```python
class RateLimiter:
    """Redis-based rate limiter with sliding window."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def check_rate_limit(self, key: str, max_attempts: int, window: int) -> dict:
        """Check rate limit for given key."""
        now = datetime.utcnow().timestamp()
        
        # Remove expired entries
        await self.redis.zremrangebyscore(key, 0, now - window)
        
        # Count current attempts
        attempts = await self.redis.zcard(key)
        
        if attempts >= max_attempts:
            return {
                "allowed": False,
                "remaining": 0,
                "attempts": attempts,
                "reset_time": now + window
            }
        
        # Add current attempt
        await self.redis.zadd(key, {str(now): now})
        await self.redis.expire(key, window)
        
        return {
            "allowed": True,
            "remaining": max_attempts - attempts - 1,
            "attempts": attempts + 1
        }
```

#### Rate Limit Configuration
- **Login Attempts**: 5 per 15 minutes per IP
- **API Requests**: 100 per minute per user
- **Password Reset**: 3 per hour per email
- **Registration**: 10 per hour per IP

### Input Validation & Sanitization

#### XSS Prevention
```python
def sanitize_input(input_string: str) -> str:
    """Sanitize input to prevent XSS attacks."""
    if not input_string:
        return ""
    
    # Remove dangerous HTML tags
    dangerous_tags = [
        "<script>", "</script>", "<iframe>", "</iframe>",
        "<object>", "</object>", "<embed>", "</embed>"
    ]
    
    sanitized = input_string
    for tag in dangerous_tags:
        sanitized = sanitized.replace(tag, "")
    
    # Remove dangerous attributes
    dangerous_attributes = [
        "onload=", "onerror=", "onclick=", "onmouseover=",
        "javascript:", "vbscript:", "data:"
    ]
    
    for attr in dangerous_attributes:
        sanitized = sanitized.replace(attr, "")
    
    return sanitized.strip()
```

#### SQL Injection Prevention
```python
# Use parameterized queries with SQLModel
async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
    """Get user by username using parameterized query."""
    query = select(User).where(User.username == username)
    result = await session.execute(query)
    return result.scalar_one_or_none()

# ❌ Bad: String concatenation (vulnerable to SQL injection)
# query = f"SELECT * FROM users WHERE username = '{username}'"
```

### Session Management

#### Session Security
```python
class UserSession(SQLModel, table=True):
    """Secure user session model."""
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    session_token: str = Field(unique=True, index=True)
    refresh_token: str = Field(unique=True, index=True)
    device_fingerprint: str = Field(index=True)
    ip_address: str
    user_agent: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
```

#### Device Fingerprinting
```python
def generate_device_fingerprint(user_agent: str, ip_address: str) -> str:
    """Generate unique device fingerprint."""
    # Combine user agent and IP for fingerprinting
    fingerprint_data = f"{user_agent}:{ip_address}"
    
    # Generate SHA-256 hash
    fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    return fingerprint[:32]  # Return first 32 characters
```

## Secret Management

### Environment Variables
```bash
# Required environment variables
SECRET_KEY=your-256-bit-secret-key-here
JWT_SECRET_KEY=your-256-bit-jwt-secret-here
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
MQTT_PASSWORD=your-mqtt-password-here

# Optional but recommended
ENCRYPTION_KEY=your-encryption-key-here
API_KEY=your-api-key-here
```

### Secret Generation
```python
# Generate secure secrets
import secrets
import base64

def generate_secret_key(length: int = 32) -> str:
    """Generate cryptographically secure secret key."""
    return base64.b64encode(secrets.token_bytes(length)).decode()

def generate_jwt_secret() -> str:
    """Generate JWT secret key."""
    return generate_secret_key(32)

def generate_encryption_key() -> str:
    """Generate encryption key."""
    return generate_secret_key(32)
```

### Secret Storage
- **Development**: `.env` file (never commit to version control)
- **Production**: Environment variables or secret management service
- **Docker**: Use Docker secrets or environment files
- **Kubernetes**: Use Kubernetes secrets

### Secret Rotation
```python
class SecretManager:
    """Manage secret rotation and validation."""
    
    def __init__(self):
        self.current_secret = os.getenv("SECRET_KEY")
        self.backup_secret = os.getenv("SECRET_KEY_BACKUP")
    
    def rotate_secrets(self):
        """Rotate secrets and update environment."""
        # Generate new secrets
        new_secret = generate_secret_key()
        new_jwt_secret = generate_jwt_secret()
        
        # Update environment (implementation depends on deployment)
        os.environ["SECRET_KEY"] = new_secret
        os.environ["JWT_SECRET_KEY"] = new_jwt_secret
        
        # Invalidate existing sessions
        self.invalidate_all_sessions()
```

## Audit Logging

### Security Event Logging
```python
class SecurityAuditor:
    """Comprehensive security event logging."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def log_security_event(
        self,
        event_type: str,
        user_id: Optional[str],
        ip_address: str,
        user_agent: str,
        success: bool,
        details: Optional[dict] = None,
        severity: str = "medium"
    ):
        """Log security event with comprehensive details."""
        event = {
            "id": str(uuid.uuid4()),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "success": success,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        
        # Store in Redis for real-time access
        await self.redis.setex(
            f"security_event:{event['id']}", 
            86400,  # 24 hours
            json.dumps(event)
        )
        
        # Add to event list
        await self.redis.lpush("security_events", event["id"])
        await self.redis.ltrim("security_events", 0, 9999)  # Keep last 10k events
```

### Event Types
- **login_success**: Successful authentication
- **login_failure**: Failed authentication
- **logout**: User logout
- **password_change**: Password modification
- **account_lockout**: Account locked due to failed attempts
- **suspicious_activity**: Unusual behavior detected
- **admin_action**: Administrative operations
- **data_access**: Sensitive data access

## Security Headers

### HTTP Security Headers
```python
# FastAPI security middleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# Security headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response
```

### CORS Configuration
```python
# Secure CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"]
)
```

## Compliance & Standards

### OWASP Top 10 Compliance
1. **Broken Access Control**: Implement proper authorization
2. **Cryptographic Failures**: Use strong encryption
3. **Injection**: Parameterized queries and input validation
4. **Insecure Design**: Security by design principles
5. **Security Misconfiguration**: Secure defaults
6. **Vulnerable Components**: Regular dependency updates
7. **Authentication Failures**: Multi-factor authentication
8. **Software and Data Integrity**: Secure CI/CD pipeline
9. **Security Logging**: Comprehensive audit logging
10. **Server-Side Request Forgery**: Input validation

### GDPR Compliance
- **Data Minimization**: Only collect necessary data
- **Consent Management**: Explicit user consent
- **Right to Erasure**: Data deletion capabilities
- **Data Portability**: Export user data
- **Privacy by Design**: Built-in privacy protection

### SOC 2 Compliance
- **Security**: Protect against unauthorized access
- **Availability**: Ensure system availability
- **Processing Integrity**: Accurate data processing
- **Confidentiality**: Protect sensitive information
- **Privacy**: Protect personal information

## Security Testing

### Automated Security Tests
```python
# Security test examples
class TestSecurityFeatures:
    """Test security implementations."""
    
    def test_password_hashing(self):
        """Test password hashing security."""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        # Verify hash is different from original
        assert hashed != password
        assert len(hashed) > 50  # Argon2 hashes are long
        
        # Verify password
        assert verify_password(password, hashed) == True
        assert verify_password("WrongPassword", hashed) == False
    
    def test_jwt_token_security(self):
        """Test JWT token security."""
        user_data = {"sub": "user123", "username": "testuser"}
        token = create_access_token(user_data)
        
        # Verify token
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["iss"] == "SmartSecurity Cloud"
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        rate_limiter = RateLimiter(mock_redis)
        
        # Test rate limit enforcement
        for i in range(5):
            result = rate_limiter.check_rate_limit("test:key", 5, 900)
            if i < 4:
                assert result["allowed"] == True
            else:
                assert result["allowed"] == False
```

### Penetration Testing
- **Authentication Testing**: Test login bypass attempts
- **Authorization Testing**: Test privilege escalation
- **Input Validation**: Test injection attacks
- **Session Management**: Test session hijacking
- **API Security**: Test API endpoint security

## Incident Response

### Security Incident Procedures
1. **Detection**: Automated monitoring and alerting
2. **Assessment**: Evaluate impact and scope
3. **Containment**: Isolate affected systems
4. **Eradication**: Remove threat and vulnerabilities
5. **Recovery**: Restore normal operations
6. **Lessons Learned**: Document and improve

### Security Monitoring
```python
# Security monitoring setup
class SecurityMonitor:
    """Monitor security events and trigger alerts."""
    
    def __init__(self):
        self.alert_thresholds = {
            "failed_logins": 10,  # Per hour
            "suspicious_ips": 5,  # Per hour
            "admin_actions": 50,  # Per hour
        }
    
    async def check_security_alerts(self):
        """Check for security alert conditions."""
        # Monitor failed login attempts
        failed_logins = await self.get_failed_logins_count(hours=1)
        if failed_logins > self.alert_thresholds["failed_logins"]:
            await self.send_alert("High failed login attempts detected")
        
        # Monitor suspicious IP addresses
        suspicious_ips = await self.get_suspicious_ips_count(hours=1)
        if suspicious_ips > self.alert_thresholds["suspicious_ips"]:
            await self.send_alert("Suspicious IP activity detected")
```

## Security Checklist

### Development Checklist
- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Secure authentication
- [ ] Proper authorization
- [ ] Rate limiting
- [ ] Audit logging
- [ ] Error handling
- [ ] Security headers

### Deployment Checklist
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Environment variables secured
- [ ] Database access restricted
- [ ] Firewall configured
- [ ] Monitoring enabled
- [ ] Backup procedures
- [ ] Incident response plan
- [ ] Security testing completed
- [ ] Compliance verified 