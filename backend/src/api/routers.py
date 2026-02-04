from fastapi import APIRouter
from src.api.v1 import auth, generator, health

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(generator.router, tags=["generator"])
api_router.include_router(health.router, tags=["health"])
