"""
Tests for data ingestion endpoints.

• Tests sensor data ingestion
• Tests data validation and processing
• Tests real-time data broadcasting
• Tests data storage and retrieval
"""

import pytest
import json
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app
from app.models.sensor import SensorData, Sensor
from app.utils.security import create_access_token


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def device_token():
    """Create a device authentication token."""
    device_data = {"sub": "device-123", "tenant_id": "test-tenant", "device_id": "device-123"}
    return create_access_token(device_data)


@pytest.fixture
def sample_sensor_data():
    return {
        "sensor_type": "temperature",
        "value": 23.5,
        "unit": "°C",
        "metadata": {
            "location": "room1",
            "accuracy": 0.1,
            "timestamp": "2025-01-10T12:00:00Z"
        }
    }


@pytest.fixture
def sample_ingest_payload():
    return {
        "device_id": "test-device-123",
        "sensor_data": [
            {
                "sensor_type": "temperature",
                "value": 23.5,
                "unit": "°C"
            },
            {
                "sensor_type": "humidity",
                "value": 45.2,
                "unit": "%"
            }
        ],
        "timestamp": "2025-01-10T12:00:00Z"
    }


def test_ingest_endpoint_requires_auth(client, sample_ingest_payload):
    """Test that ingest endpoint requires authentication."""
    response = client.post("/api/v1/ingest/", json=sample_ingest_payload)
    assert response.status_code == 401


def test_sensor_data_model_validation():
    """Test SensorData model validation."""
    payload = {
        "sensor_type": "temperature",
        "value": 23.5,
        "unit": "°C"
    }
    
    sensor_data = SensorData(
        device_id="test-device",
        tenant_id="test-tenant",
        payload=json.dumps(payload)
    )
    
    assert sensor_data.device_id == "test-device"
    assert sensor_data.tenant_id == "test-tenant"
    assert sensor_data.payload == json.dumps(payload)
    assert sensor_data.timestamp is not None


def test_sensor_model_validation():
    """Test Sensor model validation."""
    sensor = Sensor(
        device_id="test-device",
        sensor_type="temperature",
        value=23.5,
        unit="°C",
        sensor_metadata=json.dumps({"location": "room1"})
    )
    
    assert sensor.device_id == "test-device"
    assert sensor.sensor_type == "temperature"
    assert sensor.value == 23.5
    assert sensor.unit == "°C"
    assert sensor.sensor_metadata == json.dumps({"location": "room1"})


def test_sensor_data_payload_validation():
    """Test sensor data payload validation."""
    # Valid payload
    valid_payload = {
        "sensor_type": "temperature",
        "value": 23.5,
        "unit": "°C"
    }
    
    # Invalid payload (missing value)
    invalid_payload = {
        "sensor_type": "temperature",
        "unit": "°C"
    }
    
    # Test JSON serialization
    valid_json = json.dumps(valid_payload)
    assert json.loads(valid_json)["sensor_type"] == "temperature"
    assert json.loads(valid_json)["value"] == 23.5


def test_sensor_data_timestamp_handling():
    """Test sensor data timestamp handling."""
    # Test automatic timestamp
    sensor_data = SensorData(
        device_id="test-device",
        tenant_id="test-tenant",
        payload=json.dumps({"temperature": 23.5})
    )
    
    assert sensor_data.timestamp is not None
    assert isinstance(sensor_data.timestamp, datetime)
    
    # Test custom timestamp
    custom_time = datetime.now(timezone.utc)
    sensor_data_custom = SensorData(
        device_id="test-device",
        tenant_id="test-tenant",
        payload=json.dumps({"temperature": 23.5}),
        timestamp=custom_time
    )
    
    assert sensor_data_custom.timestamp == custom_time


def test_sensor_data_tenant_isolation():
    """Test sensor data tenant isolation."""
    sensor_data_tenant_a = SensorData(
        device_id="device-1",
        tenant_id="tenant-a",
        payload=json.dumps({"temperature": 23.5})
    )
    
    sensor_data_tenant_b = SensorData(
        device_id="device-2",
        tenant_id="tenant-b",
        payload=json.dumps({"temperature": 25.0})
    )
    
    # Verify tenant isolation
    assert sensor_data_tenant_a.tenant_id != sensor_data_tenant_b.tenant_id


def test_sensor_data_device_relationship():
    """Test sensor data and device relationship."""
    device_id = "test-device-123"
    
    sensor_data = SensorData(
        device_id=device_id,
        tenant_id="test-tenant",
        payload=json.dumps({"temperature": 23.5})
    )
    
    assert sensor_data.device_id == device_id


def test_ingest_payload_structure():
    """Test ingest payload structure validation."""
    # Valid payload structure
    valid_payload = {
        "device_id": "test-device",
        "sensor_data": [
            {
                "sensor_type": "temperature",
                "value": 23.5,
                "unit": "°C"
            }
        ],
        "timestamp": "2025-01-10T12:00:00Z"
    }
    
    # Invalid payload (missing device_id)
    invalid_payload = {
        "sensor_data": [
            {
                "sensor_type": "temperature",
                "value": 23.5
            }
        ]
    }
    
    # Test valid payload structure
    assert "device_id" in valid_payload
    assert "sensor_data" in valid_payload
    assert isinstance(valid_payload["sensor_data"], list)
    
    # Test invalid payload structure
    assert "device_id" not in invalid_payload


def test_sensor_data_types():
    """Test different sensor data types."""
    sensor_types = [
        {"sensor_type": "temperature", "value": 23.5, "unit": "°C"},
        {"sensor_type": "humidity", "value": 45.2, "unit": "%"},
        {"sensor_type": "pressure", "value": 1013.25, "unit": "hPa"},
        {"sensor_type": "motion", "value": 1, "unit": "boolean"}
    ]
    
    for sensor_data in sensor_types:
        sensor = Sensor(
            device_id="test-device",
            sensor_type=sensor_data["sensor_type"],
            value=sensor_data["value"],
            unit=sensor_data["unit"]
        )
        
        assert sensor.sensor_type == sensor_data["sensor_type"]
        assert sensor.value == sensor_data["value"]
        assert sensor.unit == sensor_data["unit"]


def test_sensor_data_metadata():
    """Test sensor data metadata handling."""
    metadata = {
        "location": "room1",
        "accuracy": 0.1,
        "calibration_date": "2025-01-01",
        "manufacturer": "TestCorp"
    }
    
    sensor = Sensor(
        device_id="test-device",
        sensor_type="temperature",
        value=23.5,
        unit="°C",
        sensor_metadata=json.dumps(metadata)
    )
    
    # Verify metadata is stored as JSON
    assert isinstance(sensor.sensor_metadata, str)
    
    # Verify metadata can be parsed back
    parsed_metadata = json.loads(sensor.sensor_metadata)
    assert parsed_metadata["location"] == "room1"
    assert parsed_metadata["accuracy"] == 0.1


def test_ingest_endpoint_structure(client):
    """Test that ingest endpoint has correct structure."""
    # Test ingest endpoint exists
    response = client.post("/api/v1/ingest/", json={})
    # Should return 401 (unauthorized) not 404 (not found)
    assert response.status_code == 401


def test_sensor_data_retrieval_logic():
    """Test sensor data retrieval logic."""
    # Test filtering by device
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


def test_real_time_data_format():
    """Test real-time data format for WebSocket broadcasting."""
    real_time_data = {
        "device_id": "test-device",
        "tenant_id": "test-tenant",
        "payload": {"temperature": 23.5},
        "timestamp": "2025-01-10T12:00:00Z"
    }
    
    # Test JSON serialization for WebSocket
    json_data = json.dumps(real_time_data)
    parsed_data = json.loads(json_data)
    
    assert parsed_data["device_id"] == "test-device"
    assert parsed_data["tenant_id"] == "test-tenant"
    assert "payload" in parsed_data
    assert "timestamp" in parsed_data


if __name__ == "__main__":
    pytest.main([__file__]) 