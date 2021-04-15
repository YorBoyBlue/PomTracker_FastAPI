from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database.db import SessionLocal, Base, engine

from .routers import main
from .routers import user
from .routers import pomodoro


class Application:
    app: FastAPI

    def __init__(self):
        self.app = FastAPI()

        # Static files
        self.app.mount("/assets", StaticFiles(directory="pom_tracker/assets"), name="static")

        # Routes
        self.app.include_router(main.router)
        self.app.include_router(user.router)
        self.app.include_router(pomodoro.router)

    @staticmethod
    def create_db():
        Base.metadata.create_all(engine)

    # Dependency
    @staticmethod
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


application = Application()
app = application.app

# application.create_db()
