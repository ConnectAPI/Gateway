from fastapi import APIRouter

from .endpoints.service import service_endpoint


router = APIRouter()
router.include_router(service_endpoint)
