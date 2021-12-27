from fastapi import APIRouter, FastAPI

from .endpoints.proxy import proxy_endpoint
from .endpoints.service import service_router
from .endpoints.auth import auth_router

proxy_router = APIRouter()
proxy_router.include_router(proxy_endpoint)


internal_app = FastAPI()
internal_app.include_router(service_router, prefix="/service_discovery")
internal_app.include_router(auth_router, prefix="/auth")
