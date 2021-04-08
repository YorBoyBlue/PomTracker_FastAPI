from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routers import users

from .database.db import Base
from .database.db import engine


class Application:
    app: FastAPI

    def __init__(self):
        self.app = FastAPI()

        # Static files
        self.app.mount("/assets", StaticFiles(directory="pom_tracker/assets"), name="static")

        # Routes
        self.app.include_router(users.router)

    @staticmethod
    def root():
        return {"message": "Root!"}

    @staticmethod
    def create_db():
        Base.metadata.create_all(bind=engine)


application = Application()
app = application.app

# application.create_db()

app.get("/")(application.root)
