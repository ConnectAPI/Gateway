from fastapi import APIRouter

from .endpoints.proxy_endpoint import proxy_endpoint


proxy_router = APIRouter()

proxy_router.include_router(proxy_endpoint)
