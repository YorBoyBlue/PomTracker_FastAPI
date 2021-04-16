from fastapi import Request, Response, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from typing import Optional, List

import pytz
import json
from datetime import datetime

from ..dependencies.auth_manager import auth
from ..dependencies.database_manager import dbm
from ..dependencies.template_mananger import tm
from ..dependencies.timesheet_manager import tsm

from ..models.pomodoro_model import PomodoroModel
from ..models.flag_types_model import FlagTypeModel
from ..models.pom_flags_model import PomFlagsModel
from ..models.user_model import UserModel


def render_today(request: Request, db: Session = Depends(dbm.get_db),
                 user: UserModel = Depends(auth.get_user),
                 templates: Jinja2Templates = Depends(tm.get),
                 time_blocks: list = Depends(tsm.get)):
    """Todays pom sheet"""

    if user is False or user is None:
        return RedirectResponse(url="/user/login_session_expired", status_code=303)

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


def render_collection(request: Request, user: UserModel = Depends(auth.get_user),
                      templates: Jinja2Templates = Depends(tm.get)):
    """Display pomodoro collection"""

    if user is False or user is None:
        return RedirectResponse(url="/user/login_session_expired", status_code=303)

    return templates.TemplateResponse("pomodoro_set_view.html", {"request": request})


def render_export(request: Request, user: UserModel = Depends(auth.get_user),
                  templates: Jinja2Templates = Depends(tm.get)):
    """Display pomodoro collection"""

    if user is False or user is None:
        return RedirectResponse(url="/user/login_session_expired", status_code=303)

    return templates.TemplateResponse("export_poms_view.html", {"request": request})


def submit(response: Response, task: str = Form(...), review: str = Form(...),
           flags: List[str] = Form(...), distractions: Optional[List[int]] = Form(None),
           pom_success: Optional[int] = Form(None), time_blocks: List[str] = Form(...),
           db: Session = Depends(dbm.get_db), user: UserModel = Depends(auth.get_user)):
    """Validate submitted pomodoro"""

    if user is False or user is None:
        return RedirectResponse(url="/user/login_session_expired", status_code=303)

    today = datetime.now().date()
    user_id = user.id

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
            raise HTTPException(status_code=404, detail="Pomodoro already exists")

    # Set proper http status code
    response.status_code = 200
    return response


def delete(poms_to_delete: List[str] = Form(...), db: Session = Depends(dbm.get_db),
           user: UserModel = Depends(auth.get_user)):
    """Delete pomodoros"""

    if user is False or user is None:
        return RedirectResponse(url="/user/login_session_expired", status_code=303)

    db.query(PomodoroModel).filter(
        PomodoroModel.id.in_(poms_to_delete)).delete(
        synchronize_session=False)
    db.query(PomFlagsModel).filter(
        PomFlagsModel.pom_id.in_(poms_to_delete)).delete(
        synchronize_session=False)
    db.commit()

    return RedirectResponse(url="/pomodoro/today", status_code=303)


def collection(offset: Optional[int] = 0, date_filter: Optional[str] = '',
               distractions_filter: Optional[int] = 0, unsuccessful_filter: Optional[int] = 0,
               db: Session = Depends(dbm.get_db), user: UserModel = Depends(auth.get_user)):
    """Get pomodoro collection"""

    if user is False or user is None:
        return RedirectResponse(url="/user/login_session_expired", status_code=303)

    limit = 20

    query = db.query(PomodoroModel).filter_by(user_id=user.id)

    # Apply filters
    if date_filter:
        query = query.filter_by(created=date_filter)
    if distractions_filter:
        query = query.filter(PomodoroModel.distractions > 0)
    if unsuccessful_filter:
        query = query.filter_by(pom_success=0)

    # Get total count
    total_count = query.count()

    # Apply limit and offset
    if limit:
        query = query.limit(limit)
    if offset:
        query = query.offset(offset)

    pom_rows = query.all()

    # Parse flags
    poms = []
    for row in pom_rows:
        flags = []
        for flag in row.flags:
            flags.append(flag.flag_type)
        pom = {
            'task': row.task,
            'review': row.review,
            'created': row.created.strftime('%Y-%m-%d'),
            'distractions': row.distractions,
            'flags': flags,
            'pom_success': row.pom_success,
            'start_time': row.start_time.strftime('%I:%M%p').strip('0'),
            'end_time': row.end_time.strftime('%I:%M%p').strip('0')
        }
        poms.append(pom)

    data = {
        'poms': poms,
        'total_count': total_count
    }

    # Return json data
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data, status_code=200)


def export(start_date: str = Form(...), end_date: str = Form(...),
           db: Session = Depends(dbm.get_db), user: UserModel = Depends(auth.get_user)):
    """Export pomodoros"""

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Query poms within start and end dates
    poms = db.query(
        PomodoroModel).filter(PomodoroModel.created <= end_date).filter(
        PomodoroModel.created >= start_date).filter_by(
        user_id=user.id).order_by(PomodoroModel.created, PomodoroModel.start_time).all()

    data = {'poms': []}
    for row in poms:
        pom = {
            'created': datetime.strftime(row.created, '%Y-%m-%d'),
            'title': row.task,
            'start_time': row.start_time.strftime('%I:%M%p'),
            'end_time': row.end_time.strftime('%I:%M%p'),
            'distractions': row.distractions,
            'pom_success': row.pom_success,
            'review': row.review,
            'flags': []
        }
        for flag in row.flags:
            pom['flags'].append(flag.flag_type)
        data['poms'].append(pom)

    filename = str(start_date) + '-' + str(
        end_date) + '_Arin_Pom_Sheets.json'

    export_data = json.dumps(data, indent=2)

    return Response(content=export_data, status_code=200, media_type='application/octet-stream',
                    headers={"Content-Disposition": "filename=" + filename})
