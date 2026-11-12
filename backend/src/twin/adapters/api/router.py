from fastapi import APIRouter

from twin.adapters.api import health

api_router = APIRouter()
api_router.include_router(health.router)
