from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from .database.db import SessionLocal, Base, engine
from .models.session_model import SessionModel
from .models.user_model import UserModel

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

application.create_db()

app.get("/")(application.root)


@app.middleware("http")
async def user_middleware(request: Request, call_next):
    included_paths_user = [
        '/users/logout',
        '/pomodoro/today',

        '/app/pomodoro',
        '/api/poms',
        '/api/pom_sheet_export',
        '/app/export_poms',
        '/app/pom_exists',
    ]

    derp = ''

    db = SessionLocal()

    if request.url.path in included_paths_user:
        my_cookie_hash = request.cookies.get('pomodoro_login_hash')
        if my_cookie_hash is not None:
            try:
                user_session = db.query(SessionModel, SessionModel.user_id).filter_by(
                    hash=my_cookie_hash).one()

            except NoResultFound as e:
                # User session was not found, send user to session expired login
                return RedirectResponse(url="/users/login", status_code=303)
                # raise falcon.HTTPFound('/app/session_expired')

            else:
                # User session was found, try to query user
                try:
                    user = db.query(UserModel).filter_by(id=user_session.user_id).one()

                except NoResultFound as e:
                    # User was not found, send user to session expired login
                    return RedirectResponse(url="/users/login", status_code=303)
                    # raise falcon.HTTPFound('/app/session_expired')

                else:
                    # User was found, pass it through the request context
                    request.session.user = user
                    # req.context['user'] = user

    response = await call_next(request)
    return response
