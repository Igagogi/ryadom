from fastapi import FastAPI

from app.routers.activities import router as activities_router
from app.routers.auth import router as auth_router
from app.routers.recommendations import router as recommendations_router
from app.routers.stories import router as stories_router
from app.routers.users import router as users_router

app = FastAPI()

app.include_router(users_router)
app.include_router(activities_router)
app.include_router(auth_router)
app.include_router(recommendations_router)
app.include_router(stories_router)