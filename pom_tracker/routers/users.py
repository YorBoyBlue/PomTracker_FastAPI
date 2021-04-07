from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

templates = Jinja2Templates(directory="views")


@router.get("/login", response_class=HTMLResponse)
def user_login(request: Request):
    """User login endpoint"""

    return templates.TemplateResponse("user_login_view.html", {"request": request})
