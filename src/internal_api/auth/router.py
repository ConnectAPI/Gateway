from fastapi import APIRouter

from .endpoints.token import token_endpoint


token_router = APIRouter()
token_router.include_router(token_endpoint)
