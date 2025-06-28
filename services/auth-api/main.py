from fastapi import FastAPI
from sqlmodel import SQLModel

from database import engine
from routers import auth


def create_app() -> FastAPI:
    app = FastAPI(title="Auth API")

    @app.on_event("startup")
    def startup() -> None:
        SQLModel.metadata.create_all(engine)

    app.include_router(auth.router)
    return app


app = create_app()
