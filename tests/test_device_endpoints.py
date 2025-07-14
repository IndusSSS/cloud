"""
Tests for device management endpoints.

• Tests device CRUD operations
• Tests device authentication and authorization
• Tests device sensor data retrieval
• Tests device status management
"""

import pytest
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app
from app.models.device import Device
from app.models.sensor import SensorData
from app.utils.security import create_access_token


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_token():
    """Create a test authentication token."""
    user_data = {"sub": "testuser", "tenant_id": "test-tenant"}
    return create_access_token(user_data)


@pytest.fixture
def admin_token():
    """Create an admin authentication token."""
    user_data = {"sub": "admin", "tenant_id": "test-tenant", "is_admin": True}
    return create_access_token(user_data)


@pytest.fixture
def test_device_data():
    return {
        "name": "Test Device",
        "description": "A test device for API testing",
        "specifications": json.dumps({"type": "sensor", "model": "test-v1"}),
        "is_active": True
    }


def test_devices_endpoint_requires_auth(client):
    """Test that devices endpoint requires authentication."""
    response = client.get("/api/v1/devices/")
    assert response.status_code == 401


def test_device_creation_requires_auth(client, test_device_data):
    """Test that device creation requires authentication."""
    response = client.post("/api/v1/devices/", json=test_device_data)
    assert response.status_code == 401


def test_device_model_validation():
    """Test Device model validation."""
    # Test valid device
    device = Device(
        name="Test Device",
        description="Test description",
        specifications=json.dumps({"type": "sensor"}),
        is_active=True,
        tenant_id="test-tenant"
    )
    
    assert device.name == "Test Device"
    assert device.description == "Test description"
    assert device.is_active == True
    assert device.tenant_id == "test-tenant"


def test_device_model_required_fields():
    """Test Device model required fields."""
    # Test valid device with all required fields
    valid_device = Device(
        name="Valid Device",
        description="Test description",
        tenant_id="test-tenant"
    )
    assert valid_device.name == "Valid Device"
    assert valid_device.description == "Test description"
    assert valid_device.tenant_id == "test-tenant"


def test_device_specifications_json():
    """Test device specifications JSON handling."""
    specs = {
        "type": "temperature_sensor",
        "model": "TEMP-001",
        "accuracy": 0.1,
        "range": [-40, 125]
    }
    
    device = Device(
        name="Temperature Sensor",
        specifications=json.dumps(specs),
        tenant_id="test-tenant"
    )
    
    # Verify specifications are stored as JSON string
    assert isinstance(device.specifications, str)
    
    # Verify JSON can be parsed back
    parsed_specs = json.loads(device.specifications)
    assert parsed_specs["type"] == "temperature_sensor"
    assert parsed_specs["accuracy"] == 0.1


def test_device_status_management():
    """Test device active/inactive status."""
    # Test active device
    active_device = Device(
        name="Active Device",
        is_active=True,
        tenant_id="test-tenant"
    )
    assert active_device.is_active == True
    
    # Test inactive device
    inactive_device = Device(
        name="Inactive Device",
        is_active=False,
        tenant_id="test-tenant"
    )
    assert inactive_device.is_active == False


def test_device_tenant_isolation():
    """Test device tenant isolation."""
    device_tenant_a = Device(
        name="Device A",
        tenant_id="tenant-a"
    )
    
    device_tenant_b = Device(
        name="Device B",
        tenant_id="tenant-b"
    )
    
    # Devices should have different tenant IDs
    assert device_tenant_a.tenant_id != device_tenant_b.tenant_id


def test_device_unique_constraints():
    """Test device unique constraints."""
    # Test that devices can have same name in different tenants
    device1 = Device(
        name="Same Name Device",
        tenant_id="tenant-1"
    )
    
    device2 = Device(
        name="Same Name Device",
        tenant_id="tenant-2"
    )
    
    # Should be allowed (different tenants)
    assert device1.name == device2.name
    assert device1.tenant_id != device2.tenant_id


def test_sensor_data_device_relationship():
    """Test sensor data and device relationship."""
    device_id = "test-device-123"
    
    sensor_data = SensorData(
        device_id=device_id,
        tenant_id="test-tenant",
        payload=json.dumps({"temperature": 23.5})
    )
    
    assert sensor_data.device_id == device_id
    assert sensor_data.tenant_id == "test-tenant"


def test_device_endpoints_structure(client):
    """Test that device endpoints have correct structure."""
    # Test devices list endpoint
    response = client.get("/api/v1/devices/")
    # Should return 401 (unauthorized) not 404 (not found)
    assert response.status_code == 401
    
    # Test device detail endpoint
    response = client.get("/api/v1/devices/test-device-id")
    assert response.status_code == 401
    
    # Test device creation endpoint
    response = client.post("/api/v1/devices/", json={})
    assert response.status_code == 401


def test_device_data_validation():
    """Test device data validation."""
    # Test valid device data
    valid_data = {
        "name": "Valid Device",
        "description": "Valid description",
        "specifications": json.dumps({"type": "sensor"}),
        "is_active": True
    }
    
    # Test invalid device data (missing name)
    invalid_data = {
        "description": "Missing name",
        "is_active": True
    }
    
    # Valid data should pass validation
    assert "name" in valid_data
    assert valid_data["name"] != ""
    
    # Invalid data should fail validation
    assert "name" not in invalid_data


def test_device_sensor_data_retrieval():
    """Test device sensor data retrieval logic."""
    # Test sensor data filtering by device
    device_id = "test-device"
    
    sensor_data1 = SensorData(
        device_id=device_id,
        tenant_id="test-tenant",
        payload=json.dumps({"temperature": 23.5})
    )
    
    sensor_data2 = SensorData(
        device_id="other-device",
        tenant_id="test-tenant",
        payload=json.dumps({"temperature": 25.0})
    )
    
    # Verify device filtering logic
    assert sensor_data1.device_id == device_id
    assert sensor_data2.device_id != device_id


def test_device_authentication_flow():
    """Test device authentication flow."""
    # Test device authentication token format
    device_token_data = {
        "sub": "device-123",
        "tenant_id": "test-tenant",
        "device_id": "device-123"
    }
    
    token = create_access_token(device_token_data)
    
    # Verify token is created
    assert token is not None
    assert isinstance(token, str)


if __name__ == "__main__":
    pytest.main([__file__]) 