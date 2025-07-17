# app/services/auth.py
"""
Enhanced authentication service for MESSS framework - Phase 1 Implementation.

• User authentication with rate limiting
• Password validation and breach detection
• Session management and device tracking
• Security audit logging
• Account lockout protection
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
import redis

from app.models.user import User, UserSession, SecurityEvent
from app.utils.security import (
    verify_password, 
    hash_password, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    validate_password_strength,
    check_password_breach,
    generate_device_fingerprint,
    sanitize_input,
    RateLimiter,
    SecurityAuditor
)
from app.core.config import settings


class AuthenticationService:
    """Enhanced authentication service with security features."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.rate_limiter = RateLimiter(redis_client)
        self.auditor = SecurityAuditor(redis_client)
    
    async def authenticate_user(
        self, 
        session: AsyncSession, 
        username: str, 
        password: str,
        ip_address: str,
        user_agent: str
    ) -> Tuple[Optional[User], Dict[str, Any]]:
        """
        Authenticate user with enhanced security checks.
        
        Returns:
            Tuple of (User object or None, authentication result dict)
        """
        # Sanitize inputs
        username = sanitize_input(username)
        ip_address = sanitize_input(ip_address)
        user_agent = sanitize_input(user_agent)
        
        # Check rate limiting
        rate_limit_key = f"login:{ip_address}"
        rate_limit_result = self.rate_limiter.check_rate_limit(
            rate_limit_key, 
            max_attempts=5, 
            window_seconds=900  # 15 minutes
        )
        
        if not rate_limit_result["allowed"]:
            self.auditor.log_security_event(
                event_type="login_rate_limited",
                user_id=None,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                details={"rate_limit_info": rate_limit_result},
                severity="medium"
            )
            return None, {
                "success": False,
                "error": "Too many login attempts. Please try again later.",
                "rate_limited": True,
                "reset_time": rate_limit_result["reset_time"]
            }
        
        # Find user
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        
        if not user:
            # Log failed login attempt
            self.rate_limiter.increment_failed_attempt(rate_limit_key, 900)
            self.auditor.log_security_event(
                event_type="login_failed",
                user_id=None,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                details={"username": username, "reason": "user_not_found"},
                severity="low"
            )
            return None, {
                "success": False,
                "error": "Incorrect username or password",
                "rate_limited": False
            }
        
        # Check if account is locked
        login_status = user.can_login()
        if not login_status["can_login"]:
            self.rate_limiter.increment_failed_attempt(rate_limit_key, 900)
            self.auditor.log_security_event(
                event_type="login_blocked",
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                details={"reason": login_status["reason"]},
                severity="medium"
            )
            return None, {
                "success": False,
                "error": login_status["reason"],
                "requires_action": login_status.get("requires_action"),
                "rate_limited": False
            }
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            # Increment failed attempts
            user.increment_failed_login_attempts()
            await session.commit()
            
            self.rate_limiter.increment_failed_attempt(rate_limit_key, 900)
            self.auditor.log_security_event(
                event_type="login_failed",
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                details={"username": username, "reason": "invalid_password"},
                severity="medium"
            )
            
            return None, {
                "success": False,
                "error": "Incorrect username or password",
                "rate_limited": False
            }
        
        # Check for password breach
        if check_password_breach(password):
            self.auditor.log_security_event(
                event_type="password_breach_detected",
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                details={"username": username},
                severity="high"
            )
            return None, {
                "success": False,
                "error": "Password has been compromised. Please change your password.",
                "requires_action": "change_password",
                "rate_limited": False
            }
        
        # Successful authentication
        user.record_successful_login(ip_address, user_agent)
        await session.commit()
        
        # Log successful login
        self.auditor.log_security_event(
            event_type="login_success",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            details={"username": username},
            severity="low"
        )
        
        return user, {
            "success": True,
            "user": user,
            "rate_limited": False
        }
    
    async def create_user_session(
        self,
        session: AsyncSession,
        user: User,
        ip_address: str,
        user_agent: str,
        device_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new user session with device tracking."""
        # Generate device fingerprint
        device_fingerprint = generate_device_fingerprint(user_agent, ip_address)
        
        # Check for existing sessions
        existing_sessions = await session.execute(
            select(UserSession).where(
                UserSession.user_id == user.id,
                UserSession.is_active == True
            )
        )
        active_sessions = existing_sessions.scalars().all()
        
        # Check concurrent session limit
        if len(active_sessions) >= user.max_concurrent_sessions:
            # Remove oldest session
            oldest_session = min(active_sessions, key=lambda s: s.created_at)
            oldest_session.is_active = False
            await session.commit()
        
        # Create new session
        access_token = create_access_token({"sub": user.id, "username": user.username})
        refresh_token = create_refresh_token({"sub": user.id, "username": user.username})
        
        user_session = UserSession(
            user_id=user.id,
            session_token=access_token,
            refresh_token=refresh_token,
            device_fingerprint=device_fingerprint,
            device_name=device_name or "Unknown Device",
            device_type=self._detect_device_type(user_agent),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(minutes=user.session_timeout_minutes),
            requires_mfa=user.mfa_enabled,
            mfa_verified=not user.mfa_enabled  # Skip MFA if not enabled
        )
        
        session.add(user_session)
        await session.commit()
        await session.refresh(user_session)
        
        # Add device to trusted devices if not already present
        device_info = {
            "fingerprint": device_fingerprint,
            "name": device_name or "Unknown Device",
            "type": self._detect_device_type(user_agent),
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        user.add_trusted_device(device_info)
        await session.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": user.session_timeout_minutes * 60,
            "session_id": user_session.id,
            "device_fingerprint": device_fingerprint,
            "requires_mfa": user.mfa_enabled
        }
    
    async def validate_session(
        self,
        session: AsyncSession,
        access_token: str,
        ip_address: str,
        user_agent: str
    ) -> Optional[User]:
        """Validate user session and return user if valid."""
        # Verify token
        payload = verify_token(access_token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Find user
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            return None
        
        # Find session
        result = await session.execute(
            select(UserSession).where(
                UserSession.session_token == access_token,
                UserSession.is_active == True
            )
        )
        user_session = result.scalar_one_or_none()
        
        if not user_session or user_session.is_expired():
            return None
        
        # Update session activity
        user_session.update_activity()
        await session.commit()
        
        return user
    
    async def logout_user(
        self,
        session: AsyncSession,
        access_token: str,
        ip_address: str,
        user_agent: str
    ) -> bool:
        """Logout user and invalidate session."""
        # Find and deactivate session
        result = await session.execute(
            select(UserSession).where(UserSession.session_token == access_token)
        )
        user_session = result.scalar_one_or_none()
        
        if user_session:
            user_session.is_active = False
            await session.commit()
            
            # Log logout event
            self.auditor.log_security_event(
                event_type="logout",
                user_id=user_session.user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=True,
                details={"session_id": user_session.id},
                severity="low"
            )
            
            return True
        
        return False
    
    async def logout_all_sessions(
        self,
        session: AsyncSession,
        user_id: str,
        ip_address: str,
        user_agent: str
    ) -> int:
        """Logout all sessions for a user."""
        result = await session.execute(
            select(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        )
        active_sessions = result.scalars().all()
        
        for user_session in active_sessions:
            user_session.is_active = False
        
        await session.commit()
        
        # Log event
        self.auditor.log_security_event(
            event_type="logout_all_sessions",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            details={"sessions_terminated": len(active_sessions)},
            severity="medium"
        )
        
        return len(active_sessions)
    
    async def change_password(
        self,
        session: AsyncSession,
        user: User,
        current_password: str,
        new_password: str,
        ip_address: str,
        user_agent: str
    ) -> Dict[str, Any]:
        """Change user password with validation."""
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            self.auditor.log_security_event(
                event_type="password_change_failed",
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                details={"reason": "invalid_current_password"},
                severity="medium"
            )
            return {
                "success": False,
                "error": "Current password is incorrect"
            }
        
        # Validate new password strength
        password_validation = validate_password_strength(new_password)
        if not password_validation["valid"]:
            self.auditor.log_security_event(
                event_type="password_change_failed",
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                details={"reason": "weak_password", "issues": password_validation["issues"]},
                severity="medium"
            )
            return {
                "success": False,
                "error": "Password does not meet security requirements",
                "issues": password_validation["issues"],
                "suggestions": password_validation["suggestions"]
            }
        
        # Check if password is in history
        new_password_hash = hash_password(new_password)
        if user.is_password_in_history(new_password_hash):
            self.auditor.log_security_event(
                event_type="password_change_failed",
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                details={"reason": "password_in_history"},
                severity="medium"
            )
            return {
                "success": False,
                "error": "Password has been used recently. Please choose a different password."
            }
        
        # Check for breach
        if check_password_breach(new_password):
            self.auditor.log_security_event(
                event_type="password_change_failed",
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                details={"reason": "password_breach_detected"},
                severity="high"
            )
            return {
                "success": False,
                "error": "Password has been compromised. Please choose a different password."
            }
        
        # Update password
        old_password_hash = user.hashed_password
        user.hashed_password = new_password_hash
        user.password_changed_at = datetime.utcnow()
        user.add_password_to_history(old_password_hash)
        
        await session.commit()
        
        # Log successful password change
        self.auditor.log_security_event(
            event_type="password_change_success",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            details={"password_strength": password_validation["strength"]},
            severity="medium"
        )
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
    
    def _detect_device_type(self, user_agent: str) -> str:
        """Detect device type from user agent."""
        user_agent_lower = user_agent.lower()
        
        if "mobile" in user_agent_lower or "android" in user_agent_lower or "iphone" in user_agent_lower:
            return "mobile"
        elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
            return "tablet"
        elif "desktop" in user_agent_lower or "windows" in user_agent_lower or "macintosh" in user_agent_lower:
            return "desktop"
        else:
            return "unknown"


# Legacy functions for backward compatibility
async def authenticate_user(session: AsyncSession, username: str, password: str) -> Optional[User]:
    """Legacy authentication function for backward compatibility."""
    # This is a simplified version - in production, use AuthenticationService
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.hashed_password):
        return None
    
    if not user.is_active:
        return None
    
    # Update last login
    user.last_login = datetime.utcnow()
    session.add(user)
    await session.commit()
    
    return user


async def create_user(
    session: AsyncSession, 
    username: str, 
    email: str, 
    password: str,
    tenant_id: str,
    is_admin: bool = False
) -> User:
    """Create a new user account with enhanced security."""
    # Validate password strength
    password_validation = validate_password_strength(password)
    if not password_validation["valid"]:
        raise ValueError(f"Password does not meet security requirements: {', '.join(password_validation['issues'])}")
    
    # Check for breach
    if check_password_breach(password):
        raise ValueError("Password has been compromised. Please choose a different password.")
    
    hashed_password = hash_password(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        tenant_id=tenant_id,
        is_admin=is_admin,
        password_changed_at=datetime.utcnow()
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


def create_user_token(user: User) -> str:
    """Create an access token for a user."""
    token_data = {"sub": str(user.id), "username": user.username}
    return create_access_token(data=token_data)