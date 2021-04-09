from fastapi import Request, Depends
from fastapi.templating import Jinja2Templates
from datetime import datetime
from sqlalchemy.orm import Session

from ..helpers.yaml_helper import YamlHelper
from ..database.db import SessionLocal
from ..models.pomodoro_model import PomodoroModel
from ..models.pom_flags_model import PomFlagsModel


# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_timesheet_template():
    filepath = 'config/pom_sheet_times_template.yaml'
    data = YamlHelper().loader(filepath)
    return data.get('time_blocks')


templates = Jinja2Templates(directory="pom_tracker/views")


def get_today(request: Request, db: Session = Depends(get_db)):
    """Today pom sheet"""

    time_blocks = get_timesheet_template()

    today = datetime.now().date()
    # todays_poms = db.query(PomodoroModel).filter_by(created=today,
    #                              user_id=request.session.user.id).all()

    return templates.TemplateResponse("pomodoro_view.html", {
        "request": request,
        "time_blocks": time_blocks#,
        # "pom_rows": todays_poms
    })
