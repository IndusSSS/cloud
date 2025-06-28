import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import create_app  # type: ignore[import-not-found]
from security import decode_token, get_password_hash  # type: ignore[import-not-found]
from models import User  # type: ignore[import-not-found]
from database import engine  # type: ignore[import-not-found]
from sqlmodel import SQLModel, Session, select

app = create_app()
SQLModel.metadata.create_all(engine)
with Session(engine) as session:
    if not session.exec(
        select(User).where(User.email == "admin@smartsecurity.solutions")
    ).first():
        session.add(
            User(
                email="admin@smartsecurity.solutions",
                hashed_password=get_password_hash("admin123"),
                is_superuser=True,
            )
        )
        session.commit()


@pytest.mark.asyncio
async def test_login_and_refresh() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post(
            "/login",
            json={"email": "admin@smartsecurity.solutions", "password": "admin123"},
        )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data and "refresh_token" in data
    access = decode_token(data["access_token"])
    refresh = decode_token(data["refresh_token"])
    assert access["type"] == "access"
    assert refresh["type"] == "refresh"

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res2 = await ac.post("/refresh", json={"refresh_token": data["refresh_token"]})
    assert res2.status_code == 200
    new_access = res2.json()["access_token"]
    decoded = decode_token(new_access)
    assert decoded["type"] == "access"
