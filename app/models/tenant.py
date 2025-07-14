# app/models/tenant.py
"""
Tenant model for multi-tenancy support.
"""

from datetime import datetime
from sqlmodel import SQLModel, Field


class Tenant(SQLModel, table=True):
    """
    Tenant table for multi-tenancy.
    
    • `id` – UUID primary key.
    • `name` – tenant name.
    • `plan` – subscription plan (free, pro, enterprise).
    • `created_at` – record creation time.
    """
    __tablename__ = "tenants"
    
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex, primary_key=True, index=True)
    name: str = Field(index=True)
    plan: str = Field(default="free")
    created_at: datetime = Field(default_factory=datetime.utcnow) 