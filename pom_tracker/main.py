from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database.db import SessionLocal, Base, engine

from .routers import users
from .routers import pomodoro


class Application:
    app: FastAPI

    def __init__(self):
        self.app = FastAPI()

        # Static files
        self.app.mount("/assets", StaticFiles(directory="pom_tracker/assets"), name="static")

        # Routes
        self.app.include_router(users.router)
        self.app.include_router(pomodoro.router)

    @staticmethod
    def root():
        return {"message": "Root!"}

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

app.get("/")(application.root)
