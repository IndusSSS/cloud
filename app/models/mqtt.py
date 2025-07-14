# app/models/mqtt.py
"""
Pydantic models for MQTT payload validation.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class MQTTSensorPayload(BaseModel):
    """Pydantic model for MQTT sensor data payload."""
    
    sensor_type: str = Field(..., description="Type of sensor")
    value: float = Field(..., description="Sensor reading value")
    unit: Optional[str] = Field(default="", description="Measurement unit")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="When reading was taken")


class MQTTMessage(BaseModel):
    """Complete MQTT message structure."""
    
    tenant_id: str = Field(..., description="Tenant identifier")
    device_id: str = Field(..., description="Device identifier")
    payload: MQTTSensorPayload = Field(..., description="Sensor data payload")
    received_at: datetime = Field(default_factory=datetime.utcnow, description="When message was received") 