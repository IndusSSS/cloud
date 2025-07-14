# app/worker.py
"""
MQTT consumer worker for IoT sensor data ingestion.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any
from aiomqtt import Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.sensor import SensorData
from app.models.device import Device
from app.models.tenant import Tenant
import redis.asyncio as redis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [worker] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


async def consume():
    """MQTT consumer with Redis fan-out."""
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    async with Client(settings.MQTT_BROKER, port=settings.MQTT_PORT) as client:
        async with client.messages() as messages:
            await client.subscribe("iot/+/+")
            async for message in messages:
                try:
                    # Parse topic: iot/{tenant}/{device_id}
                    topic_parts = message.topic.value.split("/")
                    if len(topic_parts) != 3:
                        logger.warning(f"Invalid topic format: {message.topic.value}")
                        continue
                    
                    tenant_name = topic_parts[1]
                    device_id = topic_parts[2]
                    
                    # Parse payload
                    payload = json.loads(message.payload)
                    
                    # Get or create device
                    async with AsyncSessionLocal() as session:
                        # Get tenant by name
                        tenant_query = select(Tenant).where(Tenant.name == tenant_name)
                        result = await session.execute(tenant_query)
                        tenant = result.scalar_one_or_none()
                        
                        if not tenant:
                            # Create tenant if it doesn't exist
                            tenant = Tenant(name=tenant_name, plan="free")
                            session.add(tenant)
                            await session.commit()
                            await session.refresh(tenant)
                            logger.info(f"Created new tenant: {tenant_name}")
                        
                        # Check if device exists
                        device_query = select(Device).where(Device.id == device_id)
                        result = await session.execute(device_query)
                        device = result.scalar_one_or_none()
                        
                        if not device:
                            # Create device if it doesn't exist
                            device = Device(
                                id=device_id,
                                name=f"Device-{device_id[:8]}",
                                tenant_id=tenant.id,
                                status="active"
                            )
                            session.add(device)
                            await session.commit()
                            logger.info(f"Created new device: {device_id}")
                        
                        # Create sensor data record
                        sensor_data = SensorData(
                            id=uuid.uuid4(),
                            device_id=device_id,
                            tenant_id=tenant.id,
                            payload=payload,
                            timestamp=datetime.utcnow()
                        )
                        session.add(sensor_data)
                        await session.commit()
                        
                        # Publish to Redis for real-time updates
                        await redis_client.publish(
                            "sensor_new", 
                            json.dumps({
                                "device_id": device_id,
                                "tenant_id": str(tenant.id),
                                "payload": payload,
                                "timestamp": sensor_data.timestamp.isoformat()
                            })
                        )
                        
                        logger.info(f"Processed sensor data for device {device_id}: {payload}")
                        
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue


if __name__ == "__main__":
    asyncio.run(consume())
