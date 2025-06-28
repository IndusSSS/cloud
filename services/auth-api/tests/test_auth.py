import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import create_app  # type: ignore[import-not-found]
from security import decode_token, get_password_hash  # type: ignore[import-not-found]
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


def test_login_and_refresh() -> None:
    client = TestClient(app)
    res = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data and "refresh_token" in data
    access = decode_token(data["access_token"])
    refresh = decode_token(data["refresh_token"])
    assert access["type"] == "access"
    assert refresh["type"] == "refresh"

    res2 = client.post("/refresh", json={"refresh_token": data["refresh_token"]})
    assert res2.status_code == 200
    new_access = res2.json()["access_token"]
    decoded = decode_token(new_access)
    assert decoded["type"] == "access"


def test_login_failure() -> None:
    client = TestClient(app)
    res = client.post(
        "/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert res.status_code == 401
