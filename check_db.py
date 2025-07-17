#!/usr/bin/env python3
"""
Check database for users and create admin if needed.
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')

from sqlmodel import select
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.tenant import Tenant
from app.utils.security import hash_password

async def check_database():
    """Check database and create admin user if needed."""
    async with AsyncSessionLocal() as session:
        # Check for tenants
        result = await session.execute(select(Tenant))
        tenants = result.scalars().all()
        print(f"Found {len(tenants)} tenants:")
        for tenant in tenants:
            print(f"  - {tenant.name} (ID: {tenant.id})")
        
        # Check for users
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"\nFound {len(users)} users:")
        for user in users:
            print(f"  - {user.username} ({user.email}) - Admin: {user.is_admin}")
        
        # Create admin user if none exists
        admin_user = await session.execute(
            select(User).where(User.username == "admin")
        )
        admin_user = admin_user.scalar_one_or_none()
        
        if not admin_user:
            print("\nCreating admin user...")
            # Get default tenant
            default_tenant = await session.execute(
                select(Tenant).where(Tenant.name == "default")
            )
            default_tenant = default_tenant.scalar_one_or_none()
            
            if not default_tenant:
                print("Creating default tenant...")
                default_tenant = Tenant(name="default", plan="free")
                session.add(default_tenant)
                await session.commit()
                await session.refresh(default_tenant)
            
            # Create admin user
            admin_user = User(
                username="admin",
                email="admin@smartsecurity.local",
                hashed_password=hash_password("admin123"),
                is_admin=True,
                tenant_id=default_tenant.id
            )
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)
            print("✅ Admin user created successfully!")
        else:
            print("\n✅ Admin user already exists")

if __name__ == "__main__":
    asyncio.run(check_database()) 