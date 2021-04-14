from fastapi import Request, Response, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from datetime import datetime
import pytz

from ..helpers.yaml_helper import YamlHelper

from ..dependencies.auth import auth_user
from ..dependencies.db import get_db

from ..models.pomodoro_model import PomodoroModel
from ..models.flag_types_model import FlagTypeModel
from ..models.pom_flags_model import PomFlagsModel
from ..models.user_model import UserModel


def get_timesheet_template():
    filepath = 'pom_tracker/config/pom_sheet_times_template.yaml'
    data = YamlHelper().loader(filepath)
    return data.get('time_blocks')


templates = Jinja2Templates(directory="pom_tracker/views")


def get_today(request: Request, db: Session = Depends(get_db),
              user: UserModel = Depends(auth_user)):
    """Today pom sheet"""

    if user is False or user is None:
        return RedirectResponse(url="/users/login", status_code=303)

    time_blocks = get_timesheet_template()

    today = datetime.now().date()
    todays_poms = db.query(PomodoroModel).filter_by(created=today, user_id=user.id).all()
    flag_types = db.query(FlagTypeModel.flag_type).all()

    return templates.TemplateResponse("pomodoro_view.html", {
        "request": request,
        "time_blocks": time_blocks,
        "flag_types": flag_types,
        "pom_rows": todays_poms,
        "len": len
    })


def validate_pom(response: Response, task: str = Form(...), review: str = Form(...),
                 flags: list = Form(...), distractions: list = Form(...),
                 pom_success: int = Form(...), time_blocks: list = Form(...),
                 db: Session = Depends(get_db), user: UserModel = Depends(auth_user)):
    """Validate submitted pomodoro"""

    if user is False or user is None:
        return RedirectResponse(url="/users/login", status_code=303)

    today = datetime.now().date()
    user_id = user.id

    # Store form data that came in from the user
    form_data = {
        'distractions': distractions,
        'pom_success': pom_success,
        'review': review,
        'task': task,
        'flags': flags,
        'selected_time_blocks': time_blocks
    }

    for time_block in time_blocks:

        times = time_block.split('-')

        start_time = datetime.strptime(times[0].strip(), '%I:%M%p').replace(
            tzinfo=pytz.UTC)
        end_time = datetime.strptime(times[1].strip(), '%I:%M%p').replace(
            tzinfo=pytz.UTC)

        # Create pomodoro model object to submit to DB
        pom_to_add = PomodoroModel(user_id=user_id,
                                   distractions=len(distractions) if distractions else 0,
                                   pom_success=pom_success if pom_success else 0,
                                   task=task,
                                   review=review, created=today,
                                   start_time=start_time.time(),
                                   end_time=end_time.time())
        for flag in flags:
            pom_to_add.flags.append(PomFlagsModel(flag_type=flag))

        # Add pom to the DB
        try:
            db.add(pom_to_add)
            db.commit()
        except IntegrityError as e:
            # Pomodoro already exists with that time block
            db.rollback()
            # Create dict with form data to send back to the browser
            data = {
                'form_data': form_data,
                'message': '<br> * You have already submitted a pomodoro '
                           'with that start time today. Pick another or '
                           'resubmit to replace the current pomodoro with '
                           'the new one.'
            }

            raise HTTPException(status_code=404, detail="Pomodoro already exists")

    return response
