# app/models/user.py
"""
User model for authentication and authorization.
"""

from datetime import datetime
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex, primary_key=True, index=True)
    username: str = Field(index=True)
    email: str = Field(index=True)
    hashed_password: str = Field()
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    tenant_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime = Field(default_factory=datetime.utcnow)
