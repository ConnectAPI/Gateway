from fastapi import FastAPI

from .router import router

api = FastAPI(title="ServiceDiscovery")
api.include_router(router)
