from fastapi import Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from ..dependencies.db import get_db

from ..models.session_model import SessionModel
from ..models.user_model import UserModel


def auth_user(request: Request, db: Session = Depends(get_db)):
    included_paths_user = [
        '/users/logout',
        '/pomodoro/today',
        '/pomodoro/validation'
    ]

    if request.url.path in included_paths_user:
        my_cookie_hash = request.cookies.get('pomodoro_login_hash_2')
        if my_cookie_hash is not None:
            try:
                user_session = db.query(SessionModel, SessionModel.user_id).filter_by(
                    hash=my_cookie_hash).one()

            except NoResultFound as e:
                return False

            else:
                # User session was found, try to query user
                try:
                    user = db.query(UserModel).filter_by(id=user_session.user_id).one()

                except NoResultFound as e:
                    return False

                else:
                    # User was found, pass it through the request context
                    return user
