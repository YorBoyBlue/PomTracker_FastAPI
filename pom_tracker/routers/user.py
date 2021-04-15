from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from ..controllers.user import *
from ..models.user_schema import *

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

router.get("/settings", response_class=HTMLResponse)(render_settings)
router.get("/create", response_class=HTMLResponse)(render_create)
router.get("/login", response_class=HTMLResponse)(render_login)
router.get("/logout")(logout)

router.post("/create")(create)
router.post("/login")(login)
# router.post("/login", response_model=User)(user_login)

# @router.post("/login")
# def user_login(email: str = Form(...), password: str = Form(...)):
#     derp = ''
