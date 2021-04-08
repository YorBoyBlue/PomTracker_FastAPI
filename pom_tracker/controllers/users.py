from fastapi import Request, Response, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import random
import string
import hashlib
from datetime import datetime

from ..database.db import SessionLocal
from ..models.user_schema import *
from ..models.user_model import UserModel
from ..models.session_model import SessionModel
from ..error_handling.my_exceptions import NoSessionRecordExists


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


templates = Jinja2Templates(directory="pom_tracker/views")


def get_user_create(request: Request):
    """User create endpoint"""

    return templates.TemplateResponse("user_create_view.html", {"request": request})


def user_create(user: UserCreate, db: Session = Depends(get_db)):
    """Create new user"""

    today = datetime.utcnow()
    user_to_add = UserModel(email=user.email,
                            first_name=user.first_name, middle_name=user.middle_name,
                            last_name=user.last_name,
                            display_name=user.display_name,
                            password=user.password,
                            created=today,
                            modified=today)
    try:
        db.add(user_to_add)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        return RedirectResponse('/')
        # raise falcon.HTTPFound('/app/create_email_exists')

    else:
        # Send user to the login page if their account was created
        return RedirectResponse('/users/login')


def get_user_login(request: Request):
    """User login endpoint"""

    return templates.TemplateResponse("user_login_view.html", {"request": request})


def user_login(response: Response, email: str = Form(...), password: str = Form(...),
               db: Session = Depends(get_db)):
    """Login user"""

    db_user = db.query(UserModel).filter(UserModel.email == email).first()

    # User was not found, send back to login failed end point
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if password == db_user.password:
        rand_string = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=20))
        hash_object = hashlib.md5(rand_string.encode())
        pomodoro_login_hash = hash_object.hexdigest()
        now = datetime.utcnow()

        # check if user has an existing session in DB and modify it
        try:
            records_updated_count = db.query(SessionModel).filter_by(user_id=db_user.id).update(
                {"hash": pomodoro_login_hash, "modified": now})

            if records_updated_count == 0:
                raise NoSessionRecordExists('No session for this user was found')

            db.commit()

        # create a new session in DB if one does not exist
        except NoSessionRecordExists as e:
            session_to_add = SessionModel(user_id=db_user.id, hash=pomodoro_login_hash,
                                          created=now,
                                          modified=now)
            db.add(session_to_add)
            db.commit()

        # Send user to the pomodoro page
        finally:
            response.set_cookie(key="pomodoro_login_hash", value=pomodoro_login_hash,
                                max_age=79200, path='/')
            return RedirectResponse('/users/create')
            # return RedirectResponse('/app/pomodoro')

    else:
        derp = ''
        return RedirectResponse('/users/create')
        # return RedirectResponse('/app/login_failed')
