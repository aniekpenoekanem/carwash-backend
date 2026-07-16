from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {
        "message": "Car Wash Backend V2",
        "version": settings.APP_VERSION,
        "status": "online",
    }