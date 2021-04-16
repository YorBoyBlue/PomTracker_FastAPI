from fastapi import Request, Response, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from typing import Optional
from datetime import datetime
import random
import string
import hashlib

from ..error_handling.my_exceptions import NoSessionRecordExists

from ..dependencies.auth_manager import auth
from ..dependencies.database_manager import dbm
from ..dependencies.template_mananger import tm

from ..models.user_model import UserModel
from ..models.session_model import SessionModel


def render_settings(request: Request, user: UserModel = Depends(auth.get_user),
                    templates: Jinja2Templates = Depends(tm.get)):
    """Home endpoint"""

    if user is False or user is None:
        return RedirectResponse(url="/user/login_session_expired", status_code=303)

    return templates.TemplateResponse("settings_view.html", {"request": request})


def render_create(request: Request, templates: Jinja2Templates = Depends(tm.get)):
    """User create endpoint"""

    return templates.TemplateResponse("user_create_view.html", {"request": request})


def render_create_invalid(request: Request, templates: Jinja2Templates = Depends(tm.get)):
    """User create endpoint"""

    return templates.TemplateResponse("user_create_view.html", {
        "request": request,
        "email_exists": True
    })


def render_login(request: Request, templates: Jinja2Templates = Depends(tm.get)):
    """User login endpoint"""

    return templates.TemplateResponse("user_login_view.html", {"request": request})


def render_login_session_expired(request: Request, templates: Jinja2Templates = Depends(tm.get)):
    """User login endpoint"""

    return templates.TemplateResponse("user_login_view.html", {
        "request": request,
        "session_expired": True
    })


def render_login_invalid(request: Request, templates: Jinja2Templates = Depends(tm.get)):
    """User login endpoint"""

    return templates.TemplateResponse("user_login_view.html", {
        "request": request,
        "invalid_login": True
    })


def create(email: str = Form(...), password: str = Form(...), first_name: str = Form(...),
           last_name: str = Form(...), middle_name: Optional[str] = Form(''),
           display_name: Optional[str] = Form(''), db: Session = Depends(dbm.get_db)):
    """Create new user"""

    today = datetime.utcnow()
    user_to_add = UserModel(email=email,
                            first_name=first_name,
                            middle_name=middle_name,
                            last_name=last_name,
                            display_name=display_name,
                            password=password,
                            created=today,
                            modified=today)
    try:
        db.add(user_to_add)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        return RedirectResponse('/user/create_invalid', status_code=303)

    else:
        # Send user to the login page if their account was created
        return RedirectResponse('/user/login', status_code=303)


def login(response: Response, email: str = Form(...), password: str = Form(...),
          db: Session = Depends(dbm.get_db)):
    """Login user"""

    # Validate user
    try:
        db_user = db.query(UserModel).filter(UserModel.email == email).first()

    # User was not found, send back to login failed end point
    except NoResultFound as e:
        return RedirectResponse(url="/user/login_invalid", status_code=303)

    # User email is validated. Validate password as well
    else:
        if password == db_user.password:
            rand_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
            hash_object = hashlib.md5(rand_string.encode())
            pomodoro_login_hash = hash_object.hexdigest()
            now = datetime.utcnow()

            # Check if user has an existing session in DB and modify it
            try:
                records_updated_count = db.query(SessionModel).filter_by(
                    user_id=db_user.id).update({"hash": pomodoro_login_hash, "modified": now})

                if records_updated_count == 0:
                    raise NoSessionRecordExists('No session for this user was found')

                db.commit()

            # Create a new session in DB if one does not exist
            except NoSessionRecordExists as e:
                session_to_add = SessionModel(user_id=db_user.id,
                                              hash=pomodoro_login_hash,
                                              created=now,
                                              modified=now)
                db.add(session_to_add)
                db.commit()

            # Send user to the pomodoro page
            finally:
                response.set_cookie(key="pomodoro_login_hash_2",
                                    value=pomodoro_login_hash,
                                    max_age=79200)

                response_headers = response.headers.items()
                headers = {}

                for header in response_headers:
                    headers[header[0]] = header[1]

                return RedirectResponse(url="/pomodoro/today", status_code=303, headers=headers)

        else:
            return RedirectResponse(url="/user/login_invalid", status_code=303)


def logout(response: Response, request: Request, db: Session = Depends(dbm.get_db),
           user: UserModel = Depends(auth.get_user)):
    """Logout user"""

    if user is False or user is None:
        return RedirectResponse(url="/user/login", status_code=303)

    headers = {}
    cookies = request.cookies

    if 'pomodoro_login_hash_2' in cookies:
        response.delete_cookie('pomodoro_login_hash_2')

        db.query(SessionModel).filter_by(user_id=user.id).delete(
            synchronize_session=False)
        db.commit()

        response_headers = response.headers.items()

        for header in response_headers:
            headers[header[0]] = header[1]

    return RedirectResponse(url="/user/login", status_code=303, headers=headers)
