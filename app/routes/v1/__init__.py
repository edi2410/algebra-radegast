from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

@api_router.get("/example")
def example_endpoint():
    return {"message": "API v1 endpoint"}