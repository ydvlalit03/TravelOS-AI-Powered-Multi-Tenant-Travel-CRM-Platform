"""Version 1 API router aggregation."""
from fastapi import APIRouter

from app.api.v1 import auth

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
