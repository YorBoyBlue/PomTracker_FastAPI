from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .dependencies.database_manager import dbm
from .routers import router


class Application:
    app: FastAPI

    def __init__(self):
        self.app = FastAPI()

        # Static files
        self.app.mount("/assets", StaticFiles(directory="pom_tracker/assets"), name="static")

        # Routes
        self.app.include_router(router.routers)

    @staticmethod
    def create_db():
        dbm.Base.metadata.create_all(dbm.engine)


application = Application()
app = application.app

# application.create_db()
