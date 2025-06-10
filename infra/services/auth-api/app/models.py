# File: services/auth-api/app/models.py
# services/auth-api/app/models.py

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Float, ForeignKey
from sqlalchemy.sql import func

from app.db import Base   # <-- use the Base defined in app/db.py

# ─── Tenants ────────────────────────────────────────────────────────────────────
class Tenant(Base):
    __tablename__ = "tenants"

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False)


# ─── Logs ───────────────────────────────────────────────────────────────────────
class Log(Base):
    __tablename__ = "logs"

    id        = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    switch    = Column(Boolean)
    ts_device = Column(Integer)  # millis() from ESP
    ts_server = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )


# ─── Devices ────────────────────────────────────────────────────────────────────
class Device(Base):
    __tablename__ = "devices"

    id        = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name      = Column(String(64), nullable=False)
    status    = Column(String(16), nullable=False, server_default="offline")


# ─── Sensors ────────────────────────────────────────────────────────────────────
class Sensor(Base):
    __tablename__ = "sensors"

    id        = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))


# ─── Actuators ─────────────────────────────────────────────────────────────────
class Actuator(Base):
    __tablename__ = "actuators"

    id = Column(Integer, primary_key=True, index=True)


# ─── Metrics ────────────────────────────────────────────────────────────────────
class Metric(Base):
    __tablename__ = "metrics"

    id        = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, nullable=False)
    timestamp = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )
    value     = Column(Float, nullable=False)
