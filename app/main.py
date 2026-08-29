from fastapi import FastAPI

from app.routers.recommendations import router

app = FastAPI()
app.include_router(router)
