# app/models/device.py
from uuid import UUID, uuid4
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint


class Device(SQLModel, table=True):
    """
    IoT device registry table.

    • `id` – UUID primary-key.
    • `name` – human-friendly label.
    • `description` – optional notes.
    • `specifications` – device specifications as JSON.
    • `is_active` – soft-delete / enable flag.
    • `tenant_id` – foreign key to tenant.
    """
    __tablename__ = "devices"
    __table_args__ = (
        UniqueConstraint('tenant_id', 'name', name='uq_device_tenant_name'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str = Field(index=True, nullable=False)
    description: Optional[str] = Field(default=None)
    specifications: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    tenant_id: Optional[str] = Field(index=True, nullable=True)
