from fastapi import FastAPI

from context import initiate, cleanup
from external_api import proxy_router
from external_api.utils import openapi_schema
from internal_api import internal_api


api = FastAPI(title="Gateway")
api.mount("/internal", internal_api)
api.openapi = openapi_schema

api.include_router(proxy_router)


@api.on_event("startup")
async def startup():
    initiate()


@api.on_event("shutdown")
async def shutdown():
    cleanup()
