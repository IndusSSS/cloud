# app/models/user.py
"""
Enhanced User model for MESSS framework security implementation.

• Multi-Factor Authentication (MFA) support
• Advanced password security and breach detection
• Device tracking and session management
• Comprehensive audit logging capabilities
• Account security and recovery features
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field
from pydantic import EmailStr, validator
import json


class User(SQLModel, table=True):
    """Enhanced User model with comprehensive security features."""
    
    # Core identification
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True, index=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=50)
    email: EmailStr = Field(unique=True, index=True)
    
    # Password security
    hashed_password: str = Field()
    password_changed_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    password_history: Optional[str] = Field(default="[]")  # JSON array of previous hashes
    last_password_breach_check: Optional[datetime] = Field(default=None)
    
    # Account status and permissions
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    tenant_id: str = Field(index=True)
    
    # Multi-Factor Authentication (MFA)
    mfa_enabled: bool = Field(default=False)
    mfa_secret: Optional[str] = Field(default=None)  # TOTP secret
    mfa_backup_codes: Optional[str] = Field(default="[]")  # JSON array of backup codes
    mfa_setup_completed: bool = Field(default=False)
    
    # Contact verification
    phone_number: Optional[str] = Field(default=None, max_length=20)
    email_verified: bool = Field(default=False)
    phone_verified: bool = Field(default=False)
    email_verification_token: Optional[str] = Field(default=None)
    phone_verification_token: Optional[str] = Field(default=None)
    
    # Security and authentication
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = Field(default=None)
    last_login: Optional[datetime] = Field(default=None)
    last_login_ip: Optional[str] = Field(default=None)
    last_login_user_agent: Optional[str] = Field(default=None)
    
    # Account recovery
    security_questions: Optional[str] = Field(default="{}")  # JSON object
    recovery_email: Optional[EmailStr] = Field(default=None)
    account_recovery_token: Optional[str] = Field(default=None)
    recovery_token_expires: Optional[datetime] = Field(default=None)
    
    # Device and session management
    trusted_devices: Optional[str] = Field(default="[]")  # JSON array of device fingerprints
    max_concurrent_sessions: int = Field(default=5)
    session_timeout_minutes: int = Field(default=30)
    
    # Audit and compliance
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_security_review: Optional[datetime] = Field(default=None)
    
    # Additional security metadata
    security_preferences: Optional[str] = Field(default="{}")  # JSON object
    privacy_settings: Optional[str] = Field(default="{}")  # JSON object
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format and security."""
        if not v or len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        if not v.isalnum() and '_' not in v and '-' not in v:
            raise ValueError('Username can only contain alphanumeric characters, underscores, and hyphens')
        return v.lower()
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        if v is None:
            return v
        # Remove all non-digit characters
        digits_only = ''.join(filter(str.isdigit, v))
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError('Phone number must be between 10 and 15 digits')
        return v
    
    def is_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def is_password_expired(self, max_age_days: int = 90) -> bool:
        """Check if password has expired."""
        if self.password_changed_at is None:
            return True
        expiry_date = self.password_changed_at + timedelta(days=max_age_days)
        return datetime.utcnow() > expiry_date
    
    def get_password_history(self) -> List[str]:
        """Get password history as a list."""
        try:
            return json.loads(self.password_history or "[]")
        except (json.JSONDecodeError, TypeError):
            return []
    
    def add_password_to_history(self, hashed_password: str, max_history: int = 5):
        """Add password to history and maintain maximum size."""
        history = self.get_password_history()
        if hashed_password not in history:
            history.append(hashed_password)
            if len(history) > max_history:
                history = history[-max_history:]
            self.password_history = json.dumps(history)
    
    def is_password_in_history(self, hashed_password: str) -> bool:
        """Check if password exists in history."""
        return hashed_password in self.get_password_history()
    
    def get_mfa_backup_codes(self) -> List[str]:
        """Get MFA backup codes as a list."""
        try:
            return json.loads(self.mfa_backup_codes or "[]")
        except (json.JSONDecodeError, TypeError):
            return []
    
    def add_mfa_backup_code(self, code: str):
        """Add MFA backup code."""
        codes = self.get_mfa_backup_codes()
        if code not in codes:
            codes.append(code)
            self.mfa_backup_codes = json.dumps(codes)
    
    def remove_mfa_backup_code(self, code: str) -> bool:
        """Remove MFA backup code and return True if found."""
        codes = self.get_mfa_backup_codes()
        if code in codes:
            codes.remove(code)
            self.mfa_backup_codes = json.dumps(codes)
            return True
        return False
    
    def get_trusted_devices(self) -> List[Dict[str, Any]]:
        """Get trusted devices as a list of dictionaries."""
        try:
            return json.loads(self.trusted_devices or "[]")
        except (json.JSONDecodeError, TypeError):
            return []
    
    def add_trusted_device(self, device_info: Dict[str, Any]):
        """Add trusted device."""
        devices = self.get_trusted_devices()
        # Check if device already exists
        for device in devices:
            if device.get('fingerprint') == device_info.get('fingerprint'):
                device.update(device_info)
                device['last_used'] = datetime.utcnow().isoformat()
                self.trusted_devices = json.dumps(devices)
                return
        
        device_info['added_at'] = datetime.utcnow().isoformat()
        device_info['last_used'] = datetime.utcnow().isoformat()
        devices.append(device_info)
        self.trusted_devices = json.dumps(devices)
    
    def remove_trusted_device(self, device_fingerprint: str) -> bool:
        """Remove trusted device and return True if found."""
        devices = self.get_trusted_devices()
        for i, device in enumerate(devices):
            if device.get('fingerprint') == device_fingerprint:
                devices.pop(i)
                self.trusted_devices = json.dumps(devices)
                return True
        return False
    
    def get_security_preferences(self) -> Dict[str, Any]:
        """Get security preferences as a dictionary."""
        try:
            return json.loads(self.security_preferences or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def update_security_preferences(self, preferences: Dict[str, Any]):
        """Update security preferences."""
        current = self.get_security_preferences()
        current.update(preferences)
        self.security_preferences = json.dumps(current)
    
    def get_privacy_settings(self) -> Dict[str, Any]:
        """Get privacy settings as a dictionary."""
        try:
            return json.loads(self.privacy_settings or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def update_privacy_settings(self, settings: Dict[str, Any]):
        """Update privacy settings."""
        current = self.get_privacy_settings()
        current.update(settings)
        self.privacy_settings = json.dumps(current)
    
    def increment_failed_login_attempts(self):
        """Increment failed login attempts and handle lockout."""
        self.failed_login_attempts += 1
        
        # Progressive lockout: 5, 10, 15, 30, 60 minutes
        lockout_durations = [5, 10, 15, 30, 60]
        if self.failed_login_attempts <= len(lockout_durations):
            lockout_minutes = lockout_durations[self.failed_login_attempts - 1]
        else:
            lockout_minutes = 60  # Maximum 60 minutes
        
        self.locked_until = datetime.utcnow() + timedelta(minutes=lockout_minutes)
    
    def reset_failed_login_attempts(self):
        """Reset failed login attempts and unlock account."""
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def record_successful_login(self, ip_address: str, user_agent: str):
        """Record successful login information."""
        self.last_login = datetime.utcnow()
        self.last_login_ip = ip_address
        self.last_login_user_agent = user_agent
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def can_login(self) -> Dict[str, Any]:
        """Check if user can login and return status information."""
        if not self.is_active:
            return {
                "can_login": False,
                "reason": "Account is deactivated",
                "requires_action": "contact_admin"
            }
        
        if self.is_locked():
            if self.locked_until:
                remaining_time = self.locked_until - datetime.utcnow()
                remaining_minutes = int(remaining_time.total_seconds() / 60)
                return {
                    "can_login": False,
                    "reason": f"Account is locked for {remaining_minutes} minutes",
                    "requires_action": "wait",
                    "lockout_remaining_minutes": remaining_minutes
                }
            else:
                return {
                    "can_login": False,
                    "reason": "Account is locked",
                    "requires_action": "wait"
                }
        
        if self.is_password_expired():
            return {
                "can_login": False,
                "reason": "Password has expired",
                "requires_action": "change_password"
            }
        
        if self.mfa_enabled and not self.mfa_setup_completed:
            return {
                "can_login": False,
                "reason": "MFA setup required",
                "requires_action": "setup_mfa"
            }
        
        return {
            "can_login": True,
            "requires_mfa": self.mfa_enabled,
            "requires_email_verification": not self.email_verified
        }
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary, optionally including sensitive data."""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "is_verified": self.is_verified,
            "tenant_id": self.tenant_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "email_verified": self.email_verified,
            "phone_verified": self.phone_verified,
            "mfa_enabled": self.mfa_enabled,
            "mfa_setup_completed": self.mfa_setup_completed
        }
        
        if include_sensitive:
            data.update({
                "phone_number": self.phone_number,
                "failed_login_attempts": self.failed_login_attempts,
                "locked_until": self.locked_until.isoformat() if self.locked_until else None,
                "last_login_ip": self.last_login_ip,
                "last_login_user_agent": self.last_login_user_agent,
                "password_changed_at": self.password_changed_at.isoformat() if self.password_changed_at else None,
                "last_password_breach_check": self.last_password_breach_check.isoformat() if self.last_password_breach_check else None,
                "max_concurrent_sessions": self.max_concurrent_sessions,
                "session_timeout_minutes": self.session_timeout_minutes
            })
        
        return data


class UserSession(SQLModel, table=True):
    """User session tracking for security and audit purposes."""
    
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    session_token: str = Field(unique=True, index=True)
    refresh_token: str = Field(unique=True, index=True)
    
    # Device and location information
    device_fingerprint: str = Field(index=True)
    device_name: Optional[str] = Field(default=None)
    device_type: Optional[str] = Field(default=None)
    ip_address: str = Field()
    user_agent: str = Field()
    location_country: Optional[str] = Field(default=None)
    location_city: Optional[str] = Field(default=None)
    
    # Session management
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field()
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    # Security flags
    is_trusted: bool = Field(default=False)
    requires_mfa: bool = Field(default=False)
    mfa_verified: bool = Field(default=False)
    
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at
    
    def is_stale(self, max_idle_minutes: int = 30) -> bool:
        """Check if session is stale due to inactivity."""
        idle_time = datetime.utcnow() - self.last_activity
        return idle_time.total_seconds() > (max_idle_minutes * 60)
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "device_fingerprint": self.device_fingerprint,
            "device_name": self.device_name,
            "device_type": self.device_type,
            "ip_address": self.ip_address,
            "location_country": self.location_country,
            "location_city": self.location_city,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "is_active": self.is_active,
            "is_trusted": self.is_trusted,
            "requires_mfa": self.requires_mfa,
            "mfa_verified": self.mfa_verified
        }


class SecurityEvent(SQLModel, table=True):
    """Security event logging for audit and compliance."""
    
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)
    user_id: Optional[str] = Field(foreign_key="user.id", index=True)
    event_type: str = Field(index=True)  # login_success, login_failure, password_change, etc.
    severity: str = Field(index=True)  # low, medium, high, critical
    
    # Event details
    ip_address: str = Field()
    user_agent: str = Field()
    device_fingerprint: Optional[str] = Field(default=None)
    
    # Event metadata
    success: bool = Field(default=True)
    details: Optional[str] = Field(default=None)  # JSON string with additional details
    error_message: Optional[str] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = Field(default=None)
    resolved_by: Optional[str] = Field(default=None)
    
    # Risk assessment
    risk_score: Optional[float] = Field(default=None)  # 0.0 to 1.0
    risk_factors: Optional[str] = Field(default=None)  # JSON array of risk factors
    
    def get_details(self) -> Dict[str, Any]:
        """Get event details as a dictionary."""
        try:
            return json.loads(self.details or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_details(self, details: Dict[str, Any]):
        """Set event details from a dictionary."""
        self.details = json.dumps(details)
    
    def get_risk_factors(self) -> List[str]:
        """Get risk factors as a list."""
        try:
            return json.loads(self.risk_factors or "[]")
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_risk_factors(self, factors: List[str]):
        """Set risk factors from a list."""
        self.risk_factors = json.dumps(factors)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert security event to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_type": self.event_type,
            "severity": self.severity,
            "ip_address": self.ip_address,
            "device_fingerprint": self.device_fingerprint,
            "success": self.success,
            "details": self.get_details(),
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "risk_score": self.risk_score,
            "risk_factors": self.get_risk_factors()
        }
