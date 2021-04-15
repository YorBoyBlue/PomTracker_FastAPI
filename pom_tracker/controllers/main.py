from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="pom_tracker/views")


def render_home(request: Request):
    """Home endpoint"""

    return templates.TemplateResponse("home_view.html", {"request": request})
