from fastapi import FastAPI

from .core.models.docker import docker_client
from .router import router

api = FastAPI(title="ServiceDiscovery")
api.include_router(router)


@api.on_event('shutdown')
def shutdown():
    docker_client().stop_all()

