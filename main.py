from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import create_db_and_tables
from app.routers import auth, tasks, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Task Manager API with PostgreSQL, SQLModel and JWT authentication",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(admin.router)


@app.get(
    "/",
    tags=["Health"],
    summary="API health check"
)
def root():
    return {
        "message": "Task Manager API is running",
        "docs": "/docs"
    }