from sqlalchemy import Column, Integer, String, ForeignKey
from app.db import Base

class Device(Base):
    __tablename__ = "devices"

    id        = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name      = Column(String(64), nullable=False)
    status    = Column(String(16), nullable=False, server_default="offline")
