import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import create_app  # type: ignore[import-not-found]
from security import get_password_hash  # type: ignore[import-not-found]
from models import User  # type: ignore[import-not-found]
from database import engine  # type: ignore[import-not-found]
from sqlmodel import SQLModel, Session, select

app = create_app()
SQLModel.metadata.create_all(engine)
with Session(engine) as session:
    if not session.exec(select(User).where(User.username == "admin")).first():
        session.add(
            User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                is_superuser=True,
            )
        )
        session.commit()


def get_token(client: TestClient) -> str:
    res = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"},
    )
    return res.json()["access_token"]


def test_user_crud() -> None:
    client = TestClient(app)
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

        # create user
    res = client.post(
        "/users/",
        json={"username": "newuser", "password": "pass", "is_superuser": False},
        headers=headers,
    )
    assert res.status_code == 200
    user_id = res.json()["id"]

        # list users
    res = client.get("/users/", headers=headers)
    assert any(u["id"] == user_id for u in res.json())

        # delete user
    res = client.delete(f"/users/{user_id}", headers=headers)
    assert res.status_code == 204
