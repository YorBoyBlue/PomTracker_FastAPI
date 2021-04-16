from fastapi import Request, Depends
from fastapi.templating import Jinja2Templates

from ..dependencies.template_mananger import tm


def render_home(request: Request, templates: Jinja2Templates = Depends(tm.get)):
    """Home endpoint"""

    return templates.TemplateResponse("home_view.html", {"request": request})
