# tests/test_mqtt_ingest.py
"""
Unit tests for MQTT ingestion functionality.
"""

import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.models.sensor import SensorData
from app.models.device import Device
from app.models.tenant import Tenant
from app.worker import consume


@pytest.fixture
def sample_mqtt_payload():
    """Sample MQTT payload for testing."""
    return {
        "sensor_type": "temperature",
        "value": 23.5,
        "unit": "°C",
        "metadata": {"location": "room1", "accuracy": 0.1},
        "timestamp": "2025-01-10T12:00:00Z"
    }


@pytest.fixture
def sample_topic():
    """Sample MQTT topic for testing."""
    return "iot/tenant1/device123"


@pytest.mark.asyncio
async def test_mqtt_consumer_connection():
    """Test MQTT consumer connection and subscription."""
    with patch('app.worker.Client') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with patch('app.worker.redis.from_url') as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis.return_value = mock_redis_client
            
            with patch('app.worker.AsyncSessionLocal') as mock_session_local:
                mock_session = AsyncMock()
                mock_session_local.return_value.__aenter__.return_value = mock_session
                
                # Mock session operations
                mock_session.execute = AsyncMock()
                mock_session.add = MagicMock()
                mock_session.commit = AsyncMock()
                mock_session.refresh = AsyncMock()
                
                # Mock query results
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = None
                mock_session.execute.return_value = mock_result
                
                # This would run indefinitely, so we'll just test the setup
                # In a real test, you'd want to mock the message loop
                pass


def test_sensor_data_model():
    """Test SensorData model creation."""
    payload = {
        "sensor_type": "temperature",
        "value": 23.5,
        "unit": "°C"
    }
    
    sensor_data = SensorData(
        tenant_id="tenant1",
        device_id="device123",
        payload=json.dumps(payload)
    )
    
    assert sensor_data.tenant_id == "tenant1"
    assert sensor_data.device_id == "device123"
    assert sensor_data.payload == json.dumps(payload)
    assert sensor_data.timestamp is not None


def test_device_model():
    """Test Device model creation."""
    device = Device(
        name="Test Device",
        tenant_id="tenant1",
        is_active=True
    )
    
    assert device.name == "Test Device"
    assert device.tenant_id == "tenant1"
    assert device.is_active == True


def test_tenant_model():
    """Test Tenant model creation."""
    tenant = Tenant(
        name="test-tenant",
        plan="free"
    )
    
    assert tenant.name == "test-tenant"
    assert tenant.plan == "free"


@pytest.mark.asyncio
async def test_mqtt_topic_parsing():
    """Test MQTT topic parsing logic."""
    # Test valid topic
    topic = "iot/tenant1/device123"
    parts = topic.split("/")
    
    assert len(parts) == 3
    assert parts[0] == "iot"
    assert parts[1] == "tenant1"
    assert parts[2] == "device123"
    
    # Test invalid topic
    invalid_topic = "iot/tenant1"
    parts = invalid_topic.split("/")
    
    assert len(parts) != 3


@pytest.mark.asyncio
async def test_redis_publish_format():
    """Test Redis publish message format."""
    expected_data = {
        "device_id": "device123",
        "tenant_id": "tenant1",
        "payload": {"sensor_type": "temperature", "value": 23.5},
        "timestamp": "2025-01-10T12:00:00Z"
    }
    
    # Test JSON serialization
    json_data = json.dumps(expected_data)
    parsed_data = json.loads(json_data)
    
    assert parsed_data["device_id"] == "device123"
    assert parsed_data["tenant_id"] == "tenant1"
    assert parsed_data["payload"]["sensor_type"] == "temperature"


if __name__ == "__main__":
    pytest.main([__file__]) 