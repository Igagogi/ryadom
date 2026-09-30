from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.activities import router as activities_router
from app.routers.auth import router as auth_router
from app.routers.recommendations import router as recommendations_router
from app.routers.stories import router as stories_router
from app.routers.users import router as users_router

app = FastAPI()

# The frontend is intentionally kept as a small static application during
# development, so allow only the usual local static-server origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8001",
        "http://localhost:8001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(users_router)
app.include_router(activities_router)
app.include_router(auth_router)
app.include_router(recommendations_router)
app.include_router(stories_router)