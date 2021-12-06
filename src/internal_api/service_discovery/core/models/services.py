from typing import Dict, Optional
from functools import lru_cache

from .db import get_db
from .docker import docker_client, DockerException
from ..settings import get_settings
from models.service import Service

__all__ = ["get_services", "Services"]


class Services:
    def __init__(self):
        self.db = get_db()
        self.__services: Dict[str, Service] = {}
        self.__services_by_id: Dict[str, Service] = {}
        self._load_services()

    def _load_services(self):
        services = [
            Service.from_dict(service_dict)
            for service_dict in self.db.services.find({}, {"_id": 0})
        ]
        for service in services:
            self.add(
                service.id,
                service.name,
                service.url,
                service.openapi_dict,
                service.image_name,
                service.environment_vars
            )

    def _activate(self, service: Service):
        container = docker_client().run_container(service.image_name, service.environment_vars, service.name)

    def _stop(self, service: Service):
        docker_client().stop_container(service.name)

    def remove(self, service_id):
        service = self.__services_by_id.pop(service_id, None)
        if service is None:
            return
        self._stop(service)
        self.__services.pop(service.prefix_path)

    def add(
            self,
            id: str,
            name: str,
            url: str,
            openapi_dict: dict,
            image_name: str,
            environment_vars: dict,
    ):
        service = Service(id, name, url, openapi_dict, image_name, environment_vars)
        try:
            self._activate(service)
        except DockerException as DE:
            if not get_settings().debug:
                raise
            print("Warning: docker error", DE)
            return
        self.__services[service.prefix_path] = service
        self.__services_by_id[service.id] = service

    def get_by_prefix_path(self, prefix_path) -> Optional[Service]:
        return self.__services.get(prefix_path)

    def pause(self, id: str):
        service = self.__services_by_id[id]
        docker_client().pause(service.name)

    def unpause(self, id: str):
        service = self.__services_by_id[id]
        docker_client().unpause(service.name)

    def shutdown(self):
        docker_client().stop_all()

    def __iter__(self):
        return iter(self.__services.values())


@lru_cache
def get_services() -> Services:
    return Services()