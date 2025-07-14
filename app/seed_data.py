"""
Seed data for demo purposes.

• Creates demo devices for the default tenant.
• Generates sample sensor data for testing.
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from uuid import uuid4
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.device import Device
from app.models.sensor import SensorData
from app.models.tenant import Tenant


async def create_demo_devices():
    """Create demo devices for the default tenant."""
    async with AsyncSessionLocal() as session:
        # Get default tenant
        result = await session.execute(select(Tenant).where(Tenant.name == "default"))
        default_tenant = result.scalar_one_or_none()
        
        if not default_tenant:
            print("Default tenant not found, skipping demo device creation")
            return
        
        # Check if demo devices already exist
        result = await session.execute(select(Device).where(Device.tenant_id == default_tenant.id))
        existing_devices = result.scalars().all()
        
        if existing_devices:
            print(f"Demo devices already exist ({len(existing_devices)} devices)")
            return existing_devices
        
        # Create demo devices
        demo_devices = [
            {
                "name": "Office Temperature Sensor",
                "description": "Temperature and humidity sensor in main office",
                "specifications": {"type": "environmental", "location": "office"},
                "is_active": True
            },
            {
                "name": "Server Room Monitor",
                "description": "Environmental monitoring in server room",
                "specifications": {"type": "environmental", "location": "server_room"},
                "is_active": True
            },
            {
                "name": "Warehouse Security Camera",
                "description": "Security camera with motion detection",
                "specifications": {"type": "security", "location": "warehouse"},
                "is_active": True
            },
            {
                "name": "Parking Lot Sensor",
                "description": "Vehicle detection and counting sensor",
                "specifications": {"type": "traffic", "location": "parking_lot"},
                "is_active": False
            },
            {
                "name": "HVAC Controller",
                "description": "Smart HVAC system controller",
                "specifications": {"type": "hvac", "location": "building"},
                "is_active": True
            }
        ]
        
        devices = []
        for device_data in demo_devices:
            device = Device(
                id=str(uuid4()),
                name=device_data["name"],
                description=device_data["description"],
                specifications=json.dumps(device_data["specifications"]),
                is_active=device_data["is_active"],
                tenant_id=default_tenant.id
            )
            session.add(device)
            devices.append(device)
        
        await session.commit()
        
        for device in devices:
            await session.refresh(device)
        
        print(f"Created {len(devices)} demo devices")
        return devices


async def create_demo_sensor_data():
    """Create demo sensor data for the devices."""
    async with AsyncSessionLocal() as session:
        # Get all devices
        result = await session.execute(select(Device))
        devices = result.scalars().all()
        
        if not devices:
            print("No devices found, skipping sensor data creation")
            return
        
        # Check if sensor data already exists
        result = await session.execute(select(SensorData))
        existing_data = result.scalars().first()
        
        if existing_data:
            print("Demo sensor data already exists")
            return
        
        # Generate sensor data for the last 7 days
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)
        
        sensor_data = []
        
        for device in devices:
            # Generate data every 15 minutes for the last 7 days
            current_time = start_time
            while current_time <= end_time:
                # Generate realistic sensor values
                if "temperature" in device.name.lower() or "environmental" in device.specifications:
                    temp = random.uniform(18.0, 28.0)  # Office temperature range
                    humidity = random.uniform(40.0, 60.0)  # Normal humidity range
                    payload = {
                        "temp": round(temp, 1),
                        "humidity": round(humidity, 1),
                        "device_id": device.id,
                        "timestamp": current_time.isoformat()
                    }
                elif "security" in device.name.lower():
                    motion_detected = random.choice([True, False])
                    payload = {
                        "motion_detected": motion_detected,
                        "confidence": random.uniform(0.8, 1.0),
                        "device_id": device.id,
                        "timestamp": current_time.isoformat()
                    }
                elif "hvac" in device.name.lower():
                    temp = random.uniform(20.0, 25.0)
                    fan_speed = random.randint(0, 100)
                    payload = {
                        "temperature": round(temp, 1),
                        "fan_speed": fan_speed,
                        "mode": random.choice(["cool", "heat", "fan"]),
                        "device_id": device.id,
                        "timestamp": current_time.isoformat()
                    }
                else:
                    # Generic sensor data
                    value = random.uniform(0, 100)
                    payload = {
                        "value": round(value, 2),
                        "unit": "units",
                        "device_id": device.id,
                        "timestamp": current_time.isoformat()
                    }
                
                sensor_record = SensorData(
                    id=str(uuid4()),
                    tenant_id=device.tenant_id,
                    device_id=device.id,
                    payload=json.dumps(payload),
                    timestamp=current_time
                )
                session.add(sensor_record)
                sensor_data.append(sensor_record)
                
                current_time += timedelta(minutes=15)
        
        await session.commit()
        print(f"Created {len(sensor_data)} sensor data records")


async def seed_demo_data():
    """Seed all demo data."""
    print("Seeding demo data...")
    
    try:
        devices = await create_demo_devices()
        await create_demo_sensor_data()
        print("✅ Demo data seeded successfully")
    except Exception as e:
        print(f"❌ Error seeding demo data: {e}")


if __name__ == "__main__":
    asyncio.run(seed_demo_data()) 