from .auth import router as auth_router
from .faculty import router as faculty_router
from .timetable import router as timetable_router
from .rooms import router as rooms_router
from .substitutes import router as substitutes_router
from .analytics import router as analytics_router
from .api import api_router

__all__ = [
    "auth_router",
    "faculty_router",
    "timetable_router",
    "rooms_router",
    "substitutes_router",
    "analytics_router",
    "api_router"
]
