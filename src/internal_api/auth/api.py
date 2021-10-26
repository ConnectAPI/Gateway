from fastapi import FastAPI

from .router import token_router
from .core.models.db import get_db


api = FastAPI(title="AuthAPI")

api.include_router(token_router)


@api.on_event("startup")
def startup():
    get_db()  # Create DB connection


@api.on_event("shutdown")
def shutdown():
    get_db().close()
