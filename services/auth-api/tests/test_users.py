import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import create_app  # type: ignore[import-not-found]
from security import get_password_hash  # type: ignore[import-not-found]
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


async def get_token(ac: AsyncClient) -> str:
    res = await ac.post(
        "/login",
        json={"email": "admin@smartsecurity.solutions", "password": "admin123"},
    )
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_user_crud() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        token = await get_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # create user
        res = await ac.post(
            "/users/",
            json={"email": "new@user.com", "password": "pass", "is_superuser": False},
            headers=headers,
        )
        assert res.status_code == 200
        user_id = res.json()["id"]

        # list users
        res = await ac.get("/users/", headers=headers)
        assert any(u["id"] == user_id for u in res.json())

        # delete user
        res = await ac.delete(f"/users/{user_id}", headers=headers)
        assert res.status_code == 204
