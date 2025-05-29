# File: backend/app/models.py

from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP, Float, ForeignKey
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

# ——— The single source of truth for your metadata ————————————————
Base = declarative_base()

# ——— Your tables/models —————————————————————————————————————————

class Log(Base):
    __tablename__ = "logs"
    id        = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    switch    = Column(Boolean)
    ts_device = Column(Integer)  # millis() from ESP
    ts_server = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)

class Sensor(Base):
    __tablename__ = "sensors"
    id        = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))

class Actuator(Base):
    __tablename__ = "actuators"
    id = Column(Integer, primary_key=True, index=True)

class Metric(Base):
    __tablename__ = "metrics"
    id         = Column(Integer, primary_key=True, index=True)
    device_id  = Column(String, nullable=False)
    timestamp  = Column(TIMESTAMP(timezone=True), server_default=func.now())
    value      = Column(Float, nullable=False)
