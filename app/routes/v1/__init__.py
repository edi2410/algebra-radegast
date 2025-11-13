from fastapi import APIRouter
from app.routes.v1 import auth, course

api_router = APIRouter(prefix="/api/v1")

# Include all v1 routers
api_router.include_router(auth.router)
api_router.include_router(course.router)
