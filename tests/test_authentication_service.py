# tests/test_authentication_service.py
"""
Comprehensive tests for AuthenticationService - MESSS framework.

• User authentication with rate limiting
• Session management and device tracking
• Password change functionality
• Security audit logging
• Error handling and edge cases
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import json

from app.services.auth import AuthenticationService
from app.models.user import User, UserSession
from app.utils.security import hash_password, validate_password_strength


class TestAuthenticationService:
    """Test AuthenticationService functionality."""
    
    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        mock_redis = Mock()
        mock_redis.pipeline.return_value.execute.return_value = [0, 0, 0, True]  # No attempts
        return mock_redis
    
    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.add = AsyncMock()
        mock_session.refresh = AsyncMock()
        return mock_session
    
    @pytest.fixture
    def auth_service(self, mock_redis):
        """Create AuthenticationService instance."""
        return AuthenticationService(mock_redis)
    
    @pytest.fixture
    def test_user(self):
        """Create test user."""
        return User(
            id="user123",
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("SecurePass123!"),
            tenant_id="tenant123",
            is_active=True,
            is_admin=False
        )
    
    @pytest.mark.asyncio
    async def test_successful_authentication(self, auth_service, mock_session, test_user):
        """Test successful user authentication."""
        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_session.execute.return_value = mock_result
        
        # Test authentication
        user, result = await auth_service.authenticate_user(
            mock_session, "testuser", "SecurePass123!", "192.168.1.100", "Mozilla/5.0"
        )
        
        # Verify results
        assert result["success"] == True
        assert user is not None
        assert user.username == "testuser"
        assert result["rate_limited"] == False
        
        # Verify user was updated
        assert user.last_login is not None
        assert user.last_login_ip == "192.168.1.100"
        assert user.last_login_user_agent == "Mozilla/5.0"
        assert user.failed_login_attempts == 0
        assert user.locked_until is None
    
    @pytest.mark.asyncio
    async def test_failed_authentication_wrong_password(self, auth_service, mock_session, test_user):
        """Test authentication with wrong password."""
        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_session.execute.return_value = mock_result
        
        # Test authentication with wrong password
        user, result = await auth_service.authenticate_user(
            mock_session, "testuser", "WrongPassword", "192.168.1.100", "Mozilla/5.0"
        )
        
        # Verify results
        assert result["success"] == False
        assert user is None
        assert "Incorrect username or password" in result["error"]
        assert result["rate_limited"] == False
        
        # Verify failed attempts were incremented
        assert test_user.failed_login_attempts == 1
        assert test_user.is_locked() == True
    
    @pytest.mark.asyncio
    async def test_failed_authentication_user_not_found(self, auth_service, mock_session):
        """Test authentication with non-existent user."""
        # Mock database query - user not found
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Test authentication
        user, result = await auth_service.authenticate_user(
            mock_session, "nonexistent", "password", "192.168.1.100", "Mozilla/5.0"
        )
        
        # Verify results
        assert result["success"] == False
        assert user is None
        assert "Incorrect username or password" in result["error"]
        assert result["rate_limited"] == False
    
    @pytest.mark.asyncio
    async def test_rate_limited_authentication(self, auth_service, mock_session):
        """Test rate limited authentication."""
        # Mock rate limiting - exceeded
        mock_redis = auth_service.redis
        mock_redis.pipeline.return_value.execute.return_value = [0, 0, 5, True]  # 5 attempts
        
        # Test authentication
        user, result = await auth_service.authenticate_user(
            mock_session, "testuser", "password", "192.168.1.100", "Mozilla/5.0"
        )
        
        # Verify results
        assert result["success"] == False
        assert user is None
        assert result["rate_limited"] == True
        assert "Too many login attempts" in result["error"]
        assert "reset_time" in result
    
    @pytest.mark.asyncio
    async def test_locked_account_authentication(self, auth_service, mock_session, test_user):
        """Test authentication with locked account."""
        # Lock the account
        test_user.increment_failed_login_attempts()
        
        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_session.execute.return_value = mock_result
        
        # Test authentication
        user, result = await auth_service.authenticate_user(
            mock_session, "testuser", "SecurePass123!", "192.168.1.100", "Mozilla/5.0"
        )
        
        # Verify results
        assert result["success"] == False
        assert user is None
        assert "locked" in result["error"]
        assert result["requires_action"] == "wait"
    
    @pytest.mark.asyncio
    async def test_inactive_account_authentication(self, auth_service, mock_session, test_user):
        """Test authentication with inactive account."""
        # Deactivate account
        test_user.is_active = False
        
        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_session.execute.return_value = mock_result
        
        # Test authentication
        user, result = await auth_service.authenticate_user(
            mock_session, "testuser", "SecurePass123!", "192.168.1.100", "Mozilla/5.0"
        )
        
        # Verify results
        assert result["success"] == False
        assert user is None
        assert "deactivated" in result["error"]
        assert result["requires_action"] == "contact_admin"
    
    @pytest.mark.asyncio
    async def test_password_breach_detection(self, auth_service, mock_session, test_user):
        """Test authentication with breached password."""
        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_session.execute.return_value = mock_result
        
        # Test authentication with breached password
        user, result = await auth_service.authenticate_user(
            mock_session, "testuser", "password", "192.168.1.100", "Mozilla/5.0"
        )
        
        # Verify results
        assert result["success"] == False
        assert user is None
        assert "compromised" in result["error"]
        assert result["requires_action"] == "change_password"
    
    @pytest.mark.asyncio
    async def test_create_user_session(self, auth_service, mock_session, test_user):
        """Test user session creation."""
        # Mock database queries
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []  # No existing sessions
        mock_session.execute.return_value = mock_result
        
        # Create session
        session_data = await auth_service.create_user_session(
            mock_session, test_user, "192.168.1.100", "Mozilla/5.0", "Test Device"
        )
        
        # Verify session data
        assert "access_token" in session_data
        assert "refresh_token" in session_data
        assert session_data["token_type"] == "bearer"
        assert session_data["expires_in"] == test_user.session_timeout_minutes * 60
        assert "session_id" in session_data
        assert "device_fingerprint" in session_data
        assert session_data["requires_mfa"] == False
        
        # Verify session was added to database
        mock_session.add.assert_called()
        mock_session.commit.assert_called()
        mock_session.refresh.assert_called()
    
    @pytest.mark.asyncio
    async def test_create_user_session_with_existing_sessions(self, auth_service, mock_session, test_user):
        """Test user session creation with existing sessions."""
        # Create existing sessions
        existing_session = UserSession(
            user_id=test_user.id,
            session_token="old_token",
            refresh_token="old_refresh",
            device_fingerprint="old_device",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        
        # Mock database queries
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [existing_session]
        mock_session.execute.return_value = mock_result
        
        # Create new session
        session_data = await auth_service.create_user_session(
            mock_session, test_user, "192.168.1.100", "Mozilla/5.0", "New Device"
        )
        
        # Verify session data
        assert "access_token" in session_data
        assert "session_id" in session_data
        
        # Verify old session was deactivated
        assert existing_session.is_active == False
    
    @pytest.mark.asyncio
    async def test_validate_session(self, auth_service, mock_session, test_user):
        """Test session validation."""
        # Create valid session
        valid_session = UserSession(
            user_id=test_user.id,
            session_token="valid_token",
            refresh_token="valid_refresh",
            device_fingerprint="device123",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            is_active=True
        )
        
        # Mock database queries
        mock_result = Mock()
        mock_result.scalar_one_or_none.side_effect = [test_user, valid_session]
        mock_session.execute.return_value = mock_result
        
        # Mock token verification
        with patch('app.services.auth.verify_token') as mock_verify:
            mock_verify.return_value = {"sub": test_user.id, "username": test_user.username}
            
            # Validate session
            user = await auth_service.validate_session(
                mock_session, "valid_token", "192.168.1.100", "Mozilla/5.0"
            )
            
            # Verify results
            assert user is not None
            assert user.id == test_user.id
            assert user.username == test_user.username
            
            # Verify session activity was updated
            mock_session.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_validate_session_invalid_token(self, auth_service, mock_session):
        """Test session validation with invalid token."""
        # Mock token verification failure
        with patch('app.services.auth.verify_token') as mock_verify:
            mock_verify.return_value = None
            
            # Validate session
            user = await auth_service.validate_session(
                mock_session, "invalid_token", "192.168.1.100", "Mozilla/5.0"
            )
            
            # Verify results
            assert user is None
    
    @pytest.mark.asyncio
    async def test_validate_session_expired_session(self, auth_service, mock_session, test_user):
        """Test session validation with expired session."""
        # Create expired session
        expired_session = UserSession(
            user_id=test_user.id,
            session_token="expired_token",
            refresh_token="expired_refresh",
            device_fingerprint="device123",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            expires_at=datetime.utcnow() - timedelta(hours=1),  # Expired
            is_active=True
        )
        
        # Mock database queries
        mock_result = Mock()
        mock_result.scalar_one_or_none.side_effect = [test_user, expired_session]
        mock_session.execute.return_value = mock_result
        
        # Mock token verification
        with patch('app.services.auth.verify_token') as mock_verify:
            mock_verify.return_value = {"sub": test_user.id, "username": test_user.username}
            
            # Validate session
            user = await auth_service.validate_session(
                mock_session, "expired_token", "192.168.1.100", "Mozilla/5.0"
            )
            
            # Verify results
            assert user is None
    
    @pytest.mark.asyncio
    async def test_logout_user(self, auth_service, mock_session):
        """Test user logout."""
        # Create session to logout
        session_to_logout = UserSession(
            user_id="user123",
            session_token="token_to_logout",
            refresh_token="refresh_to_logout",
            device_fingerprint="device123",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            is_active=True
        )
        
        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = session_to_logout
        mock_session.execute.return_value = mock_result
        
        # Logout user
        success = await auth_service.logout_user(
            mock_session, "token_to_logout", "192.168.1.100", "Mozilla/5.0"
        )
        
        # Verify results
        assert success == True
        assert session_to_logout.is_active == False
        mock_session.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_logout_user_invalid_token(self, auth_service, mock_session):
        """Test user logout with invalid token."""
        # Mock database query - session not found
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Logout user
        success = await auth_service.logout_user(
            mock_session, "invalid_token", "192.168.1.100", "Mozilla/5.0"
        )
        
        # Verify results
        assert success == False
    
    @pytest.mark.asyncio
    async def test_logout_all_sessions(self, auth_service, mock_session):
        """Test logout all sessions."""
        # Create active sessions
        session1 = UserSession(
            user_id="user123",
            session_token="token1",
            refresh_token="refresh1",
            device_fingerprint="device1",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            is_active=True
        )
        
        session2 = UserSession(
            user_id="user123",
            session_token="token2",
            refresh_token="refresh2",
            device_fingerprint="device2",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            is_active=True
        )
        
        # Mock database query
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [session1, session2]
        mock_session.execute.return_value = mock_result
        
        # Logout all sessions
        sessions_terminated = await auth_service.logout_all_sessions(
            mock_session, "user123", "192.168.1.100", "Mozilla/5.0"
        )
        
        # Verify results
        assert sessions_terminated == 2
        assert session1.is_active == False
        assert session2.is_active == False
        mock_session.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, auth_service, mock_session, test_user):
        """Test successful password change."""
        # Mock password verification
        with patch('app.services.auth.verify_password') as mock_verify:
            mock_verify.return_value = True
            
            # Mock password validation
            with patch('app.services.auth.validate_password_strength') as mock_validate:
                mock_validate.return_value = {
                    "valid": True,
                    "score": 4,
                    "strength": "very_strong",
                    "issues": [],
                    "suggestions": []
                }
                
                # Mock breach detection
                with patch('app.services.auth.check_password_breach') as mock_breach:
                    mock_breach.return_value = False
                    
                    # Mock password hashing
                    with patch('app.services.auth.hash_password') as mock_hash:
                        mock_hash.return_value = "new_hashed_password"
                        
                        # Change password
                        result = await auth_service.change_password(
                            mock_session, test_user, "old_password", "NewSecurePass123!", 
                            "192.168.1.100", "Mozilla/5.0"
                        )
                        
                        # Verify results
                        assert result["success"] == True
                        assert "changed successfully" in result["message"]
                        assert test_user.hashed_password == "new_hashed_password"
                        assert test_user.password_changed_at is not None
                        mock_session.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_change_password_wrong_current_password(self, auth_service, mock_session, test_user):
        """Test password change with wrong current password."""
        # Mock password verification failure
        with patch('app.services.auth.verify_password') as mock_verify:
            mock_verify.return_value = False
            
            # Change password
            result = await auth_service.change_password(
                mock_session, test_user, "wrong_password", "NewSecurePass123!", 
                "192.168.1.100", "Mozilla/5.0"
            )
            
            # Verify results
            assert result["success"] == False
            assert "incorrect" in result["error"]
    
    @pytest.mark.asyncio
    async def test_change_password_weak_new_password(self, auth_service, mock_session, test_user):
        """Test password change with weak new password."""
        # Mock password verification
        with patch('app.services.auth.verify_password') as mock_verify:
            mock_verify.return_value = True
            
            # Mock password validation failure
            with patch('app.services.auth.validate_password_strength') as mock_validate:
                mock_validate.return_value = {
                    "valid": False,
                    "score": 1,
                    "strength": "weak",
                    "issues": ["Password too short"],
                    "suggestions": ["Use longer password"]
                }
                
                # Change password
                result = await auth_service.change_password(
                    mock_session, test_user, "old_password", "weak", 
                    "192.168.1.100", "Mozilla/5.0"
                )
                
                # Verify results
                assert result["success"] == False
                assert "requirements" in result["error"]
                assert "issues" in result
                assert "suggestions" in result
    
    @pytest.mark.asyncio
    async def test_change_password_breached_password(self, auth_service, mock_session, test_user):
        """Test password change with breached password."""
        # Mock password verification
        with patch('app.services.auth.verify_password') as mock_verify:
            mock_verify.return_value = True
            
            # Mock password validation
            with patch('app.services.auth.validate_password_strength') as mock_validate:
                mock_validate.return_value = {
                    "valid": True,
                    "score": 4,
                    "strength": "very_strong",
                    "issues": [],
                    "suggestions": []
                }
                
                # Mock breach detection
                with patch('app.services.auth.check_password_breach') as mock_breach:
                    mock_breach.return_value = True
                    
                    # Change password
                    result = await auth_service.change_password(
                        mock_session, test_user, "old_password", "password", 
                        "192.168.1.100", "Mozilla/5.0"
                    )
                    
                    # Verify results
                    assert result["success"] == False
                    assert "compromised" in result["error"]
    
    def test_device_type_detection(self, auth_service):
        """Test device type detection."""
        # Test mobile detection
        mobile_agents = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
            "Mozilla/5.0 (Linux; Android 10; SM-G975F)",
            "Mozilla/5.0 (Mobile; rv:68.0) Gecko/68.0 Firefox/68.0"
        ]
        
        for agent in mobile_agents:
            device_type = auth_service._detect_device_type(agent)
            assert device_type == "mobile"
        
        # Test tablet detection
        tablet_agents = [
            "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)",
            "Mozilla/5.0 (Linux; Android 10; SM-T860)"
        ]
        
        for agent in tablet_agents:
            device_type = auth_service._detect_device_type(agent)
            assert device_type == "tablet"
        
        # Test desktop detection
        desktop_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        ]
        
        for agent in desktop_agents:
            device_type = auth_service._detect_device_type(agent)
            assert device_type == "desktop"
        
        # Test unknown detection
        unknown_agent = "Custom User Agent String"
        device_type = auth_service._detect_device_type(unknown_agent)
        assert device_type == "unknown"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 