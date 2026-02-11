from fastapi import APIRouter
from src.api.v1 import auth, execution, generator, health, history, user

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(execution.router, prefix="/execution", tags=["execution"])
api_router.include_router(generator.router, tags=["generator"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
