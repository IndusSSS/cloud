# app/worker.py
"""
MQTT consumer worker for IoT sensor data ingestion.
"""

import asyncio
import json
import logging
import uuid
import time
from datetime import datetime
from typing import Dict, Any
from aiomqtt import Client, MqttError
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


async def wait_for_services():
    """Wait for required services to be available."""
    logger.info("Waiting for services to be ready...")
    
    # Wait for Redis
    for attempt in range(30):
        try:
            redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            await redis_client.ping()
            logger.info("✅ Redis is ready")
            break
        except Exception as e:
            logger.warning(f"Redis not ready (attempt {attempt + 1}/30): {e}")
            await asyncio.sleep(2)
    else:
        logger.error("❌ Redis failed to start after 30 attempts")
        return False
    
    # Wait for MQTT broker
    for attempt in range(30):
        try:
            async with Client(settings.MQTT_BROKER, port=settings.MQTT_PORT) as client:
                await client.publish("test/connection", "test")
                logger.info("✅ MQTT broker is ready")
                break
        except Exception as e:
            logger.warning(f"MQTT broker not ready (attempt {attempt + 1}/30): {e}")
            await asyncio.sleep(2)
    else:
        logger.error("❌ MQTT broker failed to start after 30 attempts")
        return False
    
    return True


async def consume():
    """MQTT consumer with Redis fan-out."""
    # Wait for services to be ready
    if not await wait_for_services():
        logger.error("Failed to connect to required services")
        return
    
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    while True:
        try:
            logger.info(f"Connecting to MQTT broker at {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
            async with Client(settings.MQTT_BROKER, port=settings.MQTT_PORT) as client:
                await client.subscribe("iot/+/+")
                logger.info("✅ MQTT consumer started successfully")
                
                async for message in client.messages:
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
                                    is_active=True
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
                            try:
                                await redis_client.publish(
                                    "sensor_new", 
                                    json.dumps({
                                        "device_id": device_id,
                                        "tenant_id": str(tenant.id),
                                        "payload": payload,
                                        "timestamp": sensor_data.timestamp.isoformat()
                                    })
                                )
                            except Exception as e:
                                logger.warning(f"Failed to publish to Redis: {e}")
                            
                            logger.info(f"Processed sensor data for device {device_id}: {payload}")
                            
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        continue
                        
        except MqttError as e:
            logger.error(f"MQTT connection error: {e}")
            logger.info("Retrying in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.info("Retrying in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(consume())
