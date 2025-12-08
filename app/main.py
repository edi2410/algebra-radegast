from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from app.core.db import init_db
from app.routes.v1 import api_router
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.metrics import active_courses, active_users
from sqlmodel import select, func


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Load the database and create tables
    init_db()
    yield
    # Clean up and release the resources


app = FastAPI(
    title="My FastAPI Application",
    description="Comprehensive API Documentation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)
app.include_router(api_router)


@app.on_event("startup")
async def startup_metrics():
    """Initialize gauges on startup"""
    from app.core.db import engine
    from app.models.course import Course
    from app.models.user import User
    from sqlmodel import Session

    with Session(engine) as session:
        # Set initial course count
        course_count = session.exec(select(func.count(Course.id))).one()
        active_courses.set(course_count)

        # Set initial user counts by role
        for role in ['ADMIN', 'TEACHER', 'STUDENT']:
            user_count = session.exec(
                select(func.count(User.id)).where(User.role == role)
            ).one()
            active_users.labels(role=role).set(user_count)