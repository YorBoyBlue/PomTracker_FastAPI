from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from ..controllers.main import *

router = APIRouter(
    prefix="",
    tags=[""]
)

router.get("/", response_class=HTMLResponse)(render_home)
