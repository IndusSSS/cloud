from fastapi import FastAPI
from sqlmodel import SQLModel, Session, select

from database import engine
from models import User
from routers import auth, users
from security import get_password_hash


def create_app() -> FastAPI:
    app = FastAPI(title="Auth API")

    @app.on_event("startup")
    def startup() -> None:
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            admin = session.exec(
                select(User).where(User.username == "admin")
            ).first()
            if not admin:
                session.add(
                    User(
                        username="admin",
                        hashed_password=get_password_hash("admin123"),
                        is_superuser=True,
                    )
                )
                session.commit()

    app.include_router(auth.router)
    app.include_router(users.router)
    return app


app = create_app()
