from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from ..controllers.pomodoro import *

router = APIRouter(
    prefix="/pomodoro",
    tags=["pomodoro"]
)

# HTML GET
router.get("/today", response_class=HTMLResponse)(get_today)
router.get("/display_collection", response_class=HTMLResponse)(display_collection)
router.get("/display_export", response_class=HTMLResponse)(display_export)

# JSON GET
router.get("/get_collection")(get_collection)

# POST
router.post("/submit")(submit)
router.post("/delete")(delete)
router.post("/export")(export)
