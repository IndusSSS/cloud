# app/models/audit.py
"""
Audit log model for tracking system events and user actions.
"""

from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class AuditLog(SQLModel, table=True):
    """
    Audit log table for tracking system events.
    
    • `id` – UUID primary key.
    • `tenant_id` – foreign key to tenant.
    • `user_id` – foreign key to user who performed action.
    • `action` – type of action performed.
    • `resource_type` – type of resource affected.
    • `resource_id` – ID of affected resource.
    • `details` – additional details as JSON.
    • `ip_address` – IP address of the request.
    • `user_agent` – user agent string.
    • `created_at` – when event occurred.
    """
    __tablename__ = "audit_logs"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    tenant_id: Optional[str] = Field(index=True, nullable=True)
    user_id: Optional[str] = Field(index=True, nullable=True)
    action: str = Field(index=True, nullable=False)
    resource_type: str = Field(index=True, nullable=False)
    resource_id: Optional[str] = Field(index=True, nullable=True)
    details: Optional[str] = Field(default=None)
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True) 