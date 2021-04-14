from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from ..controllers.users import *
from ..models.user_schema import *

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

router.get("/create", response_class=HTMLResponse)(get_user_create)
router.post("/create", response_model=User)(user_create)

router.get("/login", response_class=HTMLResponse)(get_user_login)

router.post("/login")(user_login)
# router.post("/login", response_model=User)(user_login)

# @router.post("/login")
# def user_login(email: str = Form(...), password: str = Form(...)):
#     derp = ''

router.get("/logout")(user_logout)
