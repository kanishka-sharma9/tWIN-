from fastapi import APIRouter

from twin.adapters.api import health
from twin.adapters.api.errors import ERROR_RESPONSES

api_router = APIRouter(responses=ERROR_RESPONSES)
api_router.include_router(health.router)
