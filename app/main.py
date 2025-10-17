from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from app.core.db import init_db
from app.routes.v1 import api_router, auth


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
    openapi_url="/api/openapi.json"
)

app.include_router(api_router)

router = APIRouter()

app.include_router(auth.router)
