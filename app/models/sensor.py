# app/models/sensor.py
"""
Sensor data model for IoT device readings.

• Stores sensor measurements and metadata.
• Links to devices and users for access control.
• Supports various sensor types and data formats.
"""

from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Sensor(SQLModel, table=True):
    """
    Sensor data table.
    
    • `id` – UUID primary key.
    • `device_id` – foreign key to device.
    • `sensor_type` – type of sensor (temperature, motion, etc.).
    • `value` – sensor reading value.
    • `unit` – measurement unit.
    • `metadata` – additional sensor data as JSON.
    • `timestamp` – when reading was taken.
    • `created_at` – record creation time.
    """
    __tablename__ = "sensors"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    device_id: str = Field(index=True, nullable=False)
    sensor_type: str = Field(index=True, nullable=False)
    value: float = Field(nullable=False)
    unit: str = Field(default="")
    sensor_metadata: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SensorData(SQLModel, table=True):
    """
    MQTT sensor data table with JSONB payload.
    
    • `id` – UUID primary key.
    • `tenant_id` – foreign key to tenant.
    • `device_id` – device identifier.
    • `payload` – JSONB payload containing sensor data.
    • `timestamp` – when data was received.
    • `created_at` – record creation time.
    """
    __tablename__ = "sensor_data"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    tenant_id: Optional[str] = Field(index=True, nullable=True)
    device_id: str = Field(index=True, nullable=False)
    payload: str = Field(default="{}")
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)