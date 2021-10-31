from fastapi import FastAPI

from context import get_services
from .router import router

api = FastAPI(title="ServiceDiscovery")
api.include_router(router)


@api.on_event('shutdown')
def shutdown():
    get_services().shutdown()

