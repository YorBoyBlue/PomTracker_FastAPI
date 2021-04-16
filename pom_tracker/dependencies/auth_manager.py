from fastapi import Request, Depends

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session

from ..dependencies.database_manager import dbm

from ..models.session_model import SessionModel
from ..models.user_model import UserModel


class AuthManager:
    included_paths_user: list

    def __init__(self):
        self.included_paths_user = [
            '/user/logout',
            '/user/settings',
            '/pomodoro/today',
            '/pomodoro/submit',
            '/pomodoro/delete',
            '/pomodoro/get_collection',
            '/pomodoro/collection',
            '/pomodoro/export'
        ]

    def get_user(self, request: Request, db: Session = Depends(dbm.get_db)):

        if request.url.path in self.included_paths_user:
            my_cookie_hash = request.cookies.get('pomodoro_login_hash_2')

            if my_cookie_hash is None:
                return False

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


auth = AuthManager()
