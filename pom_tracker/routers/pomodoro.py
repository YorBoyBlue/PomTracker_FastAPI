from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from ..controllers.pomodoro import *

router = APIRouter(
    prefix="/pomodoro",
    tags=["pomodoro"]
)

router.get("/today", response_class=HTMLResponse)(render_today)
router.get("/collection", response_class=HTMLResponse)(render_collection)
router.get("/export", response_class=HTMLResponse)(render_export)
router.get("/get_collection")(collection)

router.post("/submit")(submit)
router.post("/delete")(delete)
router.post("/export")(export)
