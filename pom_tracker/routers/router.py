from fastapi import APIRouter
from ..routers import main
from ..routers import user
from ..routers import pomodoro

routers = APIRouter()

# Include all routers here to a single router instance
routers.include_router(main.router)
routers.include_router(user.router)
routers.include_router(pomodoro.router)
