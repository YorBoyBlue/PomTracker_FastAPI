from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from routers import users

app = FastAPI()

# Static files
app.mount("/assets", StaticFiles(directory="assets"), name="static")

# Routes
app.include_router(users.router)


@app.get("/")
def root():
    return {"message": "Hello Bigger Applications!"}


@app.middleware("http")
async def db_middleware(request: Request, call_next):
    # Database session
    engine = create_engine('sqlite:///database/pom_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    response = await call_next(request)
    return response


class Application:

    def __init__(self):
        pass

    @staticmethod
    def start_app():
        uvicorn.run("app:app", host="127.0.0.1", port=1988, log_level="info")


if __name__ == '__main__':
    application = Application()
    application.start_app()
