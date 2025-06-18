from __future__ import annotations

from datetime import datetime
from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class Tenant(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    plan: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    email: EmailStr
    password_hash: str
    role: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Device(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    name: str
    type: str
    last_seen: datetime | None = None
    status: str | None = None


class Metric(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    device_id: int = Field(foreign_key="device.id")
    ts: datetime = Field(default_factory=datetime.utcnow)
    key: str
    value: float


class RefreshToken(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    token: str
    expires_at: datetime
    revoked: bool = Field(default=False)


__all__ = [
    "Tenant",
    "User",
    "Device",
    "Metric",
    "RefreshToken",
]
