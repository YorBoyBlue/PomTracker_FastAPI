from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from ..controllers.pomodoro import *

router = APIRouter(
    prefix="/pomodoro",
    tags=["pomodoro"]
)

router.get("/today", response_class=HTMLResponse)(get_today)
